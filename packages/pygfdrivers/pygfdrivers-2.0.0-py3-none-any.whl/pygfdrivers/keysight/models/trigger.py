from pydantic import AliasChoices, Field

from pygfdrivers.common.models.device.trigger import BaseTriggerModel


class KeysightTriggerModel(BaseTriggerModel):
    # Main trigger fields
    trig_holdoff: float = Field(
        default=None,
        alias='holdoff',
        validation_alias=AliasChoices('trig_holdoff', 'holdoff')
    )
    trig_sweep: str = Field(
        default='normal',
        alias='sweep_mode',
        validation_alias=AliasChoices('trig_sweep', 'sweep')
    )

    # Edge Trigger Mode Fields
    trig_coupling: str = Field(
        default='ac',
        alias='coupling',
        validation_alias=AliasChoices('trig_coupling', 'coupling')
    )
    trig_reject: str = Field(
        default='off',
        alias='reject_setting',
        validation_alias=AliasChoices('trig_reject', 'reject')
    )

    # External Trigger Source Fields
    trig_gain: float = Field(
        default=1.0,
        alias='gain',
        validation_alias=AliasChoices('trig_gain', 'trig_probe')
    )
    trig_range: float = Field(
        default=8.0,
        alias='v_range',
        validation_alias=AliasChoices('trig_range')
    )
