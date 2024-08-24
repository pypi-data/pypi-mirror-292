
from pygfdrivers.common.visa.visa_scope import VisaScope
from pygfdrivers.common.visa.visa_cmd import BaseVisaScopeCommand
from pygfdrivers.common.util.utilities import has_prop, has_setter
from pygfdrivers.common.models.device.cmd import create_cmd_class, CmdClassType

from pygfdrivers.keysight.models.trigger import KeysightTriggerModel


# ---------------------------------------------------------------------------------------------------------------------
#  Keysight VISA External Source Trigger Commands
# ---------------------------------------------------------------------------------------------------------------------
def init_ext_cmds() -> CmdClassType:
    ext: CmdClassType = create_cmd_class('ExternalTrigger')
    ext.add_cmd(key='ext_gain', cmd=':external:probe', default=1.0)
    ext.add_cmd(key='ext_range', cmd=':external:range', args=[1.6, 8.0])
    return ext


class KeysightExternalSource(BaseVisaScopeCommand):
    def __init__(self, scope: VisaScope) -> None:
        super().__init__(scope)

        self.ext_cmds = init_ext_cmds()

        _min = 0.1 if self.scope_series in {'DSOX2000', 'DSOX3000'} else 0.001
        self.ext_cmds.update_cmd_args('ext_gain', {'max': 10_000, 'min': _min})

    # -------------------------------------------------------------------------------------------------
    # Core External Source Trigger Methods - common amongst all Keysight scopes and unlikely to be modified
    # -------------------------------------------------------------------------------------------------

    @property
    def ext_gain(self) -> float:
        if not self.is_mxr:
            _ext_gain = self.query(self.ext_cmds, 'ext_gain')
            return float(_ext_gain)

    @ext_gain.setter
    def ext_gain(self, gain: float) -> None:
        if not self.is_mxr:
            self.set_and_verify_config(self.ext_cmds, 'ext_gain', gain)

    @property
    def ext_range(self) -> float:
        if not self.is_mxr:
            _ext_range = self.query(self.ext_cmds, 'ext_range')
            return float(_ext_range)

    @ext_range.setter
    def ext_range(self, v_range: float) -> None:
        if not self.is_mxr:
            self.set_and_verify_config(self.ext_cmds, 'ext_range', v_range)

            gain = self.ext_gain
            args = [1.6 * gain, 8.0 * gain] if self.scope_series in ['DSOX1200', 'DSOX4000'] else [8.0 * gain]
            self.ext_cmds.update_cmd_args('ext_range', args)
            self.ext_cmds.update_cmd_default('ext_range', 8.0 * gain)


# ---------------------------------------------------------------------------------------------------------------------
#  Keysight VISA Edge Mode Trigger Commands
# ---------------------------------------------------------------------------------------------------------------------
def init_edge_cmds() -> CmdClassType:
    edge: CmdClassType = create_cmd_class('Trigger')
    edge.add_cmd(key='edge_level', cmd=':trigger:edge:level')
    edge.add_cmd(key='edge_coupling', cmd=':trigger:edge:coupling', args=['ac', 'dc', 'lfreject'], default='ac')
    edge.add_cmd(
        key='edge_reject',
        cmd=':trigger:edge:reject',
        args=['off', 'lfreject', 'hfreject', 'lfr', 'hfr'],
        default='off'
    )
    edge.add_cmd(
        key='edge_slope',
        cmd=':trigger:edge:slope',
        args=['positive', 'negative', 'either', 'alternate'],
        default='positive'
    )
    edge.add_cmd(
        key='edge_source',
        cmd=':trigger:edge:source',
        args=['channel1', 'channel2', 'channel3', 'channel4', 'external', 'line', 'wgen'],
        default='external'
    )
    return edge


