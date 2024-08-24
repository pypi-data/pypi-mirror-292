from pydantic import AliasChoices, Field

from pygfdrivers.common.models.device.channel import BaseChannelModel
from pygfdrivers.keysight.models.source import KeysightSourceModel, KeysightSourceDataModel


class KeysightChannelModel(BaseChannelModel, KeysightSourceModel):
    ch_bandwidth: float = Field(
        default=25e6,
        alias='bandwidth',
        validation_alias=AliasChoices('ch_bandwidth', 'bandwidth')
    )
    ch_bwlimit: bool = Field(
        default=False,
        alias='bwlimit',
        validation_alias=AliasChoices('ch_bwlimit', 'bwlimit')
    )
    ch_impedance: str = Field(
        default='onemeg',
        alias='input_impedance',
        validation_alias=AliasChoices('ch_impedance', 'impedance')
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


class KeysightChannelDataModel(KeysightChannelModel, KeysightSourceDataModel):
    pass
