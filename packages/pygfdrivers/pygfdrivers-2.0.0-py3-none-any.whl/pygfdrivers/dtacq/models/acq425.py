from pydantic import BaseModel, Field, AliasChoices


class Acq425ChannelModel(BaseModel):
    pass


class Acq425SiteModel(BaseModel):
    clk_source: str = Field(
        default=None,
        alias='clock_source',
        validation_alias=AliasChoices('clk_source', 'clock_source', 'clk_src')
    )
    clk_sense: str = Field(
        default=None,
        alias='clock_sense',
        validation_alias=AliasChoices('clk_sense', 'clock_sense')
    )
    clk_div: int = Field(
        default=None,
        alias='clock_division',
        validation_alias=AliasChoices('clk_div', 'clock_div')
    )
