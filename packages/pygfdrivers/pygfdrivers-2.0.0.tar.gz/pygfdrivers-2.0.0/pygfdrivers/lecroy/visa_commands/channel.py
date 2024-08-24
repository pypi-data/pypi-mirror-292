from time import sleep
from typing import Dict, List, Union

from pygfdrivers.common.visa.visa_scope import VisaScope
from pygfdrivers.common.visa.visa_cmd import BaseVisaScopeCommand
from pygfdrivers.common.util.utilities import has_prop, has_setter
from pygfdrivers.common.models.device.cmd import create_cmd_class, CmdClassType


from pygfdrivers.lecroy.models.channel import LecroyChannelModel, LecroyChannelDataModel


def init_ch_cmds() -> CmdClassType:
    ch: CmdClassType = create_cmd_class('Channel')
    ch.add_cmd(key='ch_offset', cmd='ofst')
    ch.add_cmd(key='ch_scale', cmd='vdiv', args={'max': 10, 'min': 500e-6})
    ch.add_cmd(key='ch_display', cmd='tra', args=['on', 'off'], default='on')
    ch.add_cmd(key='ch_invert', cmd='invs', args=['on', 'off'], default='off')
    ch.add_cmd(key='ch_coupling', cmd='cpl', args=['a1m', 'a50', 'd1m', 'd50', 'gnd'], default='a1m')
    ch.add_cmd(
        key='ch_gain',
        cmd='attn',
        args=[0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1_000, 2_000, 5_000, 10_000],
        default=1
    )
    return ch


