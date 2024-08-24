from pygfdrivers.dtacq.site_modules.acq425 import ACQ425
from pygfdrivers.dtacq.site_modules.acq480 import ACQ480
# from .ao424 import AO424
# from .acq423 import ACQ423

modules_map = {
    'A5': ACQ425,
    '08': ACQ480,
    # '41'    : AO424,
    # '09'    : ACQ423
    }
