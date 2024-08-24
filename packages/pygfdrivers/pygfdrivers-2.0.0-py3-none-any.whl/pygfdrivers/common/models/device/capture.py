from typing import Union
from pydantic import BaseModel, Field, AliasChoices


class BaseCaptureModel(BaseModel):
    time_scale: float = Field(
        default=None,
        alias='t_div',
        validation_alias=AliasChoices('time_scale', 't_scale', 'time_div', 't_div')
    )
    time_range: float = Field(
        default=None,
        alias='t_total',
        validation_alias=AliasChoices('time_range', 't_range', 't_total', 'total_time')
    )
    time_zero: float = Field(
        default=None,
        alias='t_zero',
        validation_alias=AliasChoices('time_zero', 't_zero', 't_offset')
    )
    acq_srate: Union[int, float] = Field(
        default=None,
        alias='sample_freq',
        validation_alias=AliasChoices('acq_srate', 'srate', 'sample_rate', 'sample_freq')
    )

    acq_count: int  = Field(
        default=None,
        alias='samples_to_avg',
        validation_alias=AliasChoices('acq_count', 'samples_to_average', 'samples_to_avg')
    )

    # only implemented on dtacq devices
    time_pre: float = Field(
        default=None,
        alias='pre_time',
        validation_alias=AliasChoices('time_pre', 't_pre',  'pre_time', 'time_before_trigger')
    )
    time_post: float = Field(
        default=None,
        alias='post_time',
        validation_alias=AliasChoices('time_post', 't_post', 'post_time', 'time_after_trigger')
    )
    acq_pre_samples: Union[int, float] = Field(
        default=None,
        alias='pre_samples',
        validation_alias=AliasChoices('acq_pre_samples', 'pre_samples', 'pre_num_points')
    )
    acq_post_samples: Union[int, float] = Field(
        default=None,
        alias='post_samples',
        validation_alias=AliasChoices('acq_post_samples', 'post_samples', 'post_num_points')
    )
    acq_total_samples: Union[int, float] = Field(
        default=None,
        alias='num_points',
        validation_alias=AliasChoices('acq_total_samples', 'total_samples',  'num_points')
    )
