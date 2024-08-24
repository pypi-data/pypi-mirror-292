from pygfdrivers.common.visa.visa_cmd import BaseVisaScopeCommand
from pygfdrivers.common.visa.visa_scope import VisaScope
from pygfdrivers.common.util.utilities import has_prop, has_setter
from pygfdrivers.gf.models.digitizer_config import GFTriggerModel


class GFDigitizerTrigger(BaseVisaScopeCommand):
    def __init__(self, visa_scope: VisaScope) -> None:
        super().__init__(visa_scope)

    def apply_trig_config(self, config: GFTriggerModel) -> None:
        try:   
            for field, setting in config.dict().items():
                if has_setter(self, field) and setting is not None:
                    setattr(self, field, setting)
        except Exception as e:
            self.log.error(f"Applying trigger configuration encountered error: {e}")

    def fetch_trig_config(self, config: GFTriggerModel):
        try:
            for field in self.trig_fields:
                if has_prop(self, field):
                    setattr(config, field, getattr(self, field))
        except Exception as e:
            self.log.error(f"Fetching trigger configuration encountered error: {e}")

    def format_trig_level(self, level):
        try:
            level = int(level)
            if (0 <= level <= 100):
                return str(level)
            else:
                self.log.error(f"Incorrect data format for trigger level input")
        except Exception as e:
            self.log.error(f"Incorrect data format for trigger level input: {e}")

    @property
    def trig_level(self) -> int:
        return self._trig_level

    @trig_level.setter
    def trig_level(self, level: int) -> None:
        self._trig_level = level
        level = self.format_trig_level(level)
        self.query(cmd = f"set_pwm_value pwm=triglevel value={level}")