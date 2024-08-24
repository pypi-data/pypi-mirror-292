from typing import List, Dict
from pydantic import Field, BaseModel, AliasChoices
from typing import List, Dict


class BaseCameraCaptureModel(BaseModel):
    rois: List[Dict[str, int]] = Field(
        default=None,
        alias='rois',
        validation_alias=AliasChoices('rois', 'Rois', 'roi_array')
    )
    adc_gain: int = Field(
        default=None,
        alias='gain',
        validation_alias=AliasChoices('gain', 'adc_gain', 'ADC_gain', 'EM_gain')
    )
    adc_speed: float = Field(
        default=None,
        alias='adc_speed',
        validation_alias=AliasChoices('adc_speed', 'speed')
    )
    time_exposure: float = Field(
        default=None,
        alias='exposure_time',
        validation_alias=AliasChoices('exposure_time', 'time_exposure')
    )
    time_stamps: int = Field(
        default=None,
        alias='time_stamps',
        validation_alias=AliasChoices('time_stamps', 'time_stamping')
    )
    shutter_close_delay: float = Field(
        default=None,
        alias='shutter_close_delay',
        validation_alias=AliasChoices('shutter_close_delay', 'shutter_closing_delay')
    )
    shutter_open_delay: float = Field(
        default=None,
        alias='shutter_open_delay',
        validation_alias=AliasChoices('shutter_open_delay', 'shutter_opening_delay')
    )
    readout_count: int = Field(
        default=None,
        alias='readout_count',
        validation_alias=AliasChoices('readout_count', 'count')
    )
    vertical_shift_rate: float = Field(
        default=None,
        alias='vertical_shift_rate',
        validation_alias=AliasChoices('vertical_shift_rate', 'shift_rate')
    )
    pixel_format: str = Field(
        default=None,
        alias='pixel_format',
        validation_alias=AliasChoices('pixel_format', 'data_format')
    )
