import re
from typing import Dict, List
from .common.telnet_device import TelnetDevice


class Sam3Controller(TelnetDevice):
    def __init__(self, host_name: str, port_num: int, settings: Dict, log) -> None:
        super().__init__(host_name, port_num, settings, log)

        self.sam3_ctrl = self.telnet_device

    def apply_configurations(self, settings: Dict) -> None:
        self.log.debug("Applying telnet device settings...")

        try:
            self.defsw(int(settings['start_freq']), int(settings['stop_freq']), settings['sweep_time'])
            self.mode(settings['mode'])
            self.trigger(settings['trig_enable'])

            self.log.debug("Finished applying telnet device settings.")
        except Exception as e:
            self.log.error(f"Applying configurations encountered error: {e}")

    def arm(self) -> None:
        self.log.debug("Arming device...")
        self.trigger(True)
        self.log.debug("Device armed.")

    def mode(self, output_mode: str) -> None:
        mode_opts = ['normal', 'hopping', 'fast_hopping', 'sweep']

        if output_mode not in mode_opts:
            self.log.warning(f"{output_mode} is not in {mode_opts}, default to 'normal'.")
            output_mode = 'normal'

        try:
            self.write(f"mode {output_mode[0]}")
        except Exception as e:
            self.log.error(f"Setting output mode to {output_mode} encountered error: {e}")

    def trigger(self, state: bool) -> None:
        state = 'enable' if state else 'disable'
        try:
            self.write(f"trigger {state}")
        except Exception as e:
            self.log.error(f"Setting trigger to {state} encountered error: {e}")

    def defsw(self, start_freq: int, stop_freq: int, sweep_time: int) -> None:
        try:
            # Mode needs to be set to normal before changing sweep settings
            self.mode('normal')
            self.write(f"defsw i {start_freq} {stop_freq} {sweep_time}")
        except Exception as e:
            self.log.error(f"Setting sweep mode settings encountered error: {e}")

    @property
    def check_connection(self) -> bool:
        try:
            resp = self.write('help')
            _check_connection = True
        except Exception as e:
            _check_connection = False
        return _check_connection

    @property
    def status(self) -> Dict:
        _status = self.write('status').decode('unicode-escape')

        # Parse the status response and remove the empty items before further parsing
        status_list = _status.split('\n')
        status_list = [status_item for status_item in status_list if status_item.strip()]

        def freq_range(s: str) -> Dict:
            match = re.search(r"(\d+) to (\d+) kHz", s)
            if match:
                return {'min': match.group(1) + 'KHz', 'max': match.group(2) + 'KHz'}

        def sweep_settings(s: str) -> Dict:
            match = re.search(r"(\d+\.\d+) us from (\d+) to (\d+) KHz", s)
            if match:
                return {
                    'sweep_time'    : match.group(1) + ' us',
                    'start_freq'    : match.group(2) + 'KHz',
                    'end_freq'      : match.group(3) + 'KHz'
                }

        def ed04_if_gains(s: str) -> List:
            match = re.search(r"ED04 IF Gain control: ([\d, ]+) dB", s)
            if match:
                gains = match.group(1).split(', ')
                return [float(g) for g in gains]

        # Mapping of keys to their parsing functions
        status_dict = {
            'hardware_rev'              : status_list[0].split('Hardware rev. ')[1],
            'software_rev'              : status_list[1].split('Software rev. ')[1],
            'memory_available'          : status_list[2].split('Free memory ')[1],
            'connection_status'         : status_list[3],
            'configured_boards'         : status_list[4].split('Configured Boards: ')[1],
            'freq_range'                : freq_range(status_list[5]),
            'hopping_table_status'      : status_list[6].split('Hopping table ')[1],
            'sweep_settings'            : sweep_settings(status_list[7]),
            'post_sweep_ramp_tail'      : status_list[8].split('Post sweep Ramp Tail is ')[1],
            'pre_trigger_delay'         : status_list[9].split('Trigger pre-delay is ')[1],
            'post_trigger_delay'        : status_list[10].split('Trigger post-delay is ')[1],
            'hopping_interrupt_status'  : status_list[11].split('Hopping interrupt by sweep is ')[1],
            'trace_status'              : status_list[12].split('Trace is ')[1],
            'mode'                      : status_list[13].split('Mode is ')[1],
            'trigger_status'            : status_list[14].split('Trigger is ')[1],
            'ed04_if_gains'             : ed04_if_gains(status_list[15]),
            'freq_master'               : status_list[16].split('Normal mode Frequency Master is ')[1],
            'actual_main_freq'          : status_list[17].split('Actual Main frequency ')[1]
        }

        return status_dict

