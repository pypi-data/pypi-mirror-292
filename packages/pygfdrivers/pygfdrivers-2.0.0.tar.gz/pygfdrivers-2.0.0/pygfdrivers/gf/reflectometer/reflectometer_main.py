"""
The main script for the reflectometer scope. Sends the scope settings and waits until it triggers. Once
it triggers, collects the data and saves it. Scope and file settings come from a YAML configuration file
which can be modified.

This script runs forever, i.e., once the data is collected it restarts and waits for the next trigger. To
close the script press CTRL-C. Collecting the data is quite slow and may take 15-18 minutes.

Author: Armaan Randhawa, Nov 2023
"""

from typing import List, Dict, Tuple
from pyvisa import errors
from pygfdrivers.gf.reflectometer.drivers.rigol_gen import RigolGen
from pygfdrivers.gf.reflectometer.drivers.lecroy_scope import LecroyScope
from pygfdrivers.gf.reflectometer.drivers.telnet_client import Sam3Controller
from pygfdrivers.common.base_device import BaseDevice
from pygfdrivers.gf.reflectometer.models.reflectometer_config import ReflectometerConfig


class Reflectometer(BaseDevice):
    def __init__(self, reflectomter_config: ReflectometerConfig = None) -> None:
        super().__init__(reflectomter_config)

    def init(self) -> None:
        self.connect()

    
    def connect(self) -> None:
        # Parse and apply scope settings from main.yaml
        try:
            self.scope = LecroyScope(self.config.lecroy.ip_address, self.config.lecroy.dict(), self.log)
            if self.scope is None:
                raise ValueError(f"Failed to connect to scope at IP address: {self.config.lecroy.ip_address}")
            self.log.info(f"Connected to lecroy scope at IP address: {self.config.lecroy.ip_address}")

            # Parse and apply signal generator settings from main.yaml
            self.generator = RigolGen(self.config.generator.ip_address, self.config.generator.dict(), self.log)
            if self.generator is None:
                raise ValueError(f"Failed to connect to signal generator at IP address: {self.config.generator.ip_address}")
            self.log.info(f"Connected to signal generator at IP address: {self.config.generator.ip_address}")

            # Parse telnet settings and create object
        
            host, port = self.config.telnet.host, self.config.telnet.port
            self.telnet_client = Sam3Controller(host, port, self.config.telnet.dict(), self.log)
            if self.telnet_client is None:
                raise ValueError(f"Failed to connect to telnet client at {host}:{port}")
            self.log.info(f"Connected to telnet client at {host}:{port}")
        except ValueError as e:
            self.log.error(f"Failed to connect to reflectometer devices: {e}")
        except Exception as e:
            
            self.log.error(f"Error occured while connecting to reflectometer: {e}")
    

    def check_connection(self) -> bool:
        try:
            self.is_connected = self.scope.check_connection and self.generator.check_connection
            if self.config.telnet.enabled:
                self.is_connected = self.is_connected and self.telnet_client.check_connection
            return self.is_connected
        except Exception as e:
            return self.is_connected

    def disconnect(self) -> None:
        try:
            #check if attr exists to see if any opened, then close
            if getattr(self, 'scope', None) is not None:
                self.scope.close()
            if getattr(self, 'generator', None) is not None:
                self.generator.close()
            if self.config.telnet.enabled:
                if getattr(self, 'telnet_client', None) is not None:
                    self.telnet_client.close()
            self.is_connected = False
            self.log.info("Disconnected from reflectometer devices.")
        except Exception as e:
            self.log.error(f"Failed to disconnect properly: {e}")

    def apply_configurations(self) -> None:
        try:
            self.scope.apply_configurations(self.config.lecroy.dict())
            self.generator.apply_configurations(self.config.generator.dict())
            if self.config.telnet.enabled:
                self.telnet_client.apply_configurations(self.config.telnet.dict())
            self.is_configured = True
            self.log.info("Applied reflectometer configurations")
        except Exception as e:
            self.log.error(f"Applying configurations encountered error: {e}.")
            self.is_configured = False
    
    def prep_shot(self) -> None:
        try:
            self.abort()
            self.is_armed = False
            self.is_triggered = False
            self.is_downloaded = False
            self.is_aborted = False
            self.data = None
        except Exception as e:
            self.log.error(f"Preparing shot encountered error: {e}.")

    def arm(self) -> None:
        try:
            self.data = {'metadata': {}, 'data': None}
            telnet_metadata = None
            # every shot telnet device should check status and if different send commands
            if self.config.telnet.enabled:
                telnet_metadata = self.telnet_client.status
            self.data['metadata'].update({'telnet_commands' : telnet_metadata})
            self.data['metadata'].update({'scope': self.scope.fetch_metadata()})
            self.data['metadata'].update({'generator': self.generator.get_full_settings(self.config.generator.dict())})

            self.scope.arm()
            self.generator.run(self.config.generator.dict())
            self.is_armed = True
            self.log.info("Armed reflectometer devices")
        except Exception as e:
            self.log.error(f"Arming scope encountered error: {e}.")
    
    def trigger_software(self) -> None:
        """ Trigger the lecroy scope """
        #TODO: This does not triger the generator to run
        try:
            self.scope.trigger_software()
            self.is_triggered = self.scope.is_triggered
            self.log.info("Triggered reflectometer devices.")
        except Exception as e:
            self.log.error(f"Triggering scope encountered error: {e}.")

    def abort(self) -> None:
        try:
            self.scope.abort()
            self.is_aborted = True
            self.log.info("Aborted reflectometer devices")
        except Exception as e:
            self.log.error(f"Aborting scope encountered error: {e}.")

    def fetch_data(self) -> Tuple:
        self.log.info("Collecting data from scope...")
        try:
            _, raw_data = self.scope.fetch_data(t_zero=self.config.data.t_zero, w_format='numpy', data_window=self.config.data.dict())
            self.data['data'] = raw_data
            self.log.info("Data collected")
            self.is_downloaded = True
        except errors.VisaIOError as e:
            self.log.error(f"Device timed out while fetching data with error: {e}")
    
    def fetch_metadata(self) -> Dict:
        pass

    def telnet_communicate(self, telnet_client: Sam3Controller, commands: List[str]) -> Dict:
        """
        Send some commands to the telnet network, and place the commands and their response in metadata
        """
        if "exit" != commands[-1]:
            commands.append("exit")

        telnet_response = {}
        self.log.info("Open Telnet connection: sending commands")

        try:
            telnet_response = telnet_client.send_commands(commands)
        except Exception as e:
            self.log.error(f"Could not send commands on Telnet encountered error: {repr(e)}")
        self.log.info("Telnet closed.")

        return telnet_response
    

    @property
    def trigger_status(self) -> bool:
        try:
            _trigger_status = self.scope.is_triggered
            _trigger_status = _trigger_status
            self.log.debug(f"Trigger Status: {_trigger_status}")
            return _trigger_status
        except Exception as e:
            self.log.error(f"Querying trigger status encountered error: {e}")