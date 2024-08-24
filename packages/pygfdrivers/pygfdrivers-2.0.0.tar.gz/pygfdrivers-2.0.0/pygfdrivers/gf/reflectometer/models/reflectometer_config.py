from pydantic import AliasChoices, Field, BaseModel

from pygfdrivers.common.models.infrastructure.config import BaseConfigModel 
from pygfdrivers.gf.reflectometer.models.lecroy_config import ScopeConfig
from pygfdrivers.gf.reflectometer.models.telnet_config import TelnetConfig
from pygfdrivers.gf.reflectometer.models.rigol_config import GeneratorConfig

from pygfdrivers.common.models.infrastructure.config import BaseConfigDeviceModel 
from pygfdrivers.common.models.device.device import BaseDeviceModel


class ReflectometerInfo(BaseDeviceModel):
    pass

class GeneralConfig(BaseConfigModel):
    debug: bool = Field(
        default=False,
        alias='debug'
    )
    use_shot_number: bool = Field(
        default=False,
        alias='use_shot_number'
    )
    location: str = Field(
        default='CURRENT_DIRECTORY',
        alias='location'
    )
    subdirectory: str = Field(
        default='reflectometer',
        alias='subdirectory'
    )
    data_filename: str = Field(
        default='scope_data',
        alias='data_filename'
    )
    metadata_filename: str = Field(
        default='scope_metadata',
        alias='metadata_filename'
    )

class DataConfig(BaseConfigModel):
    t_zero: str = Field(
        default='start',
        alias='t_zero'
    )
    start_time: float = Field(
        default=0,
        alias='start_time'
    )
    end_time: float = Field(
        default=35.2e-3,
        alias='end_time'
    )

class RawDataConfig(BaseConfigModel):
    t_zero: str = Field(
        default='start',
        alias='t_zero'
    )
    start_time: float = Field(
        default=0,
        alias='start_time'
    )
    end_time: str = Field(
        default='MAX',
        alias='end_time'
    )

class ProcessingConfig(BaseConfigModel):
    number_of_slices: float = Field(
        default=2.5e3,
        alias='number_of_slices'
    )
    slice_length: float = Field(
        default=5e-6,
        alias='slice_length'
    )
    slice_period: float = Field(
        default=10e-6,
        alias='slice_period'
    )
    trigger_data_channel: int = Field(
        default=2,
        alias='trigger_data_channel'
    )


class ReflectometerConfig(BaseDeviceModel, BaseConfigDeviceModel):
    device: ReflectometerInfo = Field(
        default_factory=lambda: ReflectometerInfo(),
        validation_alias=AliasChoices('scope', 'scope_settings', 'scope_info')
    )
    general: GeneralConfig = Field(
        default_factory=lambda: GeneralConfig(),
        alias='general',
        validation_alias=AliasChoices('general', 'general_settings')
    )
    data: DataConfig = Field(
        default_factory=lambda: DataConfig(),
        alias='data',
        validation_alias=AliasChoices('data', 'data_settings')
    )
    raw_data: RawDataConfig = Field(
        default_factory=lambda: RawDataConfig(),
        alias='raw_data',
        validation_alias=AliasChoices('raw_data', 'raw_data_settings')
    )
    processing: ProcessingConfig = Field(
        default_factory=lambda: ProcessingConfig(),
        alias='processing',
        validation_alias=AliasChoices('processing', 'processing_settings')
    )
    lecroy: ScopeConfig = Field(
        default_factory=lambda: ScopeConfig(),
        alias='lecroy',
        validation_alias=AliasChoices('lecroy', 'lecroy_settings')
    )
    generator: GeneratorConfig = Field(
        default_factory=lambda: GeneratorConfig(),
        alias='generator',
        validation_alias=AliasChoices('generator', 'generator_settings')
    )
    telnet: TelnetConfig = Field(
        default_factory=lambda: TelnetConfig(),
        alias='telnet',
        validation_alias=AliasChoices('telnet', 'telnet_settings')
    )