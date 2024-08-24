from pydantic import Field, AliasChoices

from pygfdrivers.common.models.camera.capture import BaseCameraCaptureModel


class PrincetonCaptureConfig(BaseCameraCaptureModel):
    adc_bit_depth: int = Field(
        default=None,
        alias='adc_bit_depth',
        validation_alias=AliasChoices('adc_bit_depth', 'bit_depth')
    )
    adc_analog_gain: str = Field(
        default=None,
        alias='adc_analog_gain',
        validation_alias=AliasChoices('adc_analog_gain', 'analog_gain')
    )
    adc_quality: str = Field(
        default=None,
        alias='adc_quality',
        validation_alias=AliasChoices('adc_quality', 'AdcQuality')
    )
    readout_mode: int = Field(
        default=None,
        alias='readout_mode',
        validation_alias=AliasChoices('readout_control_mode', 'readout_mode')
    )
    time_stamp_bit_depth: int = Field(
        default=None,
        alias='time_stamp_bit_depth',
        validation_alias='time_stamp_bit_depth'
    )
    frame_tracking_bit_depth: int = Field(
        default=None,
        alias='frame_tracking_bit_depth',
        validation_alias=AliasChoices('frame_tracking_bit_depth', 'tracking_bit_depth')
    )
    shutter_delay_resolution: float = Field(
        default=None,
        alias='shutter_delay_resolution',
        validation_alias=AliasChoices('shutter_delay_resolution', 'delay_resolution')
    )
    shutter_timing_mode: str = Field(
        default=None,
        alias='shutter_timing_mode',
        validation_alias=AliasChoices('shutter_timing_mode', 'shutter_mode')
    )
    normalize_orientation: bool = Field(
        default=None,
        alias='normalize_orientation',
        validation_alias=AliasChoices('normalize_orientation', 'normalize')
    )
    invert_output_signal: bool = Field(
        default=None,
        alias='invert_output_signal',
        validation_alias=AliasChoices('invert_output_signal', 'invert_output')
    )
    disable_data_formatting: bool = Field(
        default=None,
        alias='disable_data_formatting',
        validation_alias=AliasChoices('disable_data_formatting', 'disable_formatting')
    )
    track_frames: bool = Field(
        default=None,
        alias='track_frames',
        validation_alias='track_frames'
    )
    output_signal: str = Field(
        default=None,
        alias='output_signal',
        validation_alias=AliasChoices('output_signal', 'signal_output')
    )
    time_stamp_resolution: int = Field(
        default=None,
        alias='time_stamp_resolution',
        validation_alias='time_stamp_resolution'
    )
