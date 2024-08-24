from collections import defaultdict
from typing import List, Union, Dict

from pygfdrivers.common.visa.visa_scope import VisaScope
from pygfdrivers.common.visa.visa_cmd import BaseVisaScopeCommand
from pygfdrivers.common.models.device.cmd import create_cmd_class, CmdClassType
from pygfdrivers.common.util.utilities import has_prop, has_setter, convert_value

from pygfdrivers.keysight.models.channel import KeysightChannelModel, KeysightChannelDataModel


def create_waveform_cmd_class() -> CmdClassType:
    wave: CmdClassType = create_cmd_class('Waveform')
    wave.add_cmd(key='wave_data', cmd=':waveform:data')
    wave.add_cmd(key='wave_points', cmd=':waveform:points')
    wave.add_cmd(key='wave_xinc', cmd=':waveform:xincrement')
    wave.add_cmd(key='wave_xorigin', cmd=':waveform:xorigin')
    wave.add_cmd(key='wave_xref', cmd=':waveform:xreference')
    wave.add_cmd(key='wave_yinc', cmd=':waveform:yincrement')
    wave.add_cmd(key='wave_yorigin', cmd=':waveform:yorigin')
    wave.add_cmd(key='wave_yref', cmd=':waveform:yreference')
    wave.add_cmd(key='wave_preamble', cmd=':waveform:preamble')
    wave.add_cmd(key='wave_segment_ttag', cmd=':waveform:segmented:ttag')
    wave.add_cmd(key='wave_segment_count', cmd=':waveform:segmented:count')
    wave.add_cmd(key='wave_unsigned', cmd=':waveform:unsigned', args=[1, 0, 'on', 'off'], default=1)
    wave.add_cmd(key='wave_format', cmd=':waveform:format', args=['word', 'byte', 'ascii'], default='byte')
    wave.add_cmd(key='wave_points_mode', cmd=':waveform:points:mode', args=['normal', 'max', 'raw'], default='raw')
    wave.add_cmd(key='wave_byte_order', cmd=':waveform:byteorder', args=['lsbfirst', 'msbfirst'], default='msbfirst')
    wave.add_cmd(
        key='wave_source',
        cmd=':waveform:source',
        args=['channel1', 'channel2', 'channel3', 'channel4', 'function', 'math', 'fft', 'wmemory1', 'wmemory2'],
        default='channel1'
    )
    return wave


