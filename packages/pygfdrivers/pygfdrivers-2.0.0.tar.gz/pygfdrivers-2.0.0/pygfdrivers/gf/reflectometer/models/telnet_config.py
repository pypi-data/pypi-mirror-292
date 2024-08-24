from pydantic import AliasChoices, Field

from pygfdrivers.common.models.infrastructure.config import BaseConfigModel

class TelnetCommands(BaseConfigModel):
    before_shot: list = Field(
        default=['status', 'exit'],
        alias='before_shot'
    )
    after_shot: list = Field(
        default=['status', 'exit'],
        alias='after_shot'
    )


class TelnetConfig(BaseConfigModel):
    enabled: bool = Field(
        default=False,
        alias='enabled'
    )
    host: str = Field(
        default='172.25.226.12',
        alias='host'
    )
    port: int = Field(
        default=5050,
        alias='port'
    )
    start_freq: float = Field(
        default=17.5e6,
        alias='start_freq'
    )
    stop_freq: float = Field(
        default=26.5e6,
        alias='stop_freq'
    )
    sweep_time: int = Field(
        default=2,
        alias='sweep_time'
    )
    trig_enable: bool = Field(
        default=True,
        alias='trig_enable'
    )
    mode: str = Field(
        default='sweep',
        alias='mode'
    )
    telnet_commands: TelnetCommands = Field(
        default=TelnetCommands(),
        alias='telnet_commands'
    )

 