from pydantic import BaseModel, Field, AliasChoices
from typing import Union

class BaseConfigModel(BaseModel):
    config_id: Union[str, int] = Field(
        default=None,
        validation_alias=AliasChoices('config_id', 'config_name','configuration_name')
    )

    config_type: str = Field(
        default= None,
        validation_alias=AliasChoices('config_type', 'configuration_type')
    )
    
    config_enabled: bool = Field(
        default=True,
        alias='enabled',
        validation_alias=AliasChoices('enabled', 'active', 'online')
    )
class BaseConfigDeviceModel(BaseConfigModel):
    handler_type: str = Field(
        default='device',
        alias='handler',
        validation_alias=AliasChoices('device_handler','handler','handler_type', 'handler_key')
    )