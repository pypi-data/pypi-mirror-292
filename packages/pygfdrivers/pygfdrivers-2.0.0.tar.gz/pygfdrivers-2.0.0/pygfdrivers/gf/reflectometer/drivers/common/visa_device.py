from pyvisa import ResourceManager
from pyvisa.resources import Resource
from typing import Dict

TIMEOUT = 10_000     # in ms
CHUNK_SIZE = 1024 * 1024 * 1024 * 8


class VisaDevice:
    _rm = ResourceManager()

    def __init__(self, ip_address: str, settings: Dict) -> None:
        self.device = self.connect(f"TCPIP0::{ip_address}::inst0::INSTR")
        self.settings = settings

    def connect(self, conn_str: str) -> Resource:
        _device = self._rm.open_resource(conn_str)
        _device.timeout = TIMEOUT
        _device.read_termination = '\n'
        # _device.chunk_size = CHUNK_SIZE
        return _device

    def close(self) -> None:
        if self.device:
            self.device.close()

    def write(self, cmd: str) -> None:
        self.device.write(cmd)

    # ------------------------------------------------------------------------------------
    #  Query Methods
    # ------------------------------------------------------------------------------------

    def query(self, cmd: str) -> str:
        response = self.device.query(cmd)
        return response

    def query_float(self, query_str: str) -> float:
        return float(self.query(query_str))

    def query_int(self, query_str: str) -> int:
        return int(self.query(query_str))