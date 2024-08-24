from acq400_hapi.acq400 import Acq400

from pygfdrivers.dtacq.util.utilities import pv, int_pv
from pygfdrivers.dtacq.site_modules.base_site import BaseSite
from pygfdrivers.dtacq.models.scope_config import DtacqScopeConfigModel


arg_maps = {
    'v_range_to_gain_map' : {'10V': 1, '1V': 10, '0.1V': 100, '0.01V': 1000},
    'v_range_map' : {10.0: '10V', 1.0: '1V', 0.1: '0.1V', 0.01: '0.01V'}
}


class ACQ425(BaseSite):
    def __init__(self, dtacq: Acq400 = None, config: DtacqScopeConfigModel = None) -> None:
        super().__init__(dtacq, config)

        self.bit_depth = 16
        self.coupling = 'DC'
        self.impedance = 1_000_000
        self.max_samples = 100_000
        self.input_type = 'Differential'

    # ------------------------------------------------------------------------------------
    # Site Configuration Methods
    # ------------------------------------------------------------------------------------

    @property
    def clk_source(self) -> str:
        _clk_source = pv(self.master_site.get_knob('CLK_DX')).lower()
        self.log.debug(f"clk_source: {'internal' if _clk_source == 'd0' else 'motherboard'}")
        return _clk_source

    @clk_source.setter
    def clk_source(self, source: str) -> None:
        source = source.lower()
        clk_source_map = {'external': 'd0', 'motherboard': 'd1'}
        clk_sources = list(clk_source_map.keys())

        if source not in clk_sources:
            self.log.warning(f"clk_source '{source}' not in '{clk_sources}', defaulted to 'motherboard'.")
            source = 'motherboard'

        try:
            self.log.debug(f"Setting clk_source to '{source}'.")
            self.master_site.set_knob('CLK_DC', clk_source_map[source])
        except Exception as e:
            self.log.warning(f"Setting clock source encountered error: {e}")

    @property
    def clk_div(self) -> int:
        _clk_div = int_pv(self.master_site.get_knob('CLKDIV'))
        return _clk_div

    @clk_div.setter
    def clk_div(self, clk_div: int) -> None:

        if clk_div <= 0:
            self.log.warning("Clock division cannot be 0 or negative, defaulted to 1.")
            clk_div = 1

        try:
            self.log.debug(f"Setting clock division to '{clk_div}'...")
            self.master_site.set_knob('CLKDIV', clk_div)
        except Exception as e:
            self.log.error(f"Setting clock division encountered error: {e}")

    # ------------------------------------------------------------------------------------
    # Channel Configuration Methods
    # ------------------------------------------------------------------------------------

    @property
    def ch_gain(self) -> int:
        v_range = pv(self.site.get_knob(f"GAIN_{self.site_ch}"))
        _ch_probe = arg_maps['v_range_to_gain_map'][v_range]
        return _ch_probe

    @ch_gain.setter
    def ch_gain(self, gain: int) -> None:
        gains = list(arg_maps['v_range_to_gain_map'].values())

        if gain not in gains:
            self.log.warning(f"probe '{gain}' not in valid_opts '{gains}', default to 1.")
            gain = 1

        try:
            self.site.set_knob(f"GAIN_{self.site_ch}", gain)
        except Exception as e:
            self.log.error(f"Setting channel probe encountered error: {e}")

    @property
    def ch_range(self) -> float:
        _ch_range = pv(self.site.get_knob(f"GAIN_{self.site_ch}")).rstrip('V')
        _ch_range = float(_ch_range)
        return _ch_range

    @ch_range.setter
    def ch_range(self, v_range: float) -> None:
        v_ranges = list(arg_maps['v_range_map'].keys())

        if v_range not in v_ranges:
            self.log.warning(f"v_range '{v_range}' not in valid_opts '{v_ranges}', default to 10V")
            v_range = 10.0

        try:
            self.site.set_knob(f"GAIN_{self.site_ch}", arg_maps['v_range_map'][v_range])
        except Exception as e:
            self.log.error(f"Setting channel voltage range encountered error: {e}")
