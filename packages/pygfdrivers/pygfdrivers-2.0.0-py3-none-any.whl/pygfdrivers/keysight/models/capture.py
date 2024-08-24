from pydantic import AliasChoices, Field

from pygfdrivers.common.models.device.capture import BaseCaptureModel


class KeysightCaptureModel(BaseCaptureModel):
    acq_complete: int  = Field(
        default=100,
        alias='complete',
        validation_alias=AliasChoices('acq_complete', 'percent_completion')
    )
    acq_count: int  = Field(
        default=None,
        alias='samples_to_avg',
        validation_alias=AliasChoices('acq_count', 'samples_to_average')
    )
    acq_segment_count: int = Field(
        default=1,
        alias='segment_to_acq',
        validation_alias=AliasChoices('acq_segment_count', 'segments', 'segments_to_acquire')
    )
    acq_mode: str = Field(
        default=None,
        alias='acq_mode',
        validation_alias = AliasChoices('acq_mode', 'capture_mode')
    )
    acq_type: str = Field(
        default='normal',
        alias='acq_type',
        validation_alias=AliasChoices('acq_type', 'capture_type')
    )
    time_mode: str = Field(
        default='main',
        alias='time_mode',
        validation_alias = AliasChoices('time_mode', 't_mode')
    )
    time_pos: float = Field(
        default=None,
        alias='time_pos',
        validation_alias=AliasChoices('time_pos', 't_pos')
    )
    time_ref: str = Field(
        default='center',
        alias='time_ref',
        validation_alias=AliasChoices('time_ref', 't_ref')
    )

    # Read-only Fields
    acq_points: int = Field(
        default=None,
        alias='points_acqd',
    )

    # mxr only
    acq_srate_auto: bool = Field(
        default=None,
        alias='auto_sample_rate',
        validation_alias=AliasChoices('acq_srate_auto', 'auto_sample_rate', 'auto_sample_freq')
    )
