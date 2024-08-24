
"""
Class to control scopes in the Teledyne Lecroy T3DSO2000A series
Communicates to the scope using messages in the VISA protocol, developed in python 3.10.9.
Public Functions:
    - __init__: start communication with scope
    - configure_settings : configure the scope for a measurement by sending settings.
    - get_settings : read the current settings from the scope.
    - run : start a measurement
    - stop : put scope into stop mode
    - query_trigger : get the trigger state of the scope. Use this function to know
        when the scope is triggered and ready to send data. Don't poll this function
        too fast (< 1 ms) or the script may crash.
    - collect_single : get the data for a single measurement
    - collect_sequence : get the data for a sequence of measurements
    - get_timebase_info : query the scope for information on time axis
    - construct_time_axis : create a time axis given # of points, time scale, etc.
    - close : use after completion to release resources
    - query/write : send command directly to the scope. Shouldn't be necessary
        unless low level manipulations are needed

An example program can be found in the scopeUtils.py script. That file also contains
auxilary functions to graph/save data.

Author: Armaan Randhawa, Nov 2023
"""

import numpy as np
from pyvisa import errors
from time import perf_counter, sleep
from typing import Dict, Union, Tuple

from pygfdrivers.gf.reflectometer.drivers.common.visa_device import VisaDevice
from pygfdrivers.gf.reflectometer.drivers.lecroy_preamble import WaveformPreamble
from pygfdrivers.gf.reflectometer.util.data_process import DataOperations


DEFAULT_DATA_WINDOW = {
    'start_time': 0,        # t = 0 is left side of screen
    'end_time': 'MAX'     # 'MAX' indicates right side of screen
}
NCHAN = 4


