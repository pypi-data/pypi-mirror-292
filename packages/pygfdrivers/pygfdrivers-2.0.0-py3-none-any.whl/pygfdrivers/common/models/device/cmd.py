from typing import Any, Optional, Union, List, Dict
from pydantic import BaseModel, Field


class CmdInfo(BaseModel):
    cmd: str
    args: Optional[Any] = None
    default: Optional[Union[int, str, float, bool]] = None


class CmdClassType(BaseModel):
    commands: Dict[str, CmdInfo] = Field(default_factory=dict)

    def add_cmd(self, key: str, cmd: str, args: Optional[Any] = None, default: Optional[Union[int, str, float, bool]] = None):
        self.commands[key] = CmdInfo(cmd=cmd, args=args, default=default)

    def is_valid_cmd_key(self, cmd_key: str) -> bool:
        return cmd_key in self.commands

    def fetch_cmd(self, cmd_key: str) -> Optional[str]:
        cmd_info = self.commands.get(cmd_key)
        return cmd_info.cmd if cmd_info else None

    def fetch_args(self, cmd_key: str) -> Optional[Union[List, Dict]]:
        cmd_info = self.commands.get(cmd_key)
        return cmd_info.args if cmd_info and cmd_info.args else None

    def fetch_default(self, cmd_key: str) -> Optional[Union[int, float, str, bool]]:
        cmd_info = self.commands.get(cmd_key)
        return cmd_info.default if cmd_info and cmd_info.default else None

    def update_cmd_args(self, key: str, args: Optional[Any]):
        if key in self.commands:
            self.commands[key].args = args

    def update_cmd_default(self, key: str, default: Optional[Union[int, str, float, bool]]):
        if key in self.commands:
            self.commands[key].default = default


def create_cmd_class(class_name: str) -> CmdClassType:
    return CmdClassType()
