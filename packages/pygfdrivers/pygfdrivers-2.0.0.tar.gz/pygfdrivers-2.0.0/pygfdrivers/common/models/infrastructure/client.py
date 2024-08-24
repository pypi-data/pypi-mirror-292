from pydantic import AliasChoices, Field
from pygfdrivers.common.models.infrastructure.file import BaseFileModel
from pygfdrivers.common.models.infrastructure.config import BaseConfigModel


class BaseClientInfo(BaseFileModel):
    client_name: str = Field(
        default=None,
        alias='name',
        validation_alias=AliasChoices('name', 'client_name')
    )

class BaseClientModel(BaseConfigModel):
    client: BaseClientInfo = Field(
        default_factory=lambda: BaseClientInfo(),
        validation_alias=AliasChoices('client', 'client_settings')
    )