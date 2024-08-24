from pydantic import Field, AliasChoices
from pygfdrivers.common.models.device.source import BaseSourceModel


class BaseChannelModel(BaseSourceModel):
    ch_coupling: str = Field(
        default=None,
        alias='coupling',
        validation_alias=AliasChoices('ch_coupling', 'coupling')
    )
    ch_gain: float = Field(
        default=None,
        alias='gain',
        validation_alias=AliasChoices('ch_gain', 'gain', 'probe', 'attenuation', 'attn')
    )
    ch_scale: float = Field(
        default=None,
        alias='v_div',
        validation_alias=AliasChoices('ch_scale', 'y_scale', 'y_div', 'v_scale', 'v_div')
    )
    ch_range: float = Field(
        default=None,
        alias='v_range',
        validation_alias=AliasChoices('ch_range', 'y_range', 'v_range', 'vpp')
    )
    ch_offset: float = Field(
        default=None,
        alias='dc_offset',
        validation_alias=AliasChoices('ch_offset', 'y_offset', 'v_offset', 'dc_offset')
    )
