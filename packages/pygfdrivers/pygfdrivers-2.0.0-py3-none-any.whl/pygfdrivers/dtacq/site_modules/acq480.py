from typing import Union

from acq400_hapi.acq400 import Acq400

from pygfdrivers.dtacq.site_modules.base_site import BaseSite
from pygfdrivers.dtacq.util.utilities import pv, float_pv, int_pv
from pygfdrivers.dtacq.models.scope_config import DtacqScopeConfigModel


class ACQ480(BaseSite):
    def __init__(self, dtacq: Acq400 = None, config: DtacqScopeConfigModel = None) -> None:
        super().__init__(dtacq, config)

        self.bit_depth = 14
        self.coupling = 'DC'
        self.max_samples = 3_000_000
        self.input_type = 'Single Ended'

    # ------------------------------------------------------------------------------------
    # Site Configuration Methods
    # ------------------------------------------------------------------------------------

    @property
    def master_reset(self) -> bool:
        _master_reset = pv(self.master_site.get_knob(f"ACQ480_MR_EN"))
        _master_reset = bool(int(_master_reset))
        return _master_reset

    @master_reset.setter
    def master_reset(self, state: bool) -> None:
        try:
            self.master_site.set_knob(f"ACQ480_MR_EN", int(state))
        except Exception as e:
            self.log.error(f"Enabling master reset encountered error: {e}")

    # ------------------------------------------------------------------------------------
    # Channel Configuration Methods
    # ------------------------------------------------------------------------------------

    @property
    def ch_invert(self) -> bool:
        _ch_invert = pv(self.master_site.get_knob(f"ACQ480_INVERT_{self.site_ch}")).lower()
        _ch_invert = 'inv' in _ch_invert
        return _ch_invert
    
    @ch_invert.setter
    def ch_invert(self, state: bool) -> None:
        try:
            self.site.set_knob(f"ACQ480_INVERT_{self.site_ch}", int(state))
        except Exception as e:
            self.log.error(f"Setting channel invert encountered error: {e}")

    @property
    def ch_gain(self) -> int:
        _ch_gain = pv(self.master_site.get_knob(f"ACQ480_GAIN_{self.site_ch}"))
        _ch_gain = int(_ch_gain.split()[0])
        return _ch_gain
    
    @ch_gain.setter
    def ch_gain(self, gain: int) -> None:
        gains = [i for i in range(1, 12 + 1)]

        if gain not in gains:
            self.log.warning(f"ch_gain '{gain}' not in valid_opts '{gains}', default to 1dB")
            gain = 1

        try:
            self.site.set_knob(f"ACQ480_GAIN_{self.site_ch}", gain)
        except Exception as e:
            self.log.error(f"Setting channel gain encountered error: {e}")

    @property
    def ch_hpf(self) -> str:
        _ch_hpf = pv(self.master_site.get_knob(f"ACQ480_HPF_{self.site_ch}")).lower()
        return _ch_hpf
    
    @ch_hpf.setter
    def ch_hpf(self, hpf: Union[str, bool]) -> None:
        hpf_settings = ['off', 'k2', 'k3', 'k4', 'k5', 'k6', 'k7', 'k8', 'k9', 'k10']
        hpf = 'off' if isinstance(hpf, bool) and not hpf else None

        if hpf not in hpf_settings or hpf is None:
            self.log.warning(f"ch_hpf '{hpf}' not in valid_opts '{hpf_settings}', default to 'off'.")
            hpf = 'off'

        try:
            self.site.set_knob(f"ACQ480_HPF_{self.site_ch}", hpf.upper())
        except Exception as e:
            self.log.error(f"Setting channel HPF encountered error: {e}")

    @property
    def ch_lfns(self) -> bool:
        _ch_lfns = pv(self.master_site.get_knob(f"ACQ480_LFNS_{self.site_ch}")).lower()
        _ch_lfns = 'on' in _ch_lfns
        return _ch_lfns

    @ch_lfns.setter
    def ch_lfns(self, state: bool) -> None:
        try:
            self.site.set_knob(f"ACQ480_LFNS_{self.site_ch}", int(state))
        except Exception as e:
            self.log.error(f"Setting channel LFNS encountered error: {e}")

    @property
    def ch_impedance(self) -> bool:
        _ch_impedance = pv(self.master_site.get_knob(f"ACQ480_T50R_{self.site_ch}"))
        _ch_impedance = bool(int(_ch_impedance))
        return _ch_impedance

    @ch_impedance.setter
    def ch_impedance(self, state: bool) -> None:
        try:
            self.site.set_knob(f"ACQ480_T50R_{self.site_ch}", int(state))
        except Exception as e:
            self.log.error(f"Setting channel impedance to 50R encountered error: {e}")

    # ------------------------------------------------------------------------------------
    # Read Only Methods
    # ------------------------------------------------------------------------------------

    @property
    def out_srate(self) -> float:
        _out_srate = float_pv(self.master_site.get_knob("ACQ480_OSR"))
        return _out_srate

    @property
    def fpga_decimation(self) -> int:
        _fpga_decimation = int_pv(self.master_site.get_knob("ACQ480_FPGA_DECIM"))
        return _fpga_decimation
