from pydantic import AliasChoices, Field

from pygfdrivers.common.models.device.device import BaseDeviceModel
from pygfdrivers.common.models.infrastructure.config import BaseConfigDeviceModel


class AXUVDeviceInfo(BaseDeviceModel):
    hostname: str = Field(
        default=None,
        alias='hostname',
        validation_alias=AliasChoices('hostname', 'host')
    )

    username: str = Field(
        default=None,
        alias='hostname',
        validation_alias=AliasChoices('username', 'user')
    )

    password: str = Field(
        default=None,
        alias='password',
        validation_alias = AliasChoices('password', 'pass')
    )

    remote_file: str = Field(
        default=None,
        alias='remote_file',
        validation_alias = AliasChoices('remote_file', 'remote')
    )


class AXUVDigitizerConfig(BaseConfigDeviceModel):
    device: AXUVDeviceInfo = Field(
        default_factory=lambda: AXUVDeviceInfo(),
        alias='device',
        validation_alias=AliasChoices('scope', 'scope_settings', 'device_settings')
    )
