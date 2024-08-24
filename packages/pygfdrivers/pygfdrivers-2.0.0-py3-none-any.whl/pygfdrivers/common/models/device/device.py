from pydantic import Field, AliasChoices
from pygfdrivers.common.models.infrastructure.file import BaseFileModel


class BaseDeviceModel(BaseFileModel):
    device_name: str = Field(
        default=None,
        alias='name',
        validation_alias=AliasChoices('device_name', 'name')
    )
    device_conn_str: str = Field(
        default=None,
        alias='conn_str',
        validation_alias=AliasChoices('device_conn_str', 'conn_str', 'serial_number')
    )
    device_type: str = Field(
        default=None,
        alias='device_type',
        validation_alias=AliasChoices('device_type', 'scope_type', 'spectro_type', 'camera_type', 'type')
    )

    flag_armed: bool = Field(default=None, alias='is_armed')
    flag_connected: bool = Field(default=None, alias='is_online')
    flag_triggered: bool = Field(default=None, alias='is_triggered')
    flag_downloaded: bool = Field(default=None, alias='is_downloaded')
    flag_aborted: bool = Field(default=None, alias='is_aborted')
