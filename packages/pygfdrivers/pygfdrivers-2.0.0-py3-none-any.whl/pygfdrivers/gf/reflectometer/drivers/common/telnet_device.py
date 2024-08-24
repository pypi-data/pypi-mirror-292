import pexpect
import platform
from typing import Dict
from pexpect.popen_spawn import PopenSpawn


class TelnetDevice:
    def __init__(self, host_name: str, port_num: int, settings: Dict, log) -> None:
        self.log = log

        self.port = port_num
        self.host = host_name
        self.settings = settings

        try:
            self.telnet_device = self.connect(host_name, port_num)
            if self.telnet_device is None:
                raise ValueError(f"Unable to connect to the telnet device {self.host}:{self.port}.")

            # Clear buffer
            self.telnet_device.expect('\n>')
        except Exception as e:
            self.log.error(f"Failed to connect to {self.host}:{self.port} - {e}")

    def connect(self, host_name: str, port_num: int) -> PopenSpawn:
        self.log.debug(f"Attempting to connect to {host_name}:{port_num}...")
        conn_cmd = f"{host_name} {port_num}" if port_num is not None else f"{host_name}"
        try:
            if platform.system() == 'Windows':
                telnet_client = PopenSpawn(f'plink.exe -telnet {host_name} -P {port_num}', timeout=5)
            else:
                telnet_client = pexpect.spawn(f"telnet {conn_cmd}", timeout=5)

            self.log.debug(f"Connected to {host_name}:{port_num}")
            return telnet_client
        except Exception as e:
            self.log.error(f"Connection error: {e}")
            raise

    def reconnect(self) -> None:
        self.log.debug("Attempting to reconnect to telnet device...")
        try:
            self.telnet_device = self.connect(self.host, self.port)
        except Exception as e:
            self.log.error(f"Reconnection failed: {e}")

    def close(self) -> None:
        self.log.debug("Exiting telnet device...")
        self.write('exit')

    def write(self, cmd_str: str) -> bytes:
        self.telnet_device.sendline(cmd_str)

        try:
            self.telnet_device.expect(['\n>', ' >'], timeout=5)
            response = self.telnet_device.before
            return response

        except pexpect.EOF:
            self.log.error(f"EOF in TELNET command - {cmd_str}")
        except pexpect.TIMEOUT:
            self.log.error(f"TIMEOUT in TELNET command - {cmd_str}")
        except Exception as e:
            self.log.error(f"An error occurred: {e}")