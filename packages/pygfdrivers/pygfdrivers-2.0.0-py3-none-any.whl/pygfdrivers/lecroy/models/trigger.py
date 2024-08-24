from pydantic import Field, AliasChoices

from pygfdrivers.common.models.device.trigger import BaseTriggerModel


class LecroyTriggerModel(BaseTriggerModel):
    trig_coupling: str = Field(
        default='ac',
        alias='coupling',
        validation_alias=AliasChoices('trig_coupling', 'coupling')
    )
    trig_sweep: str = Field(
        default='normal',
        alias='sweep',
        validation_alias=AliasChoices('trig_sweep', 'sweep')
    )
