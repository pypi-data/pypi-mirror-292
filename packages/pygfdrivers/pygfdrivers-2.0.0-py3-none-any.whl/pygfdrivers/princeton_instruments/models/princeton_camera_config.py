from pydantic import AliasChoices, Field

from pygfdrivers.common.models.device.device import BaseDeviceModel
from pygfdrivers.common.models.device.trigger import BaseTriggerModel
from pygfdrivers.common.models.infrastructure.config import BaseConfigDeviceModel

from pygfdrivers.princeton_instruments.models.sensor import PrincetonSensorConfig
from pygfdrivers.princeton_instruments.models.capture import PrincetonCaptureConfig


class PrincetonTriggerConfig(BaseTriggerModel):
    pass


class PrincetonCameraInfo(BaseDeviceModel):
    pass


class PrincetonCameraConfigModel(BaseConfigDeviceModel):
    device: PrincetonCameraInfo = Field(
        default_factory=lambda: PrincetonCameraInfo(),
        validation_alias=AliasChoices('camera', 'device', 'camera_info', 'camera_settings', 'device_settings')
    )
    capture: PrincetonCaptureConfig = Field(
        default_factory=lambda: PrincetonCaptureConfig(),
        validation_alias=AliasChoices('capture', 'capture_settings')
    )
    trigger: PrincetonTriggerConfig = Field(
        default_factory=lambda: PrincetonTriggerConfig(),
        validation_alias=AliasChoices('trigger', 'trigger_settings')
    )
    sensor: PrincetonSensorConfig = Field(
        default_factory=lambda: PrincetonSensorConfig(),
        validation_alias=AliasChoices('sensor', 'sensor_settings')
    )