class KeysightEdgeMode(KeysightExternalSource):
    def __init__(self, scope: VisaScope) -> None:
        super().__init__(scope)

        self.edge_cmds = init_edge_cmds()

        if self.is_mxr:
            self.edge_cmds.add_cmd(
                key='edge_source',
                cmd=':trigger:edge:source',
                args=['channel1', 'channel2', 'channel3', 'channel4', 'external', 'line', 'wgen', 'aux'],
                default='aux'
            )
            self.edge_cmds.add_cmd(
                key='edge_coupling',
                cmd=':trigger:edge:coupling',
                args=['ac', 'dc', 'lfreject', 'lfr', 'hfreject', 'hfr'],
                default='dc'
            )

    # -------------------------------------------------------------------------------------------------
    #  Core Edge Mode Trigger Methods - common amongst all Keysight scopes and unlikely to be modified
    # -------------------------------------------------------------------------------------------------

    @property
    def edge_coupling(self) -> str:
        _edge_coupling = self.query(self.edge_cmds, 'edge_coupling')
        return _edge_coupling.lower()

    @edge_coupling.setter
    def edge_coupling(self, coupling: str) -> None:
        self.set_and_verify_config(self.edge_cmds, 'edge_coupling', coupling.lower())

    @property
    def edge_level(self) -> float:
        if not self.is_mxr:
            _edge_level = self.query(self.edge_cmds, 'edge_level')
            return float(_edge_level)

    # TODO: Need to figure how to deal with v_range if the edge source is not external
    @edge_level.setter
    def edge_level(self, level: float) -> None:
        if not self.is_mxr:
            cmd_key = 'edge_level'
            v_range = getattr(self, 'ext_range') or 5.0

            if -v_range <= level <= v_range:
                self.scope.write_scope(self.edge_cmds, cmd_key, setting=level)
                self.scope.verify_config(self.edge_cmds, cmd_key, level)
            else:
                self.log.warning(f"'{cmd_key} {level}' not within [{-v_range},{v_range}], default to auto-set.")
                getattr(self, 'trig_level_auto')()

    @property
    def edge_reject(self) -> str:
        if not self.is_mxr:
            _edge_reject = self.query(self.edge_cmds, 'edge_reject')
            return _edge_reject.lower()

    @edge_reject.setter
    def edge_reject(self, reject: str) -> None:
        if not self.is_mxr:
            self.set_and_verify_config(self.edge_cmds, 'edge_reject', reject.lower())

    @property
    def edge_slope(self) -> str:
        _edge_slope = self.query(self.edge_cmds, 'edge_slope')
        return _edge_slope.lower()

    @edge_slope.setter
    def edge_slope(self, slope: str) -> None:
        self.set_and_verify_config(self.edge_cmds, 'edge_slope', slope.lower())

    @property
    def edge_source(self) -> str:
        _edge_source = self.query(self.edge_cmds, 'edge_source')
        return _edge_source.lower()

    @edge_source.setter
    def edge_source(self, source: str) -> None:
        source = source.lower()
        source = 'aux' if self.is_mxr and 'ext' in source else source
        self.set_and_verify_config(self.edge_cmds, 'edge_source', source)


# ---------------------------------------------------------------------------------------------------------------------
#  Keysight VISA Main Trigger Commands
# ---------------------------------------------------------------------------------------------------------------------
def init_trig_cmds() -> CmdClassType:
    trig: CmdClassType = create_cmd_class('Trigger')
    trig.add_cmd(key='trig_force', cmd=':trigger:force')
    trig.add_cmd(key='trig_level_auto', cmd=':trigger:level:asetup')
    trig.add_cmd(key='trig_holdoff', cmd=':trigger:holdoff', args={'max': 10, 'min': 60e-9}, default=60e-9)
    trig.add_cmd(key='trig_sweep', cmd=':trigger:sweep', args=['auto', 'normal', 'norm'], default='normal')
    trig.add_cmd(
        key='trig_mode',
        cmd=':trigger:mode',
        args=['edge', 'glitch', 'pattern', 'shold', 'transition', 'tv', 'sbus1'],
        default='edge'
    )
    return trig


