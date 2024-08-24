from typing import List
from pydantic import AliasChoices, Field, BaseModel

from pygfdrivers.common.models.device.source import BaseSourceDataModel


class KeysightSourceModel(BaseModel):
    wave_byte_order: str = Field(
        default='msbfirst',
        alias='byte_order',
        validation_alias=AliasChoices('wave_byte_order', 'byte_order')
    )
    wave_format: str = Field(
        default='byte',
        alias='format',
        validation_alias=AliasChoices('wave_format', 'format', 'data_format')
    )
    wave_points: int = Field(
        default= None,
        alias='points_acquired',
        validation_alias=AliasChoices('wave_points', 'points', 'points_acqd')
    )
    wave_points_mode: str = Field(
        default='raw',
        alias='points_mode',
        validation_alias=AliasChoices('wave_points_mode', 'points_mode')
    )
    wave_unsigned: bool = Field(
        default=True,
        alias='unsigned',
        validation_alias=AliasChoices('wave_unsigned', 'unsigned')
    )

    # only available on MXR scope
    wave_stream: bool = Field(
        default=False,
        alias='livestream_source',
        validation_alias=AliasChoices('wave_stream_source', 'stream_source')
    )
    wave_segmented_all: bool = Field(
        default=True,
        alias='download_all_segments',
        validation_alias=AliasChoices('wave_segmented_all', 'segmented_all', 'download_all_segments')
    )


class KeysightSourceDataModel(BaseSourceDataModel):
    wave_type: str = Field(default=None, alias='type')
    wave_xinc: float = Field(default=None, alias='x_inc')
    wave_yinc: float = Field(default=None, alias='y_inc')
    wave_xref: float = Field(default=None, alias='x_ref')
    wave_yref: float = Field(default=None, alias='y_ref')
    wave_xorigin: float = Field(default=None, alias='x_origin')
    wave_yorigin: float = Field(default=None, alias='y_origin')
    wave_segment_count: int = Field(default=None, alias='segments_acquired')
    wave_segment_ttag: List[float] = Field(default_factory=lambda: list(), alias='segment_trigger_times')
