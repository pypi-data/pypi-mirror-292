from pydantic import BaseModel, AliasChoices, Field


class BaseFileModel(BaseModel):
    file_name: str = Field(
        default=None,
        validation_alias=AliasChoices('file_name'),
    )
    file_format: str = Field(
        default=None,
        validation_alias=AliasChoices('file_format', 'save_format', 'file_type')
    )
    file_save_path: str = Field(
        default=None,
        alias='save_path',
        validation_alias=AliasChoices('save_path', 'save_folder', 'file_path')
    )
    file_backup_save_path: str = Field(
        default=None,
        alias='backup_save_path',
        validation_alias=AliasChoices('backup_save_path', 'back_save_folder', 'backup_file_path')
    )
