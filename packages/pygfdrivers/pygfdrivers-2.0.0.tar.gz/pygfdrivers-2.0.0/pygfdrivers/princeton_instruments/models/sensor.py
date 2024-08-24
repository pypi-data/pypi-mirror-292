from typing import List
from pydantic import Field, AliasChoices

from pygfdrivers.common.models.camera.sensor import BaseCameraSensorModel


class PrincetonSensorConfig(BaseCameraSensorModel):
    sensor_margin: List[int] = Field(
        default=None,
        alias='margin',
        validation_alias=AliasChoices('sensor_margin', 'margin')
    )
    mask_margin: List[int] = Field(
        default=None,
        alias='mask_margin',
        validation_alias=AliasChoices('sensor_mask_margin', 'mask_margin')
    )
    kinetics_height: int = Field(
        default=None,
        alias='kinetics_height',
        validation_alias=AliasChoices('kinetics_height', 'kinetics_window', 'kinetics_window_height')
    )
    clean_section_height: int = Field(
        default=None,
        alias='clean_section_height',
        validation_alias=AliasChoices('clean_section_height', 'sensor_clean_section_height')  
    )
    clean_section_height_count: int = Field(
        default=None,
        alias='clean_section_height_count',
        validation_alias=AliasChoices('clean_section_height_count', 'sensor_clean_section_height_count')
    )
    clean_cycle_count: int = Field(
        default=None,
        alias='clean_cycle_count',
        validation_alias=AliasChoices('clean_cycle_count', 'sensor_clean_cycle_count')        
    )
    clean_cycle_height: int = Field(
        default=None,
        alias='clean_cycle_height',
        validation_alias=AliasChoices('clean_cycle_height', 'sensor_clean_cycle_height')        
    )
    clean_serial_register: bool = Field(
        default=None,
        alias='clean_serial_register',
        validation_alias=AliasChoices('clean_serial_register', 'serial_register')
    )
    clean_until_trigger: bool = Field(
        default=None,
        alias='clean_until_trigger',
        validation_alias=AliasChoices('clean_until_trigger', 'sensor_clean_until_trigger')
    )
    clean_before_exposure: bool = Field(
        default=None,
        alias='clean_before_exposure',
        validation_alias=AliasChoices('clean_before_exposure', 'sensor_clean_before_exposure')
    )
    sensor_cooling_fan: bool = Field(
        default=None,
        alias='sensor_cooling_fan',
        validation_alias=AliasChoices('disable_cooling_fan', 'sensor_cooling_fan')
    )
