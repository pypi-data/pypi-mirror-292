from pydantic import BaseModel, Field, AliasChoices
from typing import Union


class BaseTriggerModel(BaseModel):
    trig_mode: Union[str, int] = Field(
        default=None,
        alias='mode',
        validation_alias=AliasChoices('trig_mode', 'mode', 'trigger_mode')
    )
    trig_source: str = Field(
        default=None,
        alias='source',
        validation_alias=AliasChoices('trig_source', 'source')
    )
    trig_slope: Union[str, int] = Field(
        default=None,
        alias='slope',
        validation_alias=AliasChoices('trig_slope', 'slope', 'trigger_determination')
    )
    trig_level: float = Field(
        default=None,
        alias='level',
        validation_alias=AliasChoices('trig_level', 'level', 'trigger_level')
    )
