from collections import defaultdict
from typing import Dict, List, Union

from pygfdrivers.common.visa.visa_scope import VisaScope
from pygfdrivers.common.visa.visa_cmd import BaseVisaScopeCommand
from pygfdrivers.common.models.device.cmd import create_cmd_class, CmdClassType
from pygfdrivers.common.util.utilities import has_prop, has_setter, convert_value

from pygfdrivers.keysight.models.channel import KeysightChannelModel, KeysightChannelDataModel


def init_ch_cmds() -> CmdClassType:
    ch: CmdClassType = create_cmd_class('Channel')
    ch.add_cmd(key='ch_scale', cmd=':scale', default=1.0)
    ch.add_cmd(key='ch_offset', cmd=':offset', default=0)
    ch.add_cmd(key='ch_display', cmd=':display', args=[1, 0, 'on', 'off'])
    ch.add_cmd(key='ch_coupling', cmd=':coupling', args=['ac', 'dc'], default='ac')
    ch.add_cmd(key='ch_range', cmd=':range', args={'max': 40.0, 'min': 8e-3}, default=8.0)
    ch.add_cmd(key='ch_gain', cmd=':probe', args={'max': 10_000.0, 'min': 0.1}, default=1.0)
    return ch


class KeysightChannel(BaseVisaScopeCommand):
    def __init__(self, scope: VisaScope) -> None:
        super().__init__(scope)

        self.ch_cmds = init_ch_cmds()
        self.ch_fields = [field for field in self.source_fields if field.startswith('ch')]

        self.max_chs = 8 if self.is_mxr else 4
        if self.is_mxr:
            self.ch_cmds.add_cmd(
                key='ch_gain',
                cmd=':probe:external:gain',
                default=1.0
            )
            self.ch_cmds.add_cmd(
                key='ch_coupling',
                cmd=':input',
                args=['dc', 'ac', 'dc50', 'dcfifty'],
                default='dc'
            )

        _min = 0.1 if self.scope_series in {'DSOX2000', 'DSOX3000'} else 0.001
        self.ch_cmds.update_cmd_args('ch_gain', {'max': 10_000, 'min': _min})

    def apply_ch_config(self, active_chs: List[int], ch_config: Dict[int, KeysightChannelModel]) -> None:
        try:
            for ch in range(1, self.max_chs + 1):
                self.set_ch('ch_display', True if ch in active_chs else False, ch)

            for ch in active_chs:
                self.ch_num = ch
                config = ch_config[ch]
                for field, setting in config.dict().items():
                    if has_setter(self, field) and setting is not None:
                        self.set_ch(field, setting, ch)

        except Exception as e:
            self.log.error(f"Applying channel configuration encountered error: {e}.")

    def fetch_ch_config(self, active_chs: List[int], ch_info: Dict[str, KeysightChannelDataModel]) -> None:
        try:
            for ch in active_chs:
                self.ch_num = ch
                info = ch_info[str(ch)]
                for field in self.ch_fields:
                    if has_prop(self, field):
                        setattr(info, field, getattr(self, field))

        except Exception as e:
            self.log.error(f"Fetching channel configuration encountered error: {e}.")

    def set_ch(self, setter: str, setting: Union[int, float, str, bool], ch: int) -> None:
        try:
            self.ch_num = ch
            setattr(self, setter, setting)
        except Exception as e:
            self.log.error(f"Setting channel '{ch}' '{setter}' to '{setting}' encountered error: {e}.")

    def get_ch(self, getter: str, ch: int) -> None:
        try:
            self.ch_num = ch
            return getattr(self, getter)
        except Exception as e:
            self.log.error(f"Fetching channel '{ch}' '{getter}' encountered error: {e}.")

    # ------------------------------------------------------------------------------------
    #  Core Channel Methods - common amongst all Keysight scopes and unlikely to be modified
    # ------------------------------------------------------------------------------------

    @property
    def ch_coupling(self) -> str:
        _ch_coupling = self.query(self.ch_cmds, 'ch_coupling', channel=self.ch_num)
        return _ch_coupling.lower()

    @ch_coupling.setter
    def ch_coupling(self, coupling: str) -> None:
        self.set_and_verify_config(self.ch_cmds, 'ch_coupling', coupling.lower(), channel=self.ch_num)

    @property
    def ch_display(self) -> bool:
        _ch_display = self.query(self.ch_cmds, 'ch_display', channel=self.ch_num)
        return bool(int(_ch_display))

    @ch_display.setter
    def ch_display(self, state: bool) -> None:
        self.set_and_verify_config(self.ch_cmds, 'ch_display', int(state), channel=self.ch_num)

    @property
    def ch_offset(self) -> float:
        _ch_offset = self.query(self.ch_cmds, 'ch_offset', channel=self.ch_num)
        return float(_ch_offset)

    @ch_offset.setter
    def ch_offset(self, y_offset: float):
        self.set_and_verify_config(self.ch_cmds, 'ch_offset', y_offset, channel=self.ch_num)

    @property
    def ch_gain(self) -> float:
        _ch_gain = self.query(self.ch_cmds, 'ch_gain', channel=self.ch_num)
        _ch_gain = _ch_gain.split(',')[0] if self.is_mxr else _ch_gain
        return float(_ch_gain)

    @ch_gain.setter
    def ch_gain(self, probe: float) -> None:
        if self.is_mxr:
            self.scope.write_scope(self.ch_cmds, 'ch_gain', setting=f"{probe},RATio", channel=self.ch_num)
            self.scope.verify_config(self.ch_cmds, 'ch_gain', setting=probe, channel=self.ch_num)
        else:
            self.set_and_verify_config(self.ch_cmds, 'ch_gain', probe, channel=self.ch_num)

    @property
    def ch_range(self) -> float:
        _ch_range = self.query(self.ch_cmds, 'ch_range', channel=self.ch_num)
        return float(_ch_range)

    @ch_range.setter
    def ch_range(self, y_range: float) -> None:
        self.set_and_verify_config(self.ch_cmds, 'ch_range', y_range, channel=self.ch_num)

    # ------------------------------------------------------------------------------------
    #  Non-Core Acquire Methods - not universal amongst all Keysight scopes
    # ------------------------------------------------------------------------------------

    # --------------DSOX1200, DSOX2000, DSOX3000, DSOX4000, DSO5000-----------------------

    @property
    def ch_scale(self) -> float:
        _ch_scale = self.query(self.ch_cmds, 'ch_scale', channel=self.ch_num)
        return float(_ch_scale)

    @ch_scale.setter
    def ch_scale(self, y_scale: float) -> None:
        self.set_and_verify_config(self.ch_cmds, 'ch_scale', y_scale, channel=self.ch_num)

    @property
    def ch_settings(self) -> Dict:
        setting_keys = [
            'range', 'offset', 'coupling', 'impedance', 'active',
            'bwlim', 'invert', 'unit', 'gain', 'probe_skew', 'input_type'
        ]
        _ch_settings = defaultdict(dict)

        for ch in range(1, self.max_chs + 1):
            query = self.query(cmd=':channel', channel=ch).split(';')
            for setting, value in zip(setting_keys, query):
                _ch_settings[ch][setting] = convert_value(value.split()[1])

        return _ch_settings
