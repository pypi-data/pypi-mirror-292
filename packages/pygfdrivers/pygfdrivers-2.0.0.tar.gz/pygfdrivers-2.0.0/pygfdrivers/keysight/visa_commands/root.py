from functools import cached_property

from pygfdrivers.common.visa.visa_scope import VisaScope
from pygfdrivers.common.visa.visa_cmd import BaseVisaScopeCommand
from pygfdrivers.common.models.device.cmd import create_cmd_class, CmdClassType


def init_root_cmds() -> CmdClassType:
    root: CmdClassType = create_cmd_class('Root')
    root.add_cmd(key='run', cmd=':run')
    root.add_cmd(key='stop', cmd=':stop')
    root.add_cmd(key='single', cmd=':single')
    root.add_cmd(key='arm_status', cmd=':aer')
    root.add_cmd(key='serial_num', cmd=':serial')
    root.add_cmd(key='trigger_status', cmd=':ter')
    return root


class KeysightRoot(BaseVisaScopeCommand):
    def __init__(self, scope: VisaScope) -> None:
        super().__init__(scope)

        self.root_cmds = init_root_cmds()

    # ------------------------------------------------------------------------------------
    #  Core Root Methods - common amongst all Keysight scopes and unlikely to be modified
    # ------------------------------------------------------------------------------------

    @property
    def arm_status(self) -> bool:
        _arm_status = self.query(self.root_cmds, 'arm_status')
        return bool(int(_arm_status))

    @property
    def trigger_status(self) -> bool:
        _trigger_status = self.query(self.root_cmds, 'trigger_status')
        return bool(int(_trigger_status))

    def single_mode(self) -> None:
        self.log.debug(f"Setting scope to 'single' mode.")
        self.write(self.root_cmds, 'single')

    def stop_mode(self) -> None:
        self.log.debug(f"Setting scope to 'stop' mode.")
        self.write(self.root_cmds, 'stop')

    def run_mode(self) -> None:
        self.log.debug(f"Setting scope to 'run' mode.")
        self.write(self.root_cmds, 'run')

    # ------------------------------------------------------------------------------------
    #  Non-Core Root Methods - not universal amongst all Keysight scopes
    # ------------------------------------------------------------------------------------

    @cached_property
    def serial_num(self) -> str:
        _serial_num = self.query(self.root_cmds, 'serial_num')
        return _serial_num
