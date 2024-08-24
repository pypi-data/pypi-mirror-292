from functools import cached_property

from pygfdrivers.common.visa.visa_scope import VisaScope
from pygfdrivers.common.visa.visa_cmd import BaseVisaScopeCommand
from pygfdrivers.common.models.device.cmd import create_cmd_class, CmdClassType


def init_common_cmds():
    common: CmdClassType = create_cmd_class('Common')
    common.add_cmd(key='idn', cmd='*idn')
    common.add_cmd(key='learn', cmd='*lrn')
    common.add_cmd(key='reset', cmd='*rst')
    common.add_cmd(key='recall', cmd='*rcl')
    common.add_cmd(key='options', cmd='*opt')
    common.add_cmd(key='trigger', cmd='*trg')
    common.add_cmd(key='op_complete', cmd='*opc')
    common.add_cmd(key='clear_status', cmd='*cls')
    return common


class KeysightCommon(BaseVisaScopeCommand):
    def __init__(self, scope: VisaScope) -> None:
        super().__init__(scope)

        self.common_cmds = init_common_cmds()

    # ------------------------------------------------------------------------------------
    #  Core Common Methods - common amongst all Keysight scopes and unlikely to be modified
    # ------------------------------------------------------------------------------------

    def clear_status(self) -> None:
        self.log.debug("Clearing scope status")
        self.write(self.common_cmds, 'clear_status')

    @property
    def learn(self) -> str:
        _learn = self.query(self.common_cmds, 'learn')
        return _learn

    @property
    def recall(self) -> int:
        return self._recall

    @recall.setter
    def recall(self, setup_num: int) -> None:
        self._recall = setup_num
        self.log.debug(f"Recalling scope setup '{setup_num}'.")
        self.write(self.common_cmds, 'recall', setting=setup_num)

    def reset(self) -> None:
        self.log.debug("Resetting scope to factory default settings.")
        self.write(self.common_cmds, 'reset')

    @property
    def op_complete(self) -> bool:
        _op_complete = self.query(self.common_cmds, 'op_complete')
        return bool(int(_op_complete))

    @op_complete.setter
    def op_complete(self, state: bool) -> None:
        self.write(self.common_cmds, 'op_complete', setting=int(state))

    @property
    def idn(self) -> str:
        _idn = self.query(self.common_cmds, 'idn')
        return _idn.lower()

    @cached_property
    def options(self) -> str:
        _options = self.query(self.common_cmds, 'options')
        return _options.lower()