class KeysightWaveform(BaseVisaScopeCommand):
    def __init__(self, scope: VisaScope) -> None:
        super().__init__(scope)
        
        self.visa_scope = self.scope.scope

        self.wave_cmds = create_waveform_cmd_class()
        self.wave_fields = [field for field in self.source_fields if field.startswith('wave')]

        if self.is_mxr:
            self.wave_cmds.add_cmd(
                key='wave_stream',
                cmd=':waveform:streaming',
                args=[1, 0, 'on', 'off'],
                default=0
            )
            self.wave_cmds.add_cmd(
                key='wave_format',
                cmd=':waveform:format',
                args=['ascii', 'byte', 'word', 'binary', 'float'],
                default='word'
            )
            self.wave_cmds.add_cmd(
                key='wave_segmented_all',
                cmd=':waveform:segmented:all',
                args=[1, 0, 'on', 'off'],
                default=1
            )
            self.wave_cmds.update_cmd_args(
                key='wave_source',
                args=[
                    'channel1', 'channel2', 'channel3', 'channel4', 'channel5', 'channel6', 'channel7', 'channel8',
                    'function', 'math', 'fft', 'wmemory1', 'wmemory2'
                ]
            )

        self.mxr_fields = {'wave_stream', 'wave_segmented_all'}
        self.ignore_fields = {'wave_points', 'wave_segment_ttag'}

    def apply_wave_config(self, active_chs: List[int], wave_config: Dict[int, KeysightChannelModel]) -> None:
        try:
            for ch in active_chs:
                self.wave_source = ch
                config = wave_config[ch]
                for field, setting in config.dict().items():
                    if has_setter(self, field) and setting is not None:
                        if field in self.mxr_fields and not self.is_mxr:
                            continue

                        setattr(self, field, setting)
        except Exception as e:
            self.log.error(f"Applying waveform configurations encountered error: {e}.")

    def fetch_wave_config(self, active_chs: List[int], wave_info: Dict[str, KeysightChannelDataModel]) -> None:
        try:
            for ch in active_chs:
                self.wave_source = ch
                info = wave_info[str(ch)]
                for field in self.wave_fields:
                    if has_prop(self, field) and field not in self.ignore_fields:
                        if field in self.mxr_fields and not self.is_mxr:
                            continue

                        setattr(info, field, getattr(self, field))
        except Exception as e:
            self.log.error(f"Fetching waveform configurations encountered error: {e}.")

    def set_wave_source(self, setter: str, setting: Union[int, float, bool, str], source: Union[int, str]) -> None:
        try:
            self.wave_source = source
            setattr(self, setter, setting)
        except Exception as e:
            self.log.error(f"Setting wave {source = } '{setter}' to '{setting}' encountered error: {e}.")

    def get_wave_source(self, getter: str, source: Union[int, str]) -> Union[int, float, str, bool]:
        try:
            self.wave_source = source
            return getattr(self, getter)
        except Exception as e:
            self.log.error(f"Fetching wave {source = } '{getter}' encountered error: {e}.")

    # ------------------------------------------------------------------------------------
    #  Core Wave Methods - common amongst all Keysight scopes and unlikely to be modified
    # ------------------------------------------------------------------------------------

    @property
    def wave_byte_order(self) -> str:
        _wave_byte_order = self.query(self.wave_cmds, 'wave_byte_order')
        return _wave_byte_order.lower()

    @wave_byte_order.setter
    def wave_byte_order(self, byte_order: str) -> None:
        self.set_and_verify_config(self.wave_cmds, 'wave_byte_order', byte_order.lower())

    @property
    def wave_data(self) -> bytes:
        if not self.is_mxr:
            _wave_data = self.visa_scope.query_binary_values('waveform:data?', datatype='B', container=bytes)
        else:
            self.visa_scope.timeout = 60000  # 600,000 ms = 10 minutes timeout
            self.write(cmd=':waveform:streaming 1')
            _wave_data = self.visa_scope.query_binary_values(
                ':waveform:data?',
                datatype='s',
                container=bytes
            )
        self.visa_scope.timeout = 2000  # Back to default 2000 ms = 2 seconds
        return _wave_data

    @property
    def wave_format(self) -> str:
        _wave_format = self.query(self.wave_cmds, 'wave_format')
        return _wave_format.lower()

    @wave_format.setter
    def wave_format(self, data_format: str) -> None:
        data_format = 'word' if self.is_mxr and data_format == 'byte' else data_format
        self.set_and_verify_config(self.wave_cmds, 'wave_format', data_format.lower())

    @property
    def wave_points(self) -> int:
        _wave_points = self.query(self.wave_cmds, 'wave_points')
        return int(_wave_points)

    @wave_points.setter
    def wave_points(self, points: int) -> None:
        self.set_and_verify_config(self.wave_cmds, 'wave_points', points)

    @property
    def wave_preamble(self) -> Dict:
        cmd_key = 'wave_preamble'
        _wave_preamble = defaultdict(dict)

        # TODO: Figure out why errors are showing up in the params class
        # unit_keys = WAVE.PREAMBLE.KEYS[self.keysight_model]['UNIT']
        # type_keys = WAVE.PREAMBLE.KEYS[self.keysight_model]['TYPE']
        # preamble_keys = WAVE.PREAMBLE.KEYS[self.keysight_model]['MAIN']
        # format_keys = WAVE.PREAMBLE.KEYS[self.keysight_model]['FORMAT']
        # coupling_keys = WAVE.PREAMBLE.KEYS[self.keysight_model]['COUPLING']
        # acq_mode_keys = WAVE.PREAMBLE.KEYS[self.keysight_model]['ACQ_MODE']

        # Define the common preamble keys and values
        preamble_keys = [
            'format', 'type', 'points', 'count', 'x_inc', 'x_origin', 'x_ref', 'y_inc', 'y_origin', 'y_ref'
        ]
        format_keys = ['byte', 'word', '', '', 'ascii']
        type_keys = ['normal', 'peak', 'average']
        coupling_keys = None
        acq_mode_keys = None
        unit_keys = None

        # If the model is MXR, extend the preamble keys and values
        if self.is_mxr:
            preamble_keys.extend([
                'coupling', 'x_display_range', 'x_display_origin', 'y_display_range', 'y_display_origin', 'date',
                'time', 'frame_model_num', 'acq_mode', 'completion', 'x_units', 'y_units', 'max_bwlim', 'min_bwlim',
                'segment_count'
            ])
            format_keys = ['ascii', 'byte', 'word', 'long', 'longlong', 'float']
            type_keys = ['raw', 'average', 'vhistogram', 'hhistogram', '', 'interpolate', '', '', 'digital', 'pdetect']
            coupling_keys = ['ac', 'dc', 'dcfifty', 'lfreject']
            acq_mode_keys = ['rtime or hresolution', 'etime', 'segmented or seghresolution', 'pdetect or segpdetect']
            unit_keys = ['unknown', 'volt', 'second', 'constant', 'amp', 'decibel']

        # Query and parse the preamble
        query = self.query(self.wave_cmds, cmd_key).split(',')
        for preamble, value in zip(preamble_keys, query):
            value = convert_value(value)
            if preamble == 'format':
                value = format_keys[value]
            elif preamble == 'type':
                value = type_keys[value]

            if self.is_mxr:
                if preamble == 'coupling':
                    value = coupling_keys[value]
                elif preamble in ['x_units', 'y_units']:
                    value = unit_keys[value]
                elif preamble == 'acq_mode':
                    value = acq_mode_keys[value]

            _wave_preamble[self.wave_source][preamble] = value

        return _wave_preamble

    @property
    def wave_source(self) -> str:
        _wave_source = self.query(self.wave_cmds, 'wave_source')
        return _wave_source.lower()

    @wave_source.setter
    def wave_source(self, source: Union[int, str]) -> None:
        source = convert_value(source)
        source = f"channel{source}" if isinstance(source, int) else source.lower()
        self.set_and_verify_config(self.wave_cmds, 'wave_source', source)

    @property
    def wave_unsigned(self) -> bool:
        if not self.is_mxr:
            _wave_unsigned = self.query(self.wave_cmds, 'wave_unsigned')
            return bool(int(_wave_unsigned))

    @wave_unsigned.setter
    def wave_unsigned(self, state: bool) -> None:
        if not self.is_mxr:
            self.set_and_verify_config(self.wave_cmds, 'wave_unsigned', int(state))

    @property
    def wave_xinc(self) -> float:
        _wave_xinc = self.query(self.wave_cmds, 'wave_xinc')
        return float(_wave_xinc)

    @property
    def wave_xorigin(self) -> float:
        _wave_xorigin = self.query(self.wave_cmds, 'wave_xorigin')
        return float(_wave_xorigin)

    @property
    def wave_xref(self) -> float:
        _wave_xref = self.query(self.wave_cmds, 'wave_xref')
        return float(_wave_xref)

    @property
    def wave_yinc(self) -> float:
        _wave_yinc = self.query(self.wave_cmds, 'wave_yinc')
        return float(_wave_yinc)

    @property
    def wave_yorigin(self) -> float:
        _wave_yorigin = self.query(self.wave_cmds, 'wave_yorigin')
        return float(_wave_yorigin)

    @property
    def wave_yref(self) -> float:
        _wave_yref = self.query(self.wave_cmds, 'wave_yref')
        return float(_wave_yref)

    # ------------------------------------------------------------------------------------
    #  Non-Core Waveform Methods - not universal amongst all Keysight scopes
    # ------------------------------------------------------------------------------------

    # --------------DSOX1200, DSOX2000, DSOX3000, DSOX4000, DSO5000-----------------------

    @property
    def wave_points_mode(self) -> str:
        if not self.is_mxr:
            _wave_points_mode = self.query(self.wave_cmds, 'wave_points_mode')
            return _wave_points_mode.lower()

    @wave_points_mode.setter
    def wave_points_mode(self, points_mode: str) -> None:
        if not self.is_mxr:
            self.set_and_verify_config(self.wave_cmds, 'wave_points_mode', points_mode.lower())

    @property
    def wave_segment_count(self) -> int:
        _wave_segment_count = self.query(self.wave_cmds, 'wave_segment_count')
        return int(_wave_segment_count)

    @property
    def wave_segment_ttag(self) -> float:
        _wave_segment_ttag = self.query(self.wave_cmds, 'wave_segment_ttag')
        return float(_wave_segment_ttag)

    # ------------------------------------MXR---------------------------------------------

    @property
    def wave_stream(self) -> bool:
        _wave_stream = self.query(self.wave_cmds, 'wave_stream')
        return bool(int(_wave_stream))

    @wave_stream.setter
    def wave_stream(self, state: bool) -> None:
        self.set_and_verify_config(self.wave_cmds, 'wave_stream', int(state))

    @property
    def wave_segmented_all(self) -> bool:
        _wave_segmented_all = self.query(self.wave_cmds, 'wave_segmented_all')
        return bool(int(_wave_segmented_all))

    @wave_segmented_all.setter
    def wave_segmented_all(self, state: bool) -> None:
        self.set_and_verify_config(self.wave_cmds, 'wave_segmented_all', int(state))
