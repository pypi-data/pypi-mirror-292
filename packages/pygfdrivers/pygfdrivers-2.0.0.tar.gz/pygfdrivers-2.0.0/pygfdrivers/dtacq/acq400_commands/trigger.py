from logging import getLogger
from typing import TYPE_CHECKING

# custom packages
from pygfdrivers.dtacq.util.utilities import pv

if TYPE_CHECKING:
    from pygfdrivers.dtacq.dtacq_scope import DtacqScope


class DtacqTrigger:
    def __init__(self, scope: 'DtacqScope') -> None:
        self.log = getLogger(__name__)

        self.scope = scope
        self.master_site = self.scope.master_site
        self.motherboard = self.scope.motherboard

    def init(self):
        raise NotImplementedError

    @property
    def trig_source(self) -> str:
        _trig_source = pv(self.master_site.get_knob('TRG_DX')).lower()
        self.log.debug(f"trig_source: {'internal' if _trig_source == 'd1' else 'external'}")
        return _trig_source

    @trig_source.setter
    def trig_source(self, source: str) -> None:
        source = source.lower()
        trig_source_map = {'external': 'd0', 'internal': 'd1'}
        trig_sources = list(trig_source_map.keys())

        try:
            if source not in trig_sources:
                self.log.warning(f"trig_source '{source}' not in '{trig_sources}', defaulted to 'internal'.")
                source = 'internal'

            self.log.debug(f"Setting trig_source to '{source}'.")
            self.master_site.set_knob('TRG_DX', trig_source_map[source])
        except Exception as e:
            self.log.error(f"Setting trigger source encountered error: {e}")

    @property
    def trig_slope(self) -> str:
        _trig_slope = pv(self.master_site.get_knob('TRG_SENSE')).lower()
        self.log.debug(f"trig_slope: {_trig_slope}")
        return _trig_slope

    @trig_slope.setter
    def trig_slope(self, slope: str) -> None:
        slope = slope.lower()
        trig_slopes = ['rising', 'falling']

        try:
            if slope not in trig_slopes:
                self.log.warning(f"trig_slope '{slope}' not in '{trig_slopes}', defaulted to 'rising'")
                slope = 'rising'

            self.log.debug(f"Setting trig_slope to '{slope}'")
            self.master_site.set_knob('TRG_SENSE', slope)
        except Exception as e:
            self.log.error(f"Setting trigger edge encountered error: {e}")
