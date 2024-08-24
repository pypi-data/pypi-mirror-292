from pygfdrivers.common.visa.visa_scope import VisaScope
from pygfdrivers.common.visa.visa_cmd import BaseVisaScopeCommand
from pygfdrivers.common.models.device.cmd import create_cmd_class, CmdClassType


def init_wave_cmds() -> CmdClassType:
    wave: CmdClassType = create_cmd_class('Waveform')
    wave.add_cmd(key='wave_data', cmd='wf', args=['c1', 'c2', 'c3', 'c4', 'math'], default='c1')
    return wave


class LecroyWaveform(BaseVisaScopeCommand):
    def __init__(self, visa_scope: VisaScope) -> None:
        super().__init__(visa_scope)

        self.visa_scope = self.scope.scope
        self.wave_cmds = init_wave_cmds()

    def wave_data(self, source: str) -> list:
        cmd_key = 'wave_data'
        source_opts = self.wave_cmds.fetch_args(cmd_key)
        source_default = self.wave_cmds.fetch_default(cmd_key)

        try:
            if source_opts is not None and source not in source_opts:
                self.log.warning(f"source: '{source}' not in '{source_opts}', default to '{source_default}'.")
                source = source_default

            cmd_str = f"{source}:{self.wave_cmds.fetch_cmd(cmd_key)}? dat2"
            _wave_data = self.visa_scope.query_binary_values(cmd_str, datatype ='b')
            return _wave_data
        except Exception as e:
            self.log.error(f"Fetching wave_data from source '{source}' encountered error: {e}.")
