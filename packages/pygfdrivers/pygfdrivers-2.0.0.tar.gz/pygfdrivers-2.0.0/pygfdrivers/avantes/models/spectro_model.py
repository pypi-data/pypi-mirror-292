from typing import List, Union
from pydantic import BaseModel, Field, AliasChoices

from pygfdrivers.common.models.device.device import BaseDeviceModel
from pygfdrivers.avantes.models.c_struct_models import DeviceConfigModel
from pygfdrivers.common.models.infrastructure.config import BaseConfigDeviceModel


class AvantesDataModel(BaseModel):
    scan_data: List[List[Union[int, float]]] = Field(
        default_factory=lambda: list(),
        alias='raw_data'
    )
    scan_times: List[float] = Field(
        default_factory=lambda: list(),
        alias='time_tags'
    )
    wavelengths: List[float] = Field(
        default_factory=lambda: list(),
        alias='wavelengths'
    )
    location: str = Field(
        default=None,
        alias='location'
    )


class AvantesSpectroInfoModel(BaseDeviceModel, DeviceConfigModel):
    class Config:
        extra = 'allow'
    device_serial_num: str = Field(
        default=None,
        alias='serial_num',
        validation_alias=AliasChoices('device_conn_str', 'conn_str', 'serial_num', 'serial')
    )
    device_conn_type: str = Field(
        default=None,
        alias='conn_type',
        validation_alias=AliasChoices('device_conn_type', 'conn_type', 'conn_media')
    )
    flag_timeout: bool = Field(
        default=False,
        alias='timed_out'
    )


class AvantesSpectroModel(BaseConfigDeviceModel):
    device: AvantesSpectroInfoModel = Field(
        default_factory=lambda: AvantesSpectroInfoModel(),
        alias='device_settings',
        validation_alias=AliasChoices('device', 'device_settings')
    )
    data: AvantesDataModel = Field(
        default_factory=lambda: AvantesDataModel(),
        alias='frames_data'
    )
