from typing import Union
from pydantic import BaseModel, Field, AliasChoices


class Acq480ChannelModel(BaseModel):
    ch_invert: bool = Field(
        default=False,
        alias='inverted',
        validation_alias=AliasChoices('ch_invert', 'inverted', 'invert')
    )
    ch_hpf: Union[str, bool] = Field(
        default=False,
        alias='high_pass_filtered',
        validation_alias=AliasChoices('ch_hpf', 'high_pass_filtered', 'hpf')
    )
    ch_lfns: bool = Field(
        default=False,
        alias='low_freq_noise_surpressed',
        validation_alias=AliasChoices('ch_lfns', 'low_freq_noise_surpressed', 'lfns')
    )
    ch_50r: bool = Field(
        default=False,
        alias='50r_terminated',
        validation_alias=AliasChoices('ch_50r', '50r_terminated', 't50r')
    )


class Acq480SiteModel(BaseModel):
    master_reset: bool = Field(
        default=False,
        validation_alias=AliasChoices('master_reset', 'en_master_resest', 'enable_reset')
    )
    all_gain: int = Field(
        default=None,
        alias='set_all_ch_gains',
        validation_alias=AliasChoices('all_gain', 'all_ch_gains', 'global_gain_setting')
    )
    all_lfns: bool = Field(
        default=None,
        alias='enable_all_ch_lfns',
        validation_alias=AliasChoices('all_lfns', 'all_ch_lfns', 'global_lfns_setting')
    )
    all_50r: bool = Field(
        default=None,
        alias='enable_all_ch_50r',
        validation_alias=AliasChoices('all_50r', 'all_ch_50r', 'global_ch_50r_setting')
    )


