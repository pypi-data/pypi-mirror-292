from pydantic import Field, AliasChoices

from pygfdrivers.common.models.device.channel import BaseChannelModel
from pygfdrivers.common.models.device.source import BaseSourceDataModel


class LecroyChannelModel(BaseChannelModel):
    ch_bwlimit: bool = Field(
        default=False,
        alias='bwlimit',
        validation_alias=AliasChoices('ch_bwlimit', 'bwlimit')
    )
    ch_invert: bool = Field(
        default=False,
        alias='inverted',
        validation_alias=AliasChoices('ch_invert', 'invert')
    )
    ch_units: str = Field(
        default='volts',
        alias='y_unit',
        validation_alias=AliasChoices('ch_units', 'units')
    )
    ch_skew: float = Field(
        default=None,
        alias='skew',
        validation_alias=AliasChoices('ch_skew', 'skew')
    )


class LecroyChannelDataModel(BaseSourceDataModel, LecroyChannelModel):
    pass