class KeysightTrigger(KeysightEdgeMode):
    def __init__(self, scope: VisaScope) -> None:
        super().__init__(scope)

        self.trig_cmds = init_trig_cmds()

        if self.is_mxr:
            self.trig_cmds.add_cmd(
                key='trig_level',
                cmd=':trigger:level'
            )

    def apply_trig_config(self, trig_config: KeysightTriggerModel) -> None:
        try:
            # Trigger mode must always be set first as it dictates which setters are going to be used.
            self.trig_mode = trig_config.trig_mode
            mode = self.trig_mode

            for field, setting in trig_config.dict().items():
                if field != 'trig_mode' and setting is not None:
                    if field.endswith(('gain', 'range')) and not self.is_mxr:
                        trig_prefix = 'ext'
                    elif field.endswith('level') and self.is_mxr:
                        trig_prefix = 'trig'
                    else:
                        trig_prefix = mode
                    setter = field.replace('trig', trig_prefix)

                    if has_setter(self, setter):
                        setattr(self, setter, setting)

        except Exception as e:
            self.log.error(f"Applying trigger configuration encountered error: {e}")

    def fetch_trig_config(self, trig_info: KeysightTriggerModel) -> None:
        try:
            trig_info.trig_mode = self.trig_mode
            mode = self.trig_mode

            for field in self.trig_fields:
                if field != 'trig_mode':
                    trig_prefix = 'ext' if field.endswith(('gain', 'range')) else f"{mode}"
                    prop = field.replace('trig', trig_prefix)

                    if has_prop(self, prop):
                        setattr(trig_info, field, getattr(self, prop))

        except Exception as e:
            self.log.error(f"Fetching trigger configuration encountered error: {e}")

    # -------------------------------------------------------------------------------------------------
    #  Core Trigger Methods - common amongst all Keysight scopes and unlikely to be modified
    # -------------------------------------------------------------------------------------------------

    @property
    def trig_holdoff(self) -> float:
        _trig_holdoff = self.query(self.trig_cmds, 'trig_holdoff')
        return float(_trig_holdoff)

    @trig_holdoff.setter
    def trig_holdoff(self, holdoff: float) -> None:
        self.set_and_verify_config(self.trig_cmds, 'trig_holdoff', holdoff)

    @property
    def trig_mode(self) -> str:
        _trig_mode = self.query(self.trig_cmds, 'trig_mode')
        return _trig_mode.lower()

    @trig_mode.setter
    def trig_mode(self, mode: str) -> None:
        self.set_and_verify_config(self.trig_cmds, 'trig_mode', mode.lower())

    @property
    def trig_sweep(self) -> str:
        _trig_sweep = self.query(self.trig_cmds, 'trig_sweep')
        return _trig_sweep.lower()

    @trig_sweep.setter
    def trig_sweep(self, sweep: str) -> None:
        self.set_and_verify_config(self.trig_cmds, 'trig_sweep', sweep.lower())

    # -------------------------------------------------------------------------------------------------
    #  Non-Core Trigger Methods - not universal amongst all Keysight scopes
    # -------------------------------------------------------------------------------------------------

    @property
    def trig_level(self) -> float:
        _trig_level = self.query(cmd=f":trigger:level? aux")
        return float(_trig_level)

    @trig_level.setter
    def trig_level(self, level: float) -> None:
        cmd_key = 'trig_level'
        v_range = 5.0

        if -v_range <= level <= v_range:
            self.scope.write_scope(self.trig_cmds, cmd_key, setting=level)
        else:
            self.log.warning(f"'{cmd_key} {level}' not within [{-v_range},{v_range}], default to auto-set.")
            getattr(self, 'trig_level_auto')()

    def trig_level_auto(self, state: bool) -> None:
        self.write(self.trig_cmds, 'trig_level_auto', setting=int(state))

    def trig_force(self) -> None:
        self.write(self.trig_cmds, 'trig_force')
