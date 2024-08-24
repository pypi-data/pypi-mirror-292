from pydantic import Field, AliasChoices

from pygfdrivers.common.models.infrastructure.config import BaseConfigModel

class BaseServerInfo(BaseConfigModel):
    server_host: str = Field(
        default=None,
        alias='host',
        validation_alias=AliasChoices('host', 'host_ip'))
    server_port: int = Field(
        default=None,
        alias='port',
        validation_alias=AliasChoices('port', 'port_num'))
    server_header: int = Field(
        default=None,
        alias='header'
    )
    server_format: str = Field(
        default=None,
        alias='format'
    )
    server_delimiter: str = Field(
        default= None,
        alias= 'delimeter',
        validation_alias=AliasChoices('server_delimiter', 'delimiter', 'termination_string')
    )
    heartbeat: int = Field(
        default=120,
        alias='heartbeat',
        validation_alias=AliasChoices('heartbeat_interval', 'heartbeat_time'))
    
    server_disconnect_msg: str = Field(
        default=None,
        alias='disconnect_msg'
    )

    log_path: str = Field(
        default=None,
        alias='log_path',
        validation_alias=AliasChoices('log_path', 'log_file_path', 'log_save_path')
    )


class BaseServerModel(BaseConfigModel):
    server: BaseServerInfo = Field(
        default_factory=lambda: BaseServerInfo(),
        validation_alias=AliasChoices('server', 'server_settings')
    )