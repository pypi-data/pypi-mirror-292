from pydantic import AliasChoices, Field

from pygfdrivers.common.models.infrastructure.config import BaseConfigModel 

class GeneratorConfig(BaseConfigModel):
    ip_address: str = Field(
        default='172.25.226.15',
        alias='ip_address'
    )
    generator_chn: int = Field(
        default=1,
        alias='generator_chn'
    )
    num_cycles: int = Field(
        default=7000,
        alias='num_cycles'
    )
    burst_mode: str = Field(
        default='TRIG',
        alias='burst_mode'
    )
    trig_source: str = Field(
        default='external',
        alias='trig_source'
    )
    waveform_mode: str = Field(
        default='pulse',
        alias='waveform_mode'
    )
    offset: float = Field(
        default=2.5,
        alias='offset'
    )
    Vpp: float = Field(
        default=4.5,
        alias='Vpp'
    )
    delay: int = Field(
        default=0,
        alias='delay'
    )

    duty_cycle: int = Field(
        default=10,
        alias='duty_cycle'
    )
    lead_time: float = Field(
        default=20e-9,
        alias='lead_time'
    )
    trail_time: float = Field(
        default=20e-9,
        alias='trail_time'
    )
    frequency: float = Field(
        default=200e3,
        alias='frequency'
    )