class LecroyChannel(BaseVisaScopeCommand):
    def __init__(self, scope: VisaScope) -> None:
        super().__init__(scope)

        self.ch_cmds = init_ch_cmds()
        self.ch_fields = [field for field in self.source_fields if field.startswith('ch')]
        self.max_chs = 4

    def apply_ch_config(self, active_chs: List[int], ch_config: Dict[int, LecroyChannelModel]) -> None:
        try:
            for ch in range(1, self.max_chs + 1):
                self.set_ch('ch_display', True if ch in active_chs else False, ch)

            for ch in active_chs:
                config = ch_config[ch]
                for field, setting in config.dict().items():
                    if has_setter(self, field) and setting is not None:
                        self.set_ch(field, setting, ch)
                    sleep(0.3)
        except Exception as e:
            self.log.error(f"Applying channel configuration encountered error: {e}.")

    def fetch_ch_config(self, active_chs: List[int], ch_info: Dict[str, LecroyChannelDataModel]) -> None:
        try:
            for ch in active_chs:
                info = ch_info[str(ch)]
                for field in self.ch_fields:
                    if has_prop(self, field):
                        setattr(info, field, self.get_ch(field, ch))

        except Exception as e:
            self.log.error(f"Fetching channel configuration encountered error: {e}.")

    def set_ch(self, setter: str, setting: Union[int, float, str, bool], ch: int) -> None:
        try:
            self.ch_num = f"c{ch}"
            setattr(self, setter, setting)
        except Exception as e:
            self.log.error(f"Setting channel '{ch}' '{setter}' to '{setting}' encountered error: {e}.")

    def get_ch(self, getter: str, ch: int) -> Union[int, float, str, bool]:
        try:
            self.ch_num = f"c{ch}"
            return getattr(self, getter)
        except Exception as e:
            self.log.error(f"Fetching channel '{ch}' '{getter}' encountered error: {e}.")

    @property
    def ch_coupling(self) -> str:
        _ch_coupling = self.query(cmd=f"{self.ch_num}:{self.ch_cmds.fetch_cmd('ch_coupling')}")
        return _ch_coupling.lower()

    @ch_coupling.setter
    def ch_coupling(self, coupling: str) -> None:
        cmd_key = 'ch_coupling'
        coupl_default = self.ch_cmds.fetch_default(cmd_key)
        coupl_opts = self.ch_cmds.fetch_args(cmd_key)

        try:
            if coupl_opts is not None and coupling not in coupl_opts:
                self.log.warning(f"coupling: '{coupling}' not in '{coupl_opts}', defaulting to '{coupl_default}'.")
                coupling = coupl_default

            cmd_str = f"{self.ch_num}:{self.ch_cmds.fetch_cmd(cmd_key)}"
            self.write(cmd=cmd_str, setting=coupling)
        except Exception as e:
            self.log.error(f"Setting ch_coupling to '{coupling}' encountered error: {e}")

    @property
    def ch_display(self) -> bool:
        query = self.query(cmd=f"c{self.ch_num}:{self.ch_cmds.fetch_cmd('ch_display')}")
        _ch_display = 'on' in query.lower()
        return _ch_display

    @ch_display.setter
    def ch_display(self, state: bool) -> None:
        cmd_key = 'ch_display'
        state = 'on' if state is True else 'off'
        cmd_str = f"{self.ch_num}:{self.ch_cmds.fetch_cmd(cmd_key)}"
        self.write(cmd=cmd_str, setting=state)

    @property
    def ch_offset(self) -> float:
        _ch_offset = self.query(cmd=f"{self.ch_num}:{self.ch_cmds.fetch_cmd('ch_offset')}")
        return float(_ch_offset)

    @ch_offset.setter
    def ch_offset(self, y_offset: float) -> None:
        # there are 400 ticks in the positive and the negative direction for setting the dc offset
        # the dc offset increment per tick is determined by (v_div * 8)/400
        cmd_key = 'ch_offset'

        try:
            cmd_str = f"{self.ch_num}:{self.ch_cmds.fetch_cmd(cmd_key)}"
            self.write(cmd=cmd_str, setting=f"{y_offset:.4e}")
        except Exception as e:
            self.log.error(f"Setting ch_offset to '{y_offset}' encountered error: {e}")

    @property
    def ch_gain(self) -> float:
        _ch_gain = self.query(cmd=f"{self.ch_num}:{self.ch_cmds.fetch_cmd('ch_gain')}")
        return float(_ch_gain)

    @ch_gain.setter
    def ch_gain(self, gain: float) -> None:
        cmd_key = 'ch_gain'
        gain = gain if gain < 0 else int(gain)
        gain_opts = self.ch_cmds.fetch_args(cmd_key)
        gain_default = self.ch_cmds.fetch_cmd(cmd_key)

        try:
            if gain_opts is not None and gain not in gain_opts:
                self.log.warning(f"gain: '{gain}' not in '{gain_opts}', defaulting to '{gain_default}'.")
                gain = gain_default

            cmd_str = f"{self.ch_num}:{self.ch_cmds.fetch_cmd(cmd_key)}"
            self.write(cmd=cmd_str, setting=gain)
        except Exception as e:
            self.log.error(f"Setting ch_gain to '{gain}' encountered error: {e}")

    @property
    def ch_range(self) -> float:
        _ch_range = self.ch_scale * 8
        return _ch_range

    @ch_range.setter
    def ch_range(self, y_range: float) -> None:
        self.ch_scale = y_range / 8

    @property
    def ch_scale(self) -> float:
        _ch_scale = self.query(cmd=f"{self.ch_num}:{self.ch_cmds.fetch_cmd('ch_scale')}")
        return float(_ch_scale)

    @ch_scale.setter
    def ch_scale(self, y_scale: float) -> None:
        cmd_key = 'ch_scale'
        scale_lim = self.ch_cmds.fetch_args(cmd_key)
        _min = scale_lim.get('min')
        _max = scale_lim.get('max')

        if _min > y_scale > _max:
            yscale_default = min(max(y_scale, _min), _max)
            self.log.warning(f"y_scale: '{y_scale}' not within '[{_min},{_max}]', default to '{yscale_default}'.")
            y_scale = yscale_default

        try:
            cmd_str = f"{self.ch_num}:{self.ch_cmds.fetch_cmd(cmd_key)}"
            self.write(cmd=cmd_str, setting=f"{y_scale:.2e}")
        except Exception as e:
            self.log.error(f"Setting ch_scale to '{y_scale}' encountered error: {e}")

    @property
    def ch_invert(self) -> bool:
        query = self.query(cmd=f"{self.ch_num}:{self.ch_cmds.fetch_cmd('ch_invert')}")
        _ch_invert = 'on' in query.lower()
        return _ch_invert

    @ch_invert.setter
    def ch_invert(self, state: bool) -> None:
        cmd_key = 'ch_invert'
        state = 'on' if state is True else 'off'
        cmd_str = f"{self.ch_num}:{self.ch_cmds.fetch_cmd(cmd_key)}"
        self.write(cmd=cmd_str, setting=state)
