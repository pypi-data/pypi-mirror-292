from collections import defaultdict
from typing import List, Dict
from pydantic import AliasChoices, Field

from pygfdrivers.common.models.infrastructure.config import BaseConfigDeviceModel
from pygfdrivers.common.models.device.visa import BaseVisaDeviceModel
from pygfdrivers.keysight.models.capture import KeysightCaptureModel
from pygfdrivers.keysight.models.trigger import KeysightTriggerModel
from pygfdrivers.keysight.models.channel import KeysightChannelModel


class KeysightScopeConfigModel(BaseConfigDeviceModel):
    device: BaseVisaDeviceModel = Field(
        default_factory=lambda: BaseVisaDeviceModel(),
        validation_alias=AliasChoices('scope', 'scope_settings', 'scope_info', 'device_settings')
    )
    capture: KeysightCaptureModel = Field(
        default_factory=lambda: KeysightCaptureModel(),
        validation_alias=AliasChoices('capture', 'capture_settings')
    )
    trigger: KeysightTriggerModel = Field(
        default_factory=lambda: KeysightTriggerModel(),
        validation_alias=AliasChoices('trigger', 'trigger_settings')
    )
    active_channels: List[int] = Field(
        default_factory=lambda: list(),
        validation_alias=AliasChoices('active_channels', 'active_sources')
    )
    channels: Dict[int, KeysightChannelModel] = Field(
        default_factory=lambda: defaultdict(KeysightChannelModel),
        validation_alias=AliasChoices('channels', 'channel_settings')
    )
