from typing import List, Dict
from collections import defaultdict
from pydantic import BaseModel, Field

from pygfdrivers.common.models.device.visa import BaseVisaDeviceModel

from pygfdrivers.lecroy.models.trigger import LecroyTriggerModel
from pygfdrivers.lecroy.models.capture import LecroyCaptureModel
from pygfdrivers.lecroy.models.channel import LecroyChannelDataModel


class LecroyScopeDataModel(BaseModel):
    scope: BaseVisaDeviceModel = Field(
        default_factory=lambda: BaseVisaDeviceModel()
    )
    capture: LecroyCaptureModel = Field(
        default_factory=lambda: LecroyCaptureModel()
    )
    trigger: LecroyTriggerModel = Field(
        default_factory=lambda: LecroyTriggerModel()
    )
    active_channels: List[int] = Field(
        default_factory=lambda: list()
    )
    channels: Dict[str, LecroyChannelDataModel] = Field(
        default_factory=lambda: defaultdict(LecroyChannelDataModel)
    )