class LecroyScope(VisaDevice):
    def __init__(self, ip_address: str, settings: Dict, log) -> None:
        super().__init__(ip_address, settings)

        self.scope = self.device
        self.log = log
        self.data_channels = settings['data_channels'] or self.settings['data_channels']

    def init(self) -> None:
        pass

    def apply_configurations(self, settings: Dict) -> None:
        """
        Configure settings on the scope. For supported settings, this function will search the Dict and send
        messages to the scope using scope.write(). This code attempts to contain as many useful settings
        as possible, though there may be some that are missed. See programming manual and notes for extra settings.

        Args:
            settings (Dict): contains all the settings for the scope
        """
        self.log.debug("Applying scope settings...")
        settings = settings or self.settings

        # Set scope to STOP mode as some settings cannot be changed in other modes
        self.write(":TRIGger:MODE normal")
        self.transient_mode = 'run'

        self.log.debug("Applying scope acquire settings...")
        self.write(":ACQuire:MODE YT")
        self.write(":ACQuire:AMODe FAST")
        self.write(":ACQuire:INTerpolation ON")
        self.write(f":ACQuire:TYPE {settings['acquire_type']}")
        self.write(f":ACQuire:RESolution {settings['bit_res']}Bits")

        # Apply trigger settings
        self.log.debug("Applying scope trigger settings...")
        self.write(":TRIGger:TYPE EDGE")
        self.write(f":TRIGger:EDGE:SLOPe {settings['trigger_slope']}")
        self.write(f":TRIGger:EDGE:LEVel {settings['trigger_voltage']}")
        self.write(f":TRIGger:EDGE:SOURce {settings.get('trigger_source')}")

        holdoff_mode = settings.get('holdoff_mode').lower()
        if holdoff_mode is not None and 'time' in holdoff_mode:
            self.write(f":TRIGger:EDGE:HLDTime {settings['holdoff_time']}")
        elif 'even' in holdoff_mode:
            self.write(f":TRIGger:EDGE:HLDEVent {settings['holdoff_events']}")
        else:
            self.write(f":TRIGger:EDGE:HOLDoff OFF")

        # Apply window settings
        self.log.debug("Applying scope timebase settings...")
        self.write(f":TIMEbase:SCALe {settings['time_scale']}")
        self.write(f":TIMebase:DELay {settings['time_delay']}")

        # Apply channel settings
        for i in range(4):
            ch_num = i + 1
            self.log.debug(f"Applying scope channel {ch_num} settings...")
            ch_enabled = 'on' if ch_num in settings['data_channels'] else 'off'
            self.write(f":CHANnel{ch_num}:SWITch {ch_enabled}")
            self.write(f":CHANnel:VISible {ch_enabled}")

            if ch_enabled == 'on':
                ch_settings = settings['channels'][ch_num]
                cmd_list = [
                    "UNIT V",
                    "INVert OFF",
                    "PROBe VALue,1",
                    f"SCALe {ch_settings['scale']}",
                    f"OFFSet {ch_settings['offset']}",
                    f"COUPling {ch_settings['coupling']}",
                    f"IMPedance {ch_settings['impedance']}",
                    f"BWLimit {ch_settings['bandwidth_limit']}"
                ]

                for cmd in cmd_list:
                    self.write(f":CHANnel{ch_num}:{cmd}")

        # Sets memory depth based on whether the scope is in single or dual channel mode
        # NOTE: Configured after the channels have been set as it depends on how many channels are active
        mem_depth = settings.get('memory_depth')
        mem_depth = mem_depth.replace('1', '2', 1) if self.ch_mode == 'single' else mem_depth.replace('2', '1', 1)
        bit_res = self.acq_res

        # NOTE: ADC bit resolution also reduces the max memory depth setting by half when set to 10-bit mode
        if bit_res == 10 and mem_depth in ['200M', '100M']:
            mem_depth = mem_depth.replace('2', '1') if mem_depth == '200M' else mem_depth.replace('10', '5', 1)
        self.write(f":ACQuire:MDEPth {mem_depth}")

        # Start a timeout to ensure ensure that apply configurations does not exceed max allowable time.
        start_time = perf_counter()
        self.log.debug("Awaiting 'operation complete' response from scope...")
        while not self.query("*OPC?"):
            if (perf_counter() - start_time) < 10_000:
                sleep(0.01)
            else:
                raise TimeoutError("Applying configurations timed out after 10 seconds.")
        self.log.debug("Finished applying scope settings.")

    def arm(self) -> None:
        self.log.debug(f"Arming scope...")

        try:
            self.prep_shot()
            self.write(f":TRIGger:MODE SINGle")
            self.query("*OPC?")

            self.log.debug(f"Scope armed.")
        except Exception as e:
            self.log.error(f"Arming scope encountered error: {repr(e)}")

    def abort(self) -> None:
        raise NotImplementedError("ABORT not yet implemented.")

    def prep_shot(self) -> None:
        self.log.debug("Clearing data buffer...")
        self.write(":ACQuire:CSWeep")

    def trigger_software(self) -> None:
        self.log.debug("Software triggering device...")
        self.write("*TRG")

    def stop_mode(self) -> None:
        self.write(":TRIGger:STOP")

    def run_mode(self) -> None:
        self.write(":TRIGger:RUN")

    # ------------------------------------------------------------------------------------
    #  Read Only Methods
    # ------------------------------------------------------------------------------------

    @property
    def trigger_status(self) -> str:
        """
        Returns the status of the trigger (Arm|Ready|Auto|Trig'd|Roll).

        Notes:
            On single mode, this returns "Trig'd" when the first measurement is triggered and "Stop" when
            all the measurements have been triggered
        """
        _trigger_status = self.query(":TRIGger:STATus?")
        return _trigger_status.lower()

    @property
    def is_triggered(self) -> bool:
        _is_triggered = self.trigger_status == 'stop'
        return _is_triggered

    @property
    def check_connection(self) -> bool:
        try:
            resp = self.query('*IDN?')
            #typo in lecroy response - it actually returns 'lecory'
            _check_connection = True if 'lecory' in resp.lower() else False
        except Exception as e:
            _check_connection = False
        return _check_connection

    @property
    def acq_res(self) -> int:
        _bit_res = self.query(":ACQuire:RESolution?").rstrip('Bits')
        return int(_bit_res)

    @property
    def ch_mode(self) -> str:
        """
        Checks if there is either 1 or 2 active per channel pairs, but if both are 0, then return None
        """
        ch_pairs = [{1, 2}, {3, 4}]
        active_chs = [i + 1 for i in range(NCHAN) if self.query(f":CHANnel{i + 1}:SWITch?") == 'ON']

        active_chs_set = set(active_chs)
        check_pairs = [len(active_chs_set & ch_pair) for ch_pair in ch_pairs]

        num_active_per_pair = max(check_pairs)
        mode = 'dual' if num_active_per_pair == 2 else ('single' if num_active_per_pair == 1 else None)
        return mode

    @property
    def transient_mode(self) -> str:
        _transient_mode = self.query(":TRIGger:MODE?")
        return _transient_mode.lower()

    @transient_mode.setter
    def transient_mode(self, mode: str) -> None:
        mode_opts = ['run', 'stop']
        try:
            if mode.lower() not in mode_opts:
                self.log.warning(f"'{mode}' not in {mode_opts}, defaulted to 'STOP'.")
                mode = 'STOP'

            self.write(f":TRIGger:{mode}")
        except Exception as e:
            self.log.error(f"Setting transient_mode to '{mode}' encountered error: {e}")

    def wave_preamble(self, source: Union[str, int]) -> WaveformPreamble:
        source = f"C{source}" if isinstance(source, int) else source
        self.write(f":WAVeform:SOURce {source}")
        raw_pre = self.scope.query_binary_values(":WAVeform:PREamble?", datatype='B', container=bytes)
        _wave_preamble = WaveformPreamble.from_byte_block(raw_pre)
        return _wave_preamble

    # ------------------------------------------------------------------------------------
    #  Data Operation Methods
    # ------------------------------------------------------------------------------------

    def fetch_data(
            self,
            t_zero: str = 'start',
            w_format: str = 'list',
            data_window: Dict = None
    ) -> Tuple[Dict, Dict]:
        """
        Collect the currently displayed waveform. Not for sequence mode.

        Args:
            t_zero (str): where t = 0 is. Either "start" or "trigger"
            w_format (str): format that the waveform will be downloaded as
            data_window: controls how much of the screen to collect. An example of when this
                           might be changed is if you only want half the data on the screen.
        """

        data_window = data_window or DEFAULT_DATA_WINDOW
        settings = self._process_data(data_window)

        raw_data = {}
        volt_data = {}
        start_time = perf_counter()

        try:
            self.write(f"WAVeform:POINt 0")
            self.write(f":WAVeform:INTerval 1")
            max_point_transfer = int(self.query(f":WAVeform:MAXpoint?"))

            for ch_num in self.data_channels:
                self.log.debug(f"Collecting data for channel {ch_num}...")
                self.write(f"WAVeform:SOURce C{ch_num}")
                raw_data[str(ch_num)] = self._get_raw(settings, max_point_transfer)

            bit_res = self.acq_res
            data_ops = DataOperations(self.log)
            for ch_num, ch_data in raw_data.items():
                ch_num = int(ch_num)
                self.log.debug(f"Calculating voltage values for channel {ch_num}...")
                v_div = float(self.query(f":CHANnel{ch_num}:SCALe?"))
                v_offset = float(self.query(f":CHANnel{ch_num}:OFFset?"))

                conv_data = data_ops.convert_data(list(ch_data), bit_res)
                adj_data = data_ops.adjust_data(conv_data, bit_res)
                volt_data[str(ch_num)] = list(data_ops.calc_volts(adj_data, bit_res, v_div, v_offset))

            t_div, t_delay, num_points = self.get_timebase_info()
            time_axis = self.construct_time_axis(t_div, t_delay, num_points, t_zero, w_format)
            time_axis = time_axis[settings['start_point'] : settings['end_point']]

            data = {
                'times'     : time_axis.tolist(),
                # 'raw_data'  : raw_data,
                'voltages'  : volt_data
            }
            mat_data = {
                'times' : time_axis
            }

            for ch, ch_voltages in volt_data.items():
                mat_data[f"voltages_{ch}"] = ch_voltages

            self.log.debug(f"Time for data transfer (s): {perf_counter() - start_time:.3f} seconds")
            return mat_data, data
        except Exception as e:
            self.log.error(f"Fetching data encountered error: {repr(e)}")
            raise e

    def fetch_metadata(self) -> Dict:
        """
        Queries the scope and returns the current settings. Intended to be saved as metadata, or for debugging.
        Settings that are printed should be most of the relevant ones.
        """

        self.log.debug("Fetching scope metadata...")
        current_settings = {
            # acquire settings
            'acquire_mode'      : self.query('ACQuire:MODE?'),
            'acquire_type'      : self.query(':ACQuire:TYPE?'),
            'acquire_amode'     : self.query(':ACQuire:AMODe?'),
            'num_points'        : round(self.query_float(':ACQuire:POINts?')),
            'sample_rate'       : round(self.query_float(':ACQuire:SRATe?')),
            'memory_depth'      : self.query(':ACQuire:MDEPth?'),

            # sequence settings
            'sequence_on'       : self.query(':ACQuire:SEQuence?'),
            'sequence_count'    : self.query_int(':ACQuire:SEQuence:COUNt?'),

            # trigger settings
            'trigger_type'      : self.query(':TRIGger:TYPE?'),
            'trigger_source'    : self.query(':TRIGger:EDGE:SOURCe?'),
            'trigger_slope'     : self.query(':TRIGger:EDGE:SLOPe?'),
            'trigger_voltage'   : self.query_float(':TRIGger:EDGE:LEVel?'),
            'holdoff_mode'      : self.query(':TRIGger:EDGE:HOLDoff?'),

            # time-axis settings
            'time_scale'        : self.query_float(':TIMEbase:SCALe?'),
            'time_offset'       : self.query_float(':TIMebase:DELay?'),
            'channels'          : {}
        }

        # depending on holdoff_mode, query the time/num_events for holdoff
        holdoff_mode = current_settings['holdoff_mode'].lower()
        if 'time' in holdoff_mode:
            current_settings['holdoff_time'] = self.query_float(':TRIGger:EDGE:HLDTime?')

        elif 'events' in holdoff_mode:
            current_settings['holoff_events'] = self.query_int(':TRIGger:EDGE:HLDEVent?')

        for i in range(4):
            ch_num = i + 1
            channel_settings = {'channel_on': self.query(f":CHANnel{ch_num}:SWITch?")}

            if channel_settings['channel_on'] == 'ON':
                channel_settings.update({
                    'visible'           : self.query(f":CHANnel{ch_num}:VISible?"),
                    'scale'             : self.query_float(f":CHANnel{ch_num}:SCALe?"),
                    'probe'             : self.query_float(f":CHANnel{ch_num}:PROBe?"),
                    'offset'            : self.query_float(f":CHANnel{ch_num}:OFFSet?"),
                    'coupling'          : self.query(f":CHANnel{ch_num}:COUPling?"),
                    'impedance'         : self.query(f":CHANnel{ch_num}:IMPedance?"),
                    'bandwidth_limit'   : self.query(f":CHANnel{ch_num}:BWLimit?")
                })
            current_settings['channels'][str(ch_num)] = channel_settings

        return current_settings

    def get_timebase_info(self) -> tuple:
        """
        Query the scope for relevant info for the horizontal axis .

        Returns:
            Tuple (time_scale, time_delay, num_points)
        """
        self.log.debug("Fetching scope timebase metadata...")
        time_scale = self.query_float(":TIMebase:SCALe?")
        time_delay = self.query_float(":TIMebase:DELay?")
        num_points = round(self.query_float(':ACQuire:POINts?'))
        return time_scale, time_delay, num_points

    def construct_time_axis(
            self,
            time_per_div : float,
            time_delay : float,
            num_points : int,
            time_zero: str = 'start',
            data_format: str = 'list'
    ) -> np.ndarray:
        """
        Constructs a time axis for voltage data. Units are in seconds.

        Args:
            time_per_div (float): time per horizontal division
            time_delay (float): time offset from center
            num_points (int): number of points for axis
            data_format (str): data format being passed into the method
            time_zero (str): choose what point is t = 0. Options are "start" or "trigger".

        Notes:
            if zeropoint is "trigger", t = 0 will be the time when the trigger occured.
        """
        self.log.debug("Constructing time axis...")
        t_div = time_per_div or float(self.query(":TIMebase:SCALe?"))
        t_range = t_div * 10
        t_axis = np.linspace(0, t_range, num = num_points, endpoint = False)

        try:
            # shift access depending on zeropoint
            if time_zero == 'start':
                pass
            elif time_zero == 'trigger':
                t_axis = t_axis - t_range/2 + time_delay
            else:
                raise ValueError(f"{time_zero} not a valid option")

            if data_format == 'numpy':
                return t_axis
            elif data_format == 'list':
                return t_axis.tolist()
            else:
                raise ValueError(f"{data_format} is not a valid format")
        except Exception as e:
            self.log.error(f"Constructing time axis encountered error: {repr(e)}")

    # ------------------------------------------------------------------------------------
    #  Helper Methods
    # ------------------------------------------------------------------------------------

    def _get_raw(self, settings: Dict, chunk_size: int) -> bytearray:
        """
        Collect the raw data from the scope. If the data is too big, it will come in multiple chunks.

        Args:
            settings (Dict): contains the scope configuration that determines how data is being collected

        Returns:
            data (bytesarray): contains the binary data collected from active channel as a single bytearray
        """

        data = bytearray()
        chunk_size = chunk_size or int(self.query(":WAVeform:MAXpoint?"))
        points_collected = settings['start_point']
        expected_points = settings['expected_points']

        try:
            # Setting the scope to 10-bit requires two bytes sent by the scope for every point, so the byte width
            # of the raw data needs to be set to WORD for 16-bits else BYTE sends 8-bits.
            # NOTE: The programming manual under :WAVeform:WIDth indicates that setting as width as WORD, the
            # byte data will be transferred with the MSB first, then LSB (aka big endian). This is not the case,
            # and instead you need to refer the waveform preamble COMM_ORDER (see lecroy_preamble.py)
            bit_res = int(self.query(":ACQuire:RESolution?").rstrip('Bits'))
            if bit_res == 10:
                wave_width = 'WORD'
                bytes_per_point = 2
            else:
                wave_width = 'BYTE'
                bytes_per_point = 1
            self.write(f":WAVeform:WIDth {wave_width}")

            while points_collected < expected_points:
                sleep(0.1)

                current_chunk_size = min(expected_points - points_collected, chunk_size)
                self.write(f":WAVeform:POINt {current_chunk_size}")
                self.write(f":WAVeform:STARt {points_collected}")

                # Download data as unsigned bytes, then adjust for signed bytes values later during post-processing
                raw_data = self.scope.query_binary_values(":WAVeform:DATA?", datatype='B', container=bytearray)

                data += raw_data
                points_collected += len(raw_data) // bytes_per_point
                self.log.debug(f"Data Received: {points_collected:_} out of {expected_points:_}")

            # Ensure that all expected points are obtained
            num_points_to_capture = expected_points * bytes_per_point
            if len(data) != num_points_to_capture:
                raise ValueError(f"Expected {num_points_to_capture:_} bytes, but received {len(data):_} bytes.")

            return data
        except Exception as e:
            self.log.error(f"Fetching raw data encountered error: {e}")
        except errors.VisaIOError as e:
            raise e

    def _process_data(self, data_settings: Dict) -> Dict:

        max_rate = round(float(self.query(':ACQuire:SRATe?')))
        max_points = round(float(self.query(':ACQuire:POINts?')))

        start_point = round(data_settings['start_time'] * max_rate)

        if data_settings['end_time'] == 'MAX':
            end_point = max_points
        else:
            end_point = round(data_settings['end_time'] * max_rate)

        expected_points = end_point - start_point

        if start_point < 0 or start_point >= end_point:
            raise ValueError("Data settings don't make sense")
        if end_point > max_points:
            raise ValueError("End time is too high")

        settings = {
            'start_point'       : start_point,
            'end_point'         : end_point,
            'expected_points'   : expected_points
        }
        return settings