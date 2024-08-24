from typing import TYPE_CHECKING

from pygfdrivers.common.visa.visa_cmd import BaseVisaScopeCommand
from pygfdrivers.common.util.utilities import has_prop, has_setter
from pygfdrivers.common.models.device.cmd import create_cmd_class, CmdClassType

from pygfdrivers.keysight.models.capture import KeysightCaptureModel

if TYPE_CHECKING:
    from pygfdrivers.keysight.keysight_visa_scope import KeysightVisaScope


def init_acq_cmds() -> CmdClassType:
    acq: CmdClassType = create_cmd_class('acquire')
    acq.add_cmd(key='acq_srate', cmd=':acquire:srate')
    acq.add_cmd(key='acq_points', cmd=':acquire:points')
    acq.add_cmd(key='acq_segment_count', cmd=':acquire:segmented:count')
    acq.add_cmd(key='acq_segment_index', cmd=':acquire:segmented:index')
    acq.add_cmd(key='acq_complete', cmd=':acquire:complete', args=[100], default=100)
    acq.add_cmd(key='acq_count', cmd=':acquire:count', args={'max': 65536, 'min': 2}, default=2)
    acq.add_cmd(key='acq_mode', cmd=':acquire:mode', args=['rtime', 'rtim', 'segmented', 'segm'], default='rtime')
    acq.add_cmd(
        key='acq_type',
        cmd=':acquire:type',
        args=['normal', 'norm', 'average', 'aver', 'hresolution', 'hres', 'peak'],
        default='normal'
    )
    return acq


class KeysightAcquire(BaseVisaScopeCommand):
    def __init__(self, scope: 'KeysightVisaScope') -> None:
        super().__init__(scope)

        self.has_segment_mode = None
        self.acq_cmds = init_acq_cmds()
        self.acq_fields = [field for field in self.capture_fields if field.startswith('acq')]

        # Segment count and index can still be set even if the option is not present in the scope, since it exists
        # in the software and a license key just unlocks the functionality or active usage of it
        max_segments = 250
        if self.scope_series in ['DSOX2000', 'DSO5000']:
            max_segments = 250
        elif self.scope_series in ['DSOX1200']:
            max_segments = 500
        elif self.scope_series in ['DSOX3000', 'DSOX4000', 'MXR']:
            max_segments = 1000
        self.acq_cmds.update_cmd_args('acq_segment_count', {'max': max_segments, 'min': 2})

        if self.scope_series in {'MXR', 'DSOX4000'}:
            self.acq_cmds.add_cmd(key='acq_srate', cmd=':acquire:srate:analog')
            self.acq_cmds.add_cmd(key='acq_srate_auto', cmd=':acquire:srate:auto', args=[1, 0, 'on', 'off'], default=1)

    def apply_acq_config(self, acq_config: KeysightCaptureModel) -> None:
        try:
            segment_count = acq_config.acq_segment_count
            self.acq_mode = 'segm' if self.has_segment_mode and segment_count > 1 else 'rtime'

            for field, setting in acq_config.dict().items():
                if has_setter(self, field) and setting is not None and field != 'acq_segment_count':
                    setattr(self, field, setting)
        except Exception as e:
            self.log.error(f"Applying acquire configuration encountered error: {e}")

    def fetch_acq_config(self, acq_info: KeysightCaptureModel) -> None:
        try:
            for field in self.acq_fields:
                if has_prop(self, field):
                    setattr(acq_info, field, getattr(self, field))
        except Exception as e:
            self.log.error(f"Fetching acquire configuration encountered error: {e}")

    # ------------------------------------------------------------------------------------
    #  Core Acquire Methods - common amongst all Keysight scopes and unlikely to be modified
    # ------------------------------------------------------------------------------------

    @property
    def acq_complete(self) -> int:
        _acq_complete = self.query(self.acq_cmds, 'acq_complete')
        return int(_acq_complete)

    @acq_complete.setter
    def acq_complete(self, percent: int) -> None:
        self.set_and_verify_config(self.acq_cmds, 'acq_complete', percent)

    @property
    def acq_count(self):
        _acq_count = self.query(self.acq_cmds, 'acq_count')
        return int(_acq_count)

    @acq_count.setter
    def acq_count(self, count: int) -> None:
        self.set_and_verify_config(self.acq_cmds, 'acq_count', count)

    @property
    def acq_mode(self) -> str:
        _acq_mode = self.query(self.acq_cmds, 'acq_mode')
        return _acq_mode.lower()

    @acq_mode.setter
    def acq_mode(self, acq_mode: str) -> None:
        self.set_and_verify_config(self.acq_cmds, 'acq_mode', acq_mode.lower())

    @property
    def acq_points(self) -> int:
        _acq_points = self.query(self.acq_cmds, 'acq_points')
        return int(_acq_points)

    @property
    def acq_type(self) -> str:
        if not self.is_mxr:
            _acq_type = self.query(self.acq_cmds, 'acq_type')
            return _acq_type.lower()

    @acq_type.setter
    def acq_type(self, acq_type: str) -> None:
        if not self.is_mxr:
            self.set_and_verify_config(self.acq_cmds, 'acq_type', acq_type.lower())

    # ------------------------------------------------------------------------------------
    #  Non-Core Acquire Methods - not universal amongst all Keysight scopes
    # ------------------------------------------------------------------------------------

    # --------------DSOX1200, DSOX2000, DSOX3000, DSOX4000, DSO5000-----------------------

    @property
    def acq_segment_count(self) -> int:
        _acq_segment_count = self.query(self.acq_cmds, 'acq_segment_count')
        return int(_acq_segment_count)

    @acq_segment_count.setter
    def acq_segment_count(self, segment_count: int) -> None:
        self.set_and_verify_config(self.acq_cmds, 'acq_segment_count', segment_count)

    @property
    def acq_segment_index(self) -> int:
        _acq_segment_index = self.query(self.acq_cmds, 'acq_segment_index')
        return int(_acq_segment_index)

    @acq_segment_index.setter
    def acq_segment_index(self, index: int) -> None:
        self.set_and_verify_config(self.acq_cmds, 'acq_segment_index', index)

    @property
    def acq_srate(self) -> float:
        _acq_srate = self.query(self.acq_cmds, 'acq_srate')
        return float(_acq_srate)

    @acq_srate.setter
    def acq_srate(self, srate: float) -> None:
        if self.scope_series in ['MXR', 'DSOX4000']:
            self.set_and_verify_config(self.acq_cmds, 'acq_srate', srate)

    # ------------------------------------MXR---------------------------------------------

    @property
    def acq_srate_auto(self) -> bool:
        if self.scope_series in ['MXR', 'DSOX4000']:
            _acq_srate_auto = self.query(self.acq_cmds, 'acq_srate')
            return bool(int(_acq_srate_auto))

    @acq_srate_auto.setter
    def acq_srate_auto(self, srate_auto: bool) -> None:
        if self.scope_series in ['MXR', 'DSOX4000']:
            self.set_and_verify_config(self.acq_cmds, 'acq_srate_auto', int(srate_auto))
