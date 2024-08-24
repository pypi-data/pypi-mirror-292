from pydantic import Field, BaseModel, AliasChoices


class BaseCameraSensorModel(BaseModel):
    sensor_width: int = Field(
        default=None,
        alias='width',
        validation_alias=AliasChoices('sensor_width', 'width')
    )
    sensor_height: int = Field(
        default=None,
        alias='height',
        validation_alias=AliasChoices('sensor_height', 'height')
    )
    mask_height: int = Field(
        default=None,
        alias='mask_height',
        validation_alias=AliasChoices('sensor_mask_height', 'mask_height')
    )
    