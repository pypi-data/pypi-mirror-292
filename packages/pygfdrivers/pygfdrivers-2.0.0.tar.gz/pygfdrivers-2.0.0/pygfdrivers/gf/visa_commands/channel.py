from typing import List, Dict, Union

from pygfdrivers.common.visa.visa_cmd import BaseVisaScopeCommand
from pygfdrivers.common.visa.visa_scope import VisaScope
from pygfdrivers.common.util.utilities import has_prop, has_setter
from pygfdrivers.gf.models.digitizer_config import GFChannelModel
from pygfdrivers.gf.models.digitizer_data import GFChannelDataModel


class GFDigitizerChannel(BaseVisaScopeCommand):
    def __init__(self, visa_scope: VisaScope) -> None:
        self._channels = {}
        for channel in range(1,11):
            self._channels[str(channel)] = GFChannelDataModel() 
        super().__init__(visa_scope)

    def apply_ch_config(self, active_channels,  config: Dict[int, GFChannelModel]) -> None:
        try:
            for ch in active_channels:
                self.ch_num = ch
                ch_model = config[ch]
                for field, setting in ch_model.dict().items():
                    if has_setter(self, field) and setting is not None:
                        self.set_ch(field, setting, ch)
        except Exception as e:
            self.log.error(f"Applying channel configuration encountered error: {e}")

    def fetch_ch_config(self, active_chs: List[int], config: Dict[str, GFChannelDataModel]) -> None:
        try:
            for ch in active_chs:    
                self.ch_num = ch     
                ch_model = config[str(ch)]
                for field in self.source_fields:
                    if has_prop(self, field):
                        setattr(ch_model, field, getattr(self, field)) 
        except Exception as e:
            self.log.error(f"Fetching configuration encountered error: {e}")

    def set_ch(self, setter: str, setting: Union[int, float, str, bool], ch: int) -> None:
        try:
            self.ch_num = ch
            setattr(self, setter, setting)
        except Exception as e:
            self.log.error(f"Setting channel '{ch}' '{setter}' to '{setting}' encountered error: {e}.")

    def get_ch(self, getter: str, ch: int) -> None:
        try:
            self.ch_num = ch
            return getattr(self, getter)
        except Exception as e:
            self.log.error(f"Fetching channel '{ch}' '{getter}' encountered error: {e}.")

    def format_channel(self, channel):
        """
        Checks format of command input is of channel = xx, as required by digitizer
        i.e channel must be a number in range [1,10]
        """
        try:
            if (1 <= int(channel) <= 10 ) & (len(str(channel)) <= 2):
                return str(channel).zfill(2)
            else:
                self.log.error(f"Incorrect data format for channel input")
        except Exception as e:
            self.log.error(f"Incorrect data format for channel input: {e}")

    def format_coupling(self, coupling):
        """
        Checks format of command input is of state = ac or state = dc as required by digitizer
        """
        possibleStates = {"ac", "dc"}
        try:
            if coupling.lower() in possibleStates:
                return coupling.lower()
            else:
                self.log.error(f"Incorrect data format for state input")
        except Exception as e:
            self.log.error(f"Incorrect data format for state input: {e}")

    def format_gain(self, gain):
        try:
            gain = int(gain)
            if 1<= gain <= 16:
                return str(gain)
            else:
                self.log.error(f"Incorrect data format for gain input") 
        except Exception as e:
            self.log.error(f"Incorrect data format for gain input: {e}")

    @property
    def ch_gain(self) -> int:
        return self._channels[str(self.ch_num)].ch_gain
    
    @ch_gain.setter
    def ch_gain(self, gain:int) -> None:
        ch = self.ch_num
        self._channels[str(ch)].ch_gain = gain
        ch = self.format_channel(ch)
        gain = self.format_gain(gain)
        self.query(cmd= f"set_gain_value chan={ch} value={gain}")

    @property
    def ch_coupling(self) -> str:
        return self._channels[str(self.ch_num)].ch_coupling

    @ch_coupling.setter
    def ch_coupling(self, coupling: str) -> None:
        ch = self.ch_num
        self._channels[str(ch)].ch_coupling = coupling
        ch = self.format_channel(ch)
        coupling = self.format_coupling(coupling)
        self.query(cmd= f"set_coupling_state chan={ch} state={coupling}")

    @property
    def ch_offset(self) -> float:
        return self._channels[str(self.ch_num)].ch_offset
    
    @ch_offset.setter
    def ch_offset(self, offset: float) -> None:
        ch = self.ch_num
        self._channels[str(ch)].ch_offset = offset
