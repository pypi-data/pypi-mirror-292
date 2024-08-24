from pygfdrivers.dtacq.dtacq_scope import DtacqScope
from pygfdrivers.gf.gf_visa_digitizer import GFVisaDigitizer
from pygfdrivers.lecroy.lecroy_visa_scope import LecroyVisaScope
from pygfdrivers.avantes.avantes_spectro import AvantesSpectrometer
from pygfdrivers.keysight.keysight_visa_scope import KeysightVisaScope
from pygfdrivers.princeton_instruments.princeton_camera import PrincetonCamera


device_map = {
    'scopes' : {
        'keysight_visa'         : KeysightVisaScope,
        'lecroy_visa'           : LecroyVisaScope,
        'dtacq'                 : DtacqScope,
        'gf_digitizer'          : GFVisaDigitizer,
        'avantes_spectrometer'  : AvantesSpectrometer,
    },
    'cameras' : {
        'princeton_camera'      : PrincetonCamera
    }
}
