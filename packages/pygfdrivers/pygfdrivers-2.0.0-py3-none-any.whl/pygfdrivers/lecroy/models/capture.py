from pydantic import Field, AliasChoices

from pygfdrivers.common.models.device.capture import BaseCaptureModel


class LecroyCaptureModel(BaseCaptureModel):
    acq_avg: int  = Field(
        default=None,
        alias='samples_to_avg',
        validation_alias=AliasChoices('acq_avg', 'samples_to_average')
    )
    acq_way: str = Field(
        default='rtime',
        alias='acq_mode',
        validation_alias = AliasChoices('acq_way', 'acq_type', 'type')
    )
    acq_mem_size: str = Field(
        default=None,
        alias='memory_depth',
        validation_alias = AliasChoices('acq_mem_size', 'mem_size', 'mem_depth', 'memory_depth')
    )
    acq_interpolate: bool = Field(
        default=None,
        alias='interpolation',
        validation_alias=AliasChoices('acq_interpolate', 'interpolation')
    )
    time_pos: float = Field(
        default=None,
        alias='time_pos',
        validation_alias=AliasChoices('time_pos', 't_pos')
    )
    wave_points: int = Field(
        default=None,
        alias='num_points',
        validation_alias=AliasChoices('wave_points', 'num_points')
    )
    wave_decimation: int = Field(
        default=None,
        alias='sparse_points',
        validation_alias=AliasChoices('wave_decimation', 'sparse_points')
    )
    wave_first_point: int = Field(
        default=None,
        alias='first_point',
        validation_alias=AliasChoices('wave_first_point', 'first_point')
    )
