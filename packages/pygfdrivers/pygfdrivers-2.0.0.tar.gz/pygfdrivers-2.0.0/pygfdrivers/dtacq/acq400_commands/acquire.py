from logging import getLogger
from typing import TYPE_CHECKING

# custom packages
from pygfdrivers.dtacq.util.utilities import int_pv, float_pv

if TYPE_CHECKING:
    from pygfdrivers.dtacq.dtacq_scope import DtacqScope


class DtacqAcquire:
    def __init__(self, scope: 'DtacqScope') -> None:
        self.log = getLogger(__name__)

        self.ai_modules = scope.ai_modules
        self.master_site = scope.master_site
        self.motherboard = scope.motherboard
        self.max_samples = scope.max_samples
        self.max_clock = scope.max_clock
        self.min_clock = scope.min_clock

    def init(self):
        raise NotImplementedError

    def set_time_range(self, pre_time: float, post_time: float) -> None:
        max_time_range = self.max_samples * self.acq_srate
        if (pre_time + post_time) > max_time_range:
            pre_time = max_time_range  - post_time

        self.log.debug(f"set_time_range with pre_time '{pre_time}' and post_time '{post_time}'.")
        self.time_pre = pre_time
        self.time_post = post_time

    def set_total_samples(self, pre_samples: int, post_samples: int) -> None:
        if (pre_samples + post_samples) > self.max_samples:
            pre_samples = self.max_samples - post_samples

        self.log.debug(f"set_total_samples with pre_samples '{pre_samples}' and post_samples '{post_samples}'.")
        self.acq_pre_samples = pre_samples
        self.acq_post_samples = post_samples

    @property
    def acq_srate(self) -> float:
        # Use MB_SET clock value with the clock divider from master site because it is not constantly updating
        # in comparison to the actual clock. This allows for more consistent setting of the sample counts,
        # rather than constantly varying by +/- 10 counts.
        _set_clk = float_pv(self.motherboard.get_knob('SIG_CLK_MB_SET'))
        _clk_div = int_pv(self.master_site.get_knob('CLKDIV'))
        _acq_srate = float(_set_clk / _clk_div)
        self.log.debug(f"acq_srate: '{_acq_srate}'")
        return _acq_srate

    @acq_srate.setter
    def acq_srate(self, srate: float) -> None:
        # We always plan to use the ZCLK input, so we never change it.
        try:
            if srate > self.max_clock:
                self.log.warning("Sampling frequency set higher than max frequency, lowered to maximum allowed.")
                srate = self.max_clock

            if srate < self.min_clock:
                for div in range(1, 2000):
                    if srate * div >= self.min_clock:
                        srate *= div
                        self.ai_modules.clk_div = div
                        break

            self.log.debug(f"Setting acq_srate to '{srate}'.")
            self.motherboard.set_knob('SIG_CLK_MB_SET', srate)
        except Exception as e:
            self.log.error(f"Setting sampling frequency encountered error: {e}")

    @property
    def acq_total_samples(self) -> int:
        _acq_total_samples = self.acq_pre_samples + self.acq_post_samples
        self.log.debug(f"acq_total_samples: '{_acq_total_samples}'")
        return _acq_total_samples

    @property
    def acq_pre_samples(self) -> int:
        _acq_pre_samples = int_pv(self.motherboard.get_knob('TRANSIENT_PRE'))
        self.log.debug(f"acq_pre_samples: '{_acq_pre_samples}'")
        return _acq_pre_samples

    @acq_pre_samples.setter
    def acq_pre_samples(self, pre_samples: int) -> None:
        try:
            if pre_samples < 0:
                self.log.warning(f"Pre-sample setting below 0, defaulted to 0.")
                pre_samples = 0
            elif pre_samples > self.max_samples:
                self.log.warning(f"Pre-sample setting above max samples, lowered to max samples.")
                pre_samples = self.max_samples

            self.log.debug(f"Setting acq_pre_samples to '{pre_samples}'.")
            self.motherboard.set_knob('TRANSIENT_PRE', pre_samples)
        except Exception as e:
            self.log.error(f"Setting pre-samples encountered an error: {e}")

    @property
    def acq_post_samples(self) -> int:
        _acq_post_samples = int_pv(self.motherboard.get_knob('TRANSIENT_POST'))
        self.log.debug(f"acq_post_samples: '{_acq_post_samples}'")
        return _acq_post_samples

    @acq_post_samples.setter
    def acq_post_samples(self, post_samples: int) -> None:
        try:
            if post_samples < 0:
                self.log.warning(f"acq_post_samples <'0', default to '0'.")
                post_samples = 0
            elif post_samples > self.max_samples:
                self.log.warning(f"acq_post_samples >'{self.max_samples}', default to '{self.max_samples}'.")
                post_samples = self.max_samples

            self.log.debug(f"Setting acq_post_samples to '{post_samples}'.")
            self.motherboard.set_knob('TRANSIENT_POST', post_samples)
        except Exception as e:
            self.log.error(f"Setting post-samples encountered an error: {e}")

    @property
    def time_range(self) -> float:
        _time_range = self.time_pre + self.time_post
        self.log.debug(f"time_range: '{_time_range}'")
        return _time_range

    @property
    def time_pre(self) -> float:
        _time_pre = float(self.acq_post_samples / self.acq_srate)
        self.log.debug(f"time_pre: '{_time_pre}'")
        return _time_pre

    @time_pre.setter
    def time_pre(self, pre_time: float) -> None:
        self.log.debug(f"Setting time_pre to '{pre_time}'.")
        self.acq_pre_samples = int(pre_time * self.acq_srate)

    @property
    def time_post(self) -> float:
        _time_post = float(self.acq_post_samples / self.acq_srate)
        self.log.debug(f"time_post: '{_time_post}'")
        return _time_post

    @time_post.setter
    def time_post(self, post_time: float) -> None:
        self.log.debug(f"Setting time_post to '{post_time}'.")
        self.acq_post_samples = int(post_time * self.acq_srate)
