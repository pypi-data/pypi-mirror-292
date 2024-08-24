from pydantic import BaseModel, Field, AliasChoices
from typing import List, Union


class BaseSourceModel(BaseModel):
    source_name: str = Field(
        default=None,
        alias='name',
        validation_alias=AliasChoices('source_name', 'name')
    )
    source_id: str = Field(
        default=None,
        alias='id',
        validation_alias=AliasChoices('source_id', 'id')
    )


class BaseSourceDataModel(BaseModel):
    bytes_to_volt: float = Field(
        default=None,
        alias='bytes_to_volt',
        validation_alias=AliasChoices('bytes_to_volt', 'volt_conversion_factor', 'volt_multiplier'))
    raw_data: List[Union[bytes, List[bytes], List]] = Field(
        default_factory=lambda: list(),
        alias='raw_data',
        validation_alias=AliasChoices('raw_data', 'raw_values', 'byte_values')
    )
    volt_values: List[Union[float, List[float], List]] = Field(
        default_factory=lambda: list(),
        alias='volt_values',
        validation_alias=AliasChoices('volt_values', 'volt_data', 'voltage')
    )
