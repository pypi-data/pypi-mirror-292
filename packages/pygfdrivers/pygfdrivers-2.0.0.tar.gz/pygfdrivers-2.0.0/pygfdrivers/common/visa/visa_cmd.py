from logging import getLogger
from typing import Any, Optional, Union, List, Dict

# custom packages
from pygfdrivers.common.visa.visa_scope import VisaScope
from pygfdrivers.common.models.device.cmd import CmdClassType
from pygfdrivers.common.util.exceptions import DeviceExceptions as dev_err
from pygfdrivers.common.util.exceptions import CommandClassExceptions as cmd_err


class BaseVisaScopeCommand:
    def __init__(self, visa_scope: VisaScope = None) -> None:

        self.scope = visa_scope

        self.log = getLogger(__name__)
        self.scope_series = self.scope.scope_series
        self.is_mxr = self.scope_series == 'MXR'

        self.write = self.scope.write_scope
        self.query = self.scope.query_scope
        self.set_and_verify_config = self.scope.set_and_verify_config
        self.read_bytes = self.scope.read_bytes_from_scope

        self.trig_fields = getattr(self.scope.scope_info.trigger, 'model_fields')
        self.capture_fields = getattr(self.scope.scope_info.capture, 'model_fields')
        self.source_fields = getattr(getattr(self.scope.scope_info.channels, 'default_factory'), 'model_fields')

    def create_cmd_str(
            self,
            cmd_obj: CmdClassType,
            cmd_key: str,
            setting: Union[int, float, str] = None,
            channel: Union[int, str] = None
    ) -> str:
        self.log.debug(f"construct_cmd string for '{cmd_key}' in '{cmd_obj.__name__}'...")

        try:
            cmd = self.fetch_cmd(cmd_obj, cmd_key)

            if channel is not None:
                cmd = self.format_cmd_with_channel(cmd, channel)

            if setting is not None:
                cmd = f"{cmd} {setting}"

            return cmd
        except Exception as e:
            self.log.error(f"Constructing VISA command string encountered error: {e}")

    def format_cmd_with_channel(self, cmd: str, channel: Union[int, str]) -> str:
        self.log.debug(f"format_cmd_with_channel for '{cmd}' with channel '{channel}'...")

        try:
            if self.device_mfr == 'keysight':
                return f":CHANnel{channel}{cmd}"

            elif self.device_mfr == 'lecroy':
                return f"c{channel}{cmd}"

            else:
                raise dev_err.DeviceNotSupportedError

        except dev_err.DeviceNotSupportedError:
            self.log.error(f"Scope manufacturer '{self.device_mfr}', not yet supported.")

    # ------------------------------------------------------------------------------------
    #  Main Methods
    # ------------------------------------------------------------------------------------

    def fetch_cmd(self, cmd_obj: CmdClassType, cmd_key: str) -> str:
        self.log.debug(f"fetch_cmd for '{cmd_key}' in '{cmd_obj.__name__}'...")
        try:
            if not hasattr(cmd_obj, cmd_key):
                raise cmd_err.CommandNotSupportedError

            cmd_attrs = getattr(cmd_obj, cmd_key)
            if not hasattr(cmd_attrs, 'cmd'):
                raise cmd_err.CommandError

            return cmd_attrs.cmd
        except cmd_err.CommandNotSupportedError:
            self.log.error(f"'{cmd_key}' command not yet supported.")

        except cmd_err.CommandError:
            self.log.debug(f"'{cmd_key}' in '{cmd_obj.__name__}' does not have a 'cmd' attribute.")

    def fetch_cmd_args(self, cmd_obj: CmdClassType, cmd_key: str) -> Union[List, Dict, None]:
        self.log.debug(f"fetch_cmd_args for '{cmd_key}' in '{cmd_obj.__name__}'...")
        try:
            cmd_attrs = getattr(cmd_obj, cmd_key)
            if not hasattr(cmd_attrs, 'args'):
                raise cmd_err.CommandArgsError

            return cmd_attrs.args
        except cmd_err.CommandArgsError:
            self.log.debug(f"'{cmd_key}' in '{cmd_obj.__name__}' does not have an 'args' attribute.")

    def fetch_cmd_default(self, cmd_obj: CmdClassType, cmd_key: str) -> Union[int, float, str]:
        self.log.debug(f"fetch_cmd_default for '{cmd_key}' in '{cmd_obj.__name__}'...")
        try:
            cmd_attrs = getattr(cmd_obj, cmd_key)
            if not hasattr(cmd_attrs, 'default'):
                raise cmd_err.CommandDefaultError

            return cmd_attrs.default
        except cmd_err.CommandDefaultError:
            self.log.error(f"'{cmd_key}' in '{cmd_obj.__name__}' does not have a 'default' attribute.")

    # ------------------------------------------------------------------------------------
    #  Command Class Methods
    # ------------------------------------------------------------------------------------

    def update_cmd_args(self, obj: CmdClassType, key: str, args: Optional[Any]) -> None:
        try:
            cmd_info = getattr(obj, key)
            cmd_info.args = args
        except Exception as e:
            self.log.error(f"Updating '{obj.__name__}' key '{key}' args to '{args}' encountered error: {e} ")

    def update_cmd_default(self, obj: CmdClassType, key: str, default: Optional[Any]) -> None:
        try:
            cmd_info = getattr(obj, key)
            cmd_info.default = default
        except Exception as e:
            self.log.error(f"Updating '{obj.__name__}' key '{key}' default to '{default}' encountered error: {e} ")