from pygfdrivers.common.visa.visa_scope import VisaScope
from pygfdrivers.common.visa.visa_cmd import BaseVisaScopeCommand
from pygfdrivers.common.util.utilities import has_prop, has_setter
from pygfdrivers.common.models.device.cmd import create_cmd_class, CmdClassType

from pygfdrivers.lecroy.models.trigger import LecroyTriggerModel


def init_trig_cmds() -> CmdClassType:
    trig: CmdClassType = create_cmd_class('Trigger')
    trig.add_cmd(key='trig_force', cmd='*trg')
    trig.add_cmd(key='trig_level', cmd='trlv')
    trig.add_cmd(key='trig_select', cmd='trse')
    trig.add_cmd(key='trig_set50', cmd='set50', default=False)
    trig.add_cmd(key='trig_sweep', cmd='trmd', args=['auto', 'normal'], default='normal')
    trig.add_cmd(key='trig_coupling', cmd='trcp', args=['ac', 'dc', 'hfrej', 'lfrej'], default='ac')
    trig.add_cmd(key='trig_slope', cmd='trsl', args=['negative', 'positive', 'alternating'], default='positive')
    trig.add_cmd(key='trig_source', cmd='trse', args=['c1', 'c2', 'c3', 'c4', 'line', 'ex', 'ex5'], default='ex5')
    trig.add_cmd(key='trig_mode', cmd='trse', args=['edge', 'slew', 'glit', 'intv', 'runt', 'drop'], default='edge')
    return trig


class LecroyTrigger(BaseVisaScopeCommand):
    def __init__(self, scope: VisaScope) -> None:
        super().__init__(scope)

        self.trig_cmds = init_trig_cmds()

    def apply_trig_config(self, trig_config: LecroyTriggerModel) -> None:
        try:
            for field in trig_config.model_fields:
                setting = getattr(trig_config, field)
                if has_setter(self, field) and setting is not None:
                    setattr(self, field, setting)

        except Exception as e:
            self.log.error(f"Applying trigger configuration encountered error: {e}")

    def fetch_trig_config(self, trig_info: LecroyTriggerModel) -> None:
        try:
            for field in self.trig_fields:
                if has_prop(self, field):
                    setattr(trig_info, field, getattr(self, field))

        except Exception as e:
            self.log.error(f"Fetching trigger configuration encountered error: {e}")

    @property
    def trig_select(self) -> str:
        _trig_select = self.query(self.trig_cmds, 'trig_select')
        return _trig_select.lower()

    @trig_select.setter
    def trig_select(self, option: str) -> None:
        cmd_key = 'trig_select'
        option = option.lower()

        try:
            self.write(self.trig_cmds, cmd_key, setting=option)
        except Exception as e:
            self.log.error(f"Setting trig_select to '{option}' encountered error: {e}")

    @property
    def trig_mode(self) -> str:
        _trig_mode = self.trig_select.split(',')[0]
        return _trig_mode.lower()

    @trig_mode.setter
    def trig_mode(self, mode: str) -> None:
        cmd_key = 'trig_mode'
        mode = mode.lower()
        mode_opts = self.trig_cmds.fetch_args(cmd_key)
        mode_default = self.trig_cmds.fetch_default(cmd_key)

        try:
            if mode_opts is not None and mode not in mode_opts:
                self.log.warning(f"mode: '{mode}' not in '{mode_opts}', default to '{mode_default}'.")
                mode = mode_default

            self.trig_select = mode
        except Exception as e:
            self.log.error(f"Setting trig_mode to '{mode}' encountered error: {e}")

    @property
    def trig_sweep(self) -> str:
        _trig_sweep = self.query(self.trig_cmds, 'trig_sweep')
        return _trig_sweep.lower()

    @trig_sweep.setter
    def trig_sweep(self, sweep: str) -> None:
        cmd_key = 'trig_sweep'
        sweep = sweep.lower()
        sweep_opts = self.trig_cmds.fetch_args(cmd_key)

        try:
            if sweep_opts is not None and sweep not in sweep_opts:
                self.log.warning(f"sweep: '{sweep}' not in valid options: '{sweep_opts}', default to 'normal'.")
                sweep = self.trig_cmds.fetch_default(cmd_key)

            sweep = 'norm' if 'norm' in sweep else 'auto'
            cmd_str = f"{self.trig_cmds.fetch_cmd(cmd_key)}"
            self.write(cmd=cmd_str, setting=sweep)
        except Exception as e:
            self.log.error(f"Setting trig_sweep to '{sweep}' encountered error: {e}")

    @property
    def trig_level(self) -> float:
        _trig_level = self.query(self.trig_cmds, 'trig_level')
        return float(_trig_level)

    @trig_level.setter
    def trig_level(self, level: float) -> None:
        source = self.trig_source
        if source == 'ex':
            max_level = 600e-3
        elif source == 'ex5':
            max_level = 3.0
        else:
            max_level = 4.5

        level = min(max(level, -max_level), max_level)
        cmd_str = f"{self.trig_source}:{self.trig_cmds.fetch_cmd('trig_level')}"

        try:
            self.write(cmd=cmd_str, setting=level)
        except Exception as e:
            self.log.error(f"Setting trigger level to '{level}' encountered error: {e}")

    @property
    def trig_coupling(self) -> str:
        _trig_coupling = self.query(cmd=f"{self.trig_source}:{self.trig_cmds.fetch_cmd('trig_coupling')}")
        return _trig_coupling.lower()

    @trig_coupling.setter
    def trig_coupling(self, coupling: str) -> None:
        cmd_key = 'trig_coupling'
        coupling = coupling.lower()
        coupling_opts = self.trig_cmds.fetch_args(cmd_key)
        coupling_default = self.trig_cmds.fetch_default(cmd_key)

        try:
            if coupling_opts is not None and coupling not in coupling_opts:
                self.log.warning(f"coupling: '{coupling}' not in '{coupling_opts}', default to '{coupling_default}'.")
                coupling = coupling_default

            cmd_str = f"{self.trig_source}:{self.trig_cmds.fetch_cmd(cmd_key)}"
            self.write(cmd=cmd_str, setting=coupling)
        except Exception as e:
            self.log.error(f"Setting trig_coupling to '{coupling}' encountered error: {e}")

    @property
    def trig_slope(self) -> str:
        _trig_slope = self.query(self.trig_cmds, 'trig_slope')
        return _trig_slope.lower()

    @trig_slope.setter
    def trig_slope(self, slope: str) -> None:
        cmd_key = 'trig_slope'
        slope = slope.lower()
        slope_opts = self.trig_cmds.fetch_args(cmd_key)
        slope_default = self.trig_cmds.fetch_default(cmd_key)

        try:
            if slope_opts is not None and slope not in slope_opts:
                self.log.warning(f"slope: '{slope}' not in '{slope_opts}', default to '{slope_default}'.")
                slope = slope_default

            if slope == 'negative':
                slope = 'neg'
            elif slope == 'positive':
                slope = 'pos'
            elif slope == 'alternating':
                slope = 'window'

            cmd_str = f"{self.trig_source}:{self.trig_cmds.fetch_cmd(cmd_key)}"
            self.write(cmd=cmd_str, setting=slope)
        except Exception as e:
            self.log.error(f"Setting trig_slope to '{slope}' encountered error: {e}")

    @property
    def trig_source(self) -> str:
        _trig_source = self.trig_select.split(',')[2]
        _trig_source = 'external' if 'EX' in _trig_source else _trig_source
        return _trig_source.lower()

    @trig_source.setter
    def trig_source(self, source: str) -> None:
        cmd_key = 'trig_source'
        source = source.lower()
        source_opts = self.trig_cmds.fetch_args(cmd_key)
        source_default = self.trig_cmds.fetch_default(cmd_key)

        try:
            if source_opts is not None and source not in source_opts:
                self.log.warning(f"source: '{source}' not in '{source_opts}', default to '{source_default}'.")
                source = source_default

            self.trig_select = f"{self.trig_mode},sr,{source}"
        except Exception as e:
            self.log.error(f"Setting trig_source to '{source}' encountered error: {e}")

    def trig_set50(self, state: bool) -> None:
        try:
            self.scope.set_and_verify_config(self.trig_cmds, 'trig_set50', int(state))
        except Exception as e:
            self.log.error(f"Setting trig_level to 50% of y_range encountered error: {e}")

    def trig_force(self) -> None:
        self.write(self.trig_cmds, 'trig_force')
