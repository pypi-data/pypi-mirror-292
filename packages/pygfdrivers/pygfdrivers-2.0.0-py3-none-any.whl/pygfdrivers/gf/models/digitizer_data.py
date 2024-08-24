from pydantic import Field, BaseModel
from typing import Dict, List
from collections import defaultdict

from pygfdrivers.gf.models.digitizer_config import (
    GFTriggerModel,
    GFDigitizerInfo,
    GFCaptureModel,
    GFChannelModel,
)


class GFChannelDataModel(GFChannelModel):
    raw_data: List = Field(
        default= None
    )

    volt_value: List = Field(
        default= None
    )


class GFDigitizerDataModel(BaseModel):
    scope: GFDigitizerInfo = Field(
        default_factory=lambda: GFDigitizerInfo()
    )
    capture: GFCaptureModel = Field(
        default_factory=lambda: GFCaptureModel()
    )
    trigger: GFTriggerModel = Field(
        default_factory=lambda: GFTriggerModel()
    )
    active_channels: List[int] = Field(
        default_factory=lambda: list()
    )
    channels: Dict[str, GFChannelDataModel] = Field(
        default_factory=lambda: defaultdict(GFChannelDataModel)
    )
