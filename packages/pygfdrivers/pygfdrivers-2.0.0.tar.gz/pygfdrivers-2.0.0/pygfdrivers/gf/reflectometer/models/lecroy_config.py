from pydantic import AliasChoices, Field

from pygfdrivers.common.models.infrastructure.config import BaseConfigModel 
from pygfdrivers.common.models.device.device import BaseDeviceModel
from typing import Union

class ChannelConfig(BaseConfigModel):
    enabled: str = Field(
        default='ON',
        alias='enabled'
    )
    scale: float = Field(
        default=0.5,
        alias='scale'
    )
    offset: float = Field(
        default=-1.5,
        alias='offset'
    )
    bandwidth_limit: str = Field(
        default='FULL',
        alias='bandwidth_limit'
    )
    coupling: str = Field(
        default='DC',
        alias='coupling'
    )
    impedance: str = Field(
        default='ONEMeg',
        alias='impedance'
    )
    visible: str = Field(
        default='ON',
        alias='visible'
    )

class ScopeConfig(BaseConfigModel):
    ip_address: str = Field(
        default='172.25.226.15H',
        alias='ip_address'
    )
    reset: bool = Field(
        default=False,
        alias='reset'
    )
    acquire_type: str = Field(
        default='normal',
        alias='acquire_type'
    )
    memory_depth: str = Field(
        default='50M',
        alias='memory_depth'
    )
    bit_res: int = Field(
        default=10,
        alias='bit_res'
    )
    trigger_source: str = Field(
        default='c2',
        alias='trigger_source'
    )
    trigger_slope: str = Field(
        default='rising',
        alias='trigger_slope'
    )
    trigger_voltage: float = Field(
        default=0.6,
        alias='trigger_voltage'
    )
    holdoff_mode: str = Field(
        default='OFF',
        alias='holdoff_mode'
    )
    holdoff_time: Union[str, None] = Field(
        default=None,
        alias='holdoff_time'
    )
    holdoff_events: Union[str, None] = Field(
        default=None,
        alias='holdoff_events'
    )
    time_scale: float = Field(
        default=5e-3,
        alias='time_scale'
    )
    time_delay: float = Field(
        default=25e-3,
        alias='time_delay'
    )
    data_channels: list = Field(
        default=[1, 2],
        alias='data_channels'
    )
    channels: dict = Field(
        default_factory=lambda: {
            1: ChannelConfig(),
            2: ChannelConfig()
        },
        alias='channels'
    )