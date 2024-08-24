from functools import cached_property

from pygfdrivers.common.visa.visa_scope import VisaScope
from pygfdrivers.common.visa.visa_cmd import BaseVisaScopeCommand
from pygfdrivers.common.models.device.cmd import create_cmd_class, CmdClassType


def init_common_cmds():
    common: CmdClassType = create_cmd_class('Common')
    common.add_cmd(key='idn',cmd='*idn')
    common.add_cmd(key='arm', cmd='arm')
    common.add_cmd(key='stop', cmd='stop')
    common.add_cmd(key='reset', cmd='*rst')
    common.add_cmd(key='status', cmd='inr')
    common.add_cmd(key='op_complete', cmd='*opc')
    common.add_cmd(key='single', cmd='trmd single')
    common.add_cmd(key='comm_header', cmd='chdr', args=['long', 'short', 'off'])
    return common


class LecroyCommon(BaseVisaScopeCommand):
    def __init__(self, scope: VisaScope) -> None:
        super().__init__(scope)

        self.common_cmds = init_common_cmds()

    @property
    def idn(self) -> str:
        _idn = self.query(self.common_cmds, 'idn')
        return _idn.lower()

    @property
    def op_complete(self) -> bool:
        _op_complete = self.query(self.common_cmds, 'op_complete')
        return bool(int(_op_complete))

    @op_complete.setter
    def op_complete(self, state: bool) -> None:
        self.write(self.common_cmds, 'op_complete', setting=int(state))

    def reset(self) -> None:
        self.log.debug("Resetting scope to factory default settings.")
        self.write(self.common_cmds, 'reset')

    def comm_header(self, setting: str) -> None:
        try:
            self.write(self.common_cmds, 'comm_header', setting=setting.lower())
        except Exception as e:
            self.log.error(f"Setting comm_header encountered error: {e}")

    @property
    def status(self) -> int:
        _status = self.query(self.common_cmds, 'status')
        return int(_status)

    def single_mode(self) -> None:
        self.write(cmd='arm')

    def stop_mode(self) -> None:
        self.write(cmd='stop')

    def run_mode(self) -> None:
        raise NotImplementedError
