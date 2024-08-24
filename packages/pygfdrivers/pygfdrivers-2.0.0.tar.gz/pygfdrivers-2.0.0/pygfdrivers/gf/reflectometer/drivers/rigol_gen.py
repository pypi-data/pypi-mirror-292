"""
Class to set and modify config values on the RIGOL DG4102 Function Wave Generator.

Current methods:
    __init__: creates communication with generator
    run: Apply custom settings, verify, then run the generator
    close: Stop the generator from generating waveforms
    configure_settings: Configure generator settings based on script settings yaml
    get_settings: Get and return the current generator settings
    verify_settings: Compares the current settings on the generator to the ones provided in the yaml file.
    get_full_settings: Combines the script settings and current settings into one dictionary.
    write: writes a command to the generator
    query: query information from the generator

Created by Simon Marcotte, January 30th, 2024
"""

from typing import Dict
from .common.visa_device import VisaDevice


class RigolGen(VisaDevice):
    def __init__(self, ip_address: str, settings: Dict, log) -> None:
        super().__init__(ip_address, settings)
        self.generator = self.device
        self.log = log

    def run(self, settings: Dict) -> None:
        """ Apply custom settings, verify, then run the generator """
        ch_num = settings['generator_chn']
        is_on = self.query(f":OUTPut{ch_num}?") == 'ON'
        self.log.debug(f"Turning signal generator channel {ch_num} output ON...")

        if not is_on:
            try:
                self.write(f":OUTPut{ch_num} ON")
                self.log.debug(f"GEN channel {ch_num} output ON")
            except Exception as e:
                self.log.error(f"Turning on GEN channel {ch_num} output ON encountered error: {repr(e)}", exc_info=True)
        else:
            self.log.warning(f"Output is already ON.")

    def apply_configurations(self, settings: Dict) -> None:
        """ Configure generator settings based on script settings yaml """
        self.log.debug("Applying signal generator settings...")

        settings = settings or self.settings
        channel = settings['generator_chn']
        
        # Turn screen saver off
        self.write('DISPlay:SAVer:STATe OFF')

        # Apply mode type and frequency:
        self.write(f"SOURce{channel}:APPLy:{settings['waveform_mode']} {settings['frequency']}")
        self.write(f"SOURce{channel}:VOLTage:OFFSet {settings['offset']}")
        self.write(f"SOURce{channel}:VOLTage {settings['Vpp']}")

        # Set the channel to burst mode
        self.write(f"SOURce{channel}:BURSt ON")
        self.write(f"SOURce{channel}:BURSt:TRIGger:SOURce {settings['trig_source']}")
        self.write(f"SOURce{channel}:BURSt:NCYCles {settings['num_cycles']}")
        
        # Set duty and lead time
        self.write(f"SOURCe{channel}:PULSe:DCYCle {settings['duty_cycle']}")
        self.write(f"SOURCe{channel}:PULSe:TRANsition {settings['lead_time']}")
        self.write(f"SOURCe{channel}:PULSe:TRANsition:TRAiling {settings['trail_time']}")
        
        self.log.debug("Finished applying generator settings.")

    def get_settings(self, settings: Dict) -> Dict:
        """ Get and return the current generator settings """
        read_settings = {}
        channel = settings['generator_chn']
        settings = settings or self.settings

        # Get general generator settings
        gen_settings = self.query(f"SOURce{channel}:APPLy?")[1:-1].split(",")
        order = ["waveform_mode", "frequency", "Vpp", "offset", "delay"]

        for i, key in enumerate(order):
            read_settings[key] = gen_settings[i]

        # Get burst type and settings
        read_settings["burst_mode"] = self.query(f"SOURce{channel}:BURSt:MODE?")

        # Get other burst settings if in trigger mode
        if read_settings["burst_mode"].lower() in "triggered":
            read_settings['num_cycles'] = self.query(f"SOURce{channel}:BURSt:NCYCles?")
            read_settings['trig_source'] = self.query(f"SOURce{channel}:BURSt:TRIGger:SOURce?")
        
        read_settings['duty_cycle'] = self.query(f"SOURCe{channel}:PULSe:DCYCle?")
        read_settings['lead_time'] = self.query(f"SOURCe{channel}:PULSe:TRANsition?")
        read_settings['trail_time'] = self.query(f"SOURCe{channel}:PULSe:TRANsition:TRAiling?")

        return read_settings

    def verify_settings(self, settings: Dict, read_settings: Dict) -> bool:
        """
        Compares the current settings on the generator to the ones provided in the yaml file.
        If there are discrepancies, return false.
        """
        settings = settings or self.settings

        # Go through the current settings, and check against the yaml provided settings
        for key in read_settings.keys():

            # For numerical comparisons
            if read_settings[key][0].isnumeric():
                if float(read_settings[key]) != float(settings[key]):
                    self.log.warning(f"For {key}: {float(read_settings[key])} found, expected {float(settings[key])}")
                    return False

            # For string comparisons
            else:
                if read_settings[key].lower() not in settings[key].lower():
                    self.log.warning(f"For {key}: {read_settings[key]} found, expected {settings[key]} ")
                    return False
                
        self.log.debug("Generator Settings Verified.")
        return True

    def get_full_settings(self, settings: Dict) -> Dict:
        """
        Combines the script settings and current settings into one dictionary.
        Note that both the yaml config and current generator settings could be the same.
        """
        read_settings = self.get_settings(settings)
        full_settings = {'script_settings': settings, 'generator_settings': read_settings}
        return full_settings

    def trigger_software(self) -> None:
        self.write("*TRG")
    
    @property
    def check_connection(self) -> bool:
        try:
            resp = self.query('*IDN?')
            _check_connection = True if 'rigol' in resp.lower() else False
        except Exception as e:
            _check_connection = False
        return _check_connection
    