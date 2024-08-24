from typing import List, Dict
from collections import defaultdict
from pydantic import BaseModel, Field

from pygfdrivers.common.models.device.visa import BaseVisaDeviceModel
from pygfdrivers.keysight.models.capture import KeysightCaptureModel
from pygfdrivers.keysight.models.trigger import KeysightTriggerModel
from pygfdrivers.keysight.models.channel import KeysightChannelDataModel


class KeysightScopeDataModel(BaseModel):
    scope: BaseVisaDeviceModel = Field(
        default_factory=lambda: BaseVisaDeviceModel()
    )
    capture: KeysightCaptureModel = Field(
        default_factory=lambda: KeysightCaptureModel()
    )
    trigger: KeysightTriggerModel = Field(
        default_factory=lambda: KeysightTriggerModel()
    )
    active_channels: List[int] = Field(
        default_factory=lambda: list()
    )
    channels: Dict[str, KeysightChannelDataModel] = Field(
        default_factory=lambda: defaultdict(KeysightChannelDataModel)
    )
