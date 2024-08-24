
from pygfdrivers.common.visa.visa_scope import VisaScope
from pygfdrivers.common.visa.visa_cmd import BaseVisaScopeCommand
from pygfdrivers.common.util.utilities import has_prop, has_setter
from pygfdrivers.common.models.device.cmd import create_cmd_class, CmdClassType

from pygfdrivers.keysight.models.capture import KeysightCaptureModel


def init_time_cmds() -> CmdClassType:
    time: CmdClassType = create_cmd_class('Timebase')
    time.add_cmd(key='time_range', cmd=':timebase:range')
    time.add_cmd(key='time_scale', cmd=':timebase:scale')
    time.add_cmd(key='time_pos', cmd=':timebase:position')
    time.add_cmd(key='time_ref', cmd=':timebase:reference', args=['left', 'center', 'right'], default='center')
    return time


class KeysightTimebase(BaseVisaScopeCommand):
    def __init__(self, scope: VisaScope) -> None:
        super().__init__(scope)

        self.time_cmds = init_time_cmds()
        self.time_fields = [field for field in self.capture_fields if field.startswith('time')]

    def apply_time_config(self, time_config: KeysightCaptureModel) -> None:
        try:
            for field, setting in time_config.dict().items():
                if has_setter(self, field) and setting is not None:
                    setattr(self, field, setting)

        except Exception as e:
            self.log.error(f"Applying timebase configuration encountered error: {e}")

    def fetch_time_config(self, time_info: KeysightCaptureModel) -> None:
        try:
            for field in self.time_fields:
                if has_prop(self, field):
                    setattr(time_info, field, getattr(self, field))

        except Exception as e:
            self.log.error(f"Fetching timebase configuration encountered error: {e}")

    # ------------------------------------------------------------------------------------
    #  Core Timebase Methods - common amongst all Keysight scopes and unlikely to be modified
    # ------------------------------------------------------------------------------------

    @property
    def time_pos(self) -> float:
        _time_pos = self.query(self.time_cmds, 'time_pos')
        return float(_time_pos)

    @time_pos.setter
    def time_pos(self, t_pos: float) -> None:
        self.set_and_verify_config(self.time_cmds, 'time_pos', t_pos)

    @property
    def time_range(self) -> float:
        _time_range = self.query(self.time_cmds, 'time_range')
        return float(_time_range)

    @time_range.setter
    def time_range(self, t_range: float) -> None:
        self.set_and_verify_config(self.time_cmds, 'time_range', t_range)

    @property
    def time_ref(self) -> str:
        _time_ref = self.query(self.time_cmds, 'time_ref')
        return _time_ref.lower()

    @time_ref.setter
    def time_ref(self, t_ref: str) -> None:
        self.set_and_verify_config(self.time_cmds, 'time_ref', t_ref.lower())

    # ------------------------------------------------------------------------------------
    #  Non-Core Acquire Methods - not universal amongst all Keysight scopes
    # ------------------------------------------------------------------------------------

    # --------------DSOX1200, DSOX2000, DSOX3000, DSOX4000, DSO5000-----------------------

    @property
    def time_scale(self) -> float:
        _time_scale = self.query(self.time_cmds, 'time_scale')
        return float(_time_scale)

    @time_scale.setter
    def time_scale(self, t_scale: float) -> None:
        self.set_and_verify_config(self.time_cmds, 'time_scale', t_scale)

    # ------------------------------------------------------------------------------------
    #  Custom Timebase Methods
    # ------------------------------------------------------------------------------------

    @property
    def time_zero(self) -> float:
        return self._time_zero

    @time_zero.setter
    def time_zero(self, t_zero: float) -> None:
        self._time_zero = t_zero
        ref_multipliers = {'cent': 5, 'left': 1, 'right': 9}

        multiplier = ref_multipliers.get(self.time_ref, None)
        if multiplier is None:
            raise ValueError("Scope is set to an unsupported timebase reference.")

        t_pos = (self.time_scale * multiplier) - t_zero
        self.log.debug(f"Calculated time position '{t_pos}' setting from time zero = '{t_zero}'.")

        self.time_pos = t_pos

    # TODO: implement with pre and post sample fields
    def samples_to_time(self) -> None:
        raise NotImplementedError

    # TODO: implement with pre and post time/sample fields
    def calc_time_values(self) -> None:
        raise NotImplementedError
