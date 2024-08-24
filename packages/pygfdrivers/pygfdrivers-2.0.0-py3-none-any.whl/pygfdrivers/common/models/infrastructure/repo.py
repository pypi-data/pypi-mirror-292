from pydantic import Field, AliasChoices

from pygfdrivers.common.models.infrastructure.config import BaseConfigModel

class BaseRepoModel(BaseConfigModel):
    repo_name: str = Field(
        default=None,
        alias='name',
        validation_alias=AliasChoices('name', 'repo_name'))
    repo_url: str = Field(
        default=None,
        alias='url',
        validation_alias=AliasChoices('url', 'repo_url'))
    repo_branch: str = Field(
        default=None,
        alias='branch',
        validation_alias=AliasChoices('branch', 'repo_branch'))
    repo_root_dir: str = Field(
        default=None,
        alias='root_dir',
        validation_alias=AliasChoices('root_config_dir', 'root_dir', 'config_dir'))
