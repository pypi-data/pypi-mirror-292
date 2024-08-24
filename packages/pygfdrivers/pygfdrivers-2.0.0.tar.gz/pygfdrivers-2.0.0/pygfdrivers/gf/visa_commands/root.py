from pygfdrivers.common.visa.visa_cmd import BaseVisaScopeCommand
from pygfdrivers.common.visa.visa_scope import VisaScope



class GFDigitizerRoot(BaseVisaScopeCommand):
    def __init__(self, visa_scope: VisaScope) -> None:
        super().__init__(visa_scope)

    def arm(self) -> str:
        return self.query(cmd = "set_trigger_arm")

    def trig_force(self) -> str:
        return self.query(cmd = "set_trigger_force")

    def clear(self) -> None:
        self.write(cmd ="clear")

    def rabbit(self) -> str: #!ONLY works with new digitizer firmware
        return self.query(cmd= "rabbit")
    
    def is_trig_armed(self) -> str:
        return self.query(cmd = "is_trigger_armed")

    #root params
    @property
    def arm_status(self) -> bool:
        _arm_status = self.query(cmd = "is_trigger_armed")
        return _arm_status.split("|")[2] == "TRUE"

    @property
    def trig_status(self) -> bool:
        _trig_status = self.query(cmd = "is_trigger_armed")
        return _trig_status.split("|")[2] == "FALSE"