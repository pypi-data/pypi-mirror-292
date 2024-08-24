from abc import ABC
from pydantic import BaseModel
from collections import defaultdict

from pygfdrivers.common.model_map import model_map
from pygfdrivers.common.base_device import BaseDevice

from pygfdrivers.dtacq.models.scope_data import DtacqSiteDataModel
from pygfdrivers.keysight.models.scope_data import KeysightChannelDataModel


class BaseScope(BaseDevice, ABC):
    def __init__(self, scope_config: BaseModel) -> None:
        super().__init__(scope_config)

        self.scope = None
        self.scope_series = None
        self.file_name = self.name

        self.scope_talk_delay = 0.1  # 0.1 not working for Lecroys
        self.scope_type = self.config.device.device_type

        self.init_scope_info()

    def init_scope_info(self) -> None:
        # TODO: Need to make this dyanmic to the scope_info specific to the scope_type
        try:
            self.scope_info = model_map['scope_info'].get(self.scope_type)()
            if self.scope_info is None:
                raise ValueError(f"Scope type '{self.scope_type}' does not have mapped scope_info model.'")

            setattr(self.scope_info, 'scope', self.config.device)
            if 'dtacq' in self.scope_type:
                setattr(self.scope_info, 'active_sites', self.config.active_sites)
            else:
                setattr(self.scope_info, 'active_channels', self.config.active_channels)
        except Exception as e:
            self.log.error(f"Initializing scope info encountered error: {e}")

    def clear_scope_info_data(self) -> None:
        if 'dtacq' in self.scope_type:
            setattr(self.scope_info, 'sites', defaultdict(DtacqSiteDataModel))
        elif 'keysight' in self.scope_type:
            setattr(self.scope_info, 'channels', defaultdict(KeysightChannelDataModel))
