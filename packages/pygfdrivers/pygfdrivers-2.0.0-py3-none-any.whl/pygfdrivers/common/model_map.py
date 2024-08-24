from pygfdrivers.common.models.infrastructure.repo import BaseRepoModel

from pygfdrivers.keysight.models.scope_config import KeysightScopeConfigModel
from pygfdrivers.keysight.models.scope_data import KeysightScopeDataModel

from pygfdrivers.dtacq.models.scope_config import DtacqScopeConfigModel
from pygfdrivers.dtacq.models.scope_data import DtacqScopeDataModel

from pygfdrivers.lecroy.models.scope_config import LecroyScopeConfigModel
from pygfdrivers.lecroy.models.scope_data import LecroyScopeDataModel

from pygfdrivers.princeton_instruments.models.princeton_camera_config import PrincetonCameraConfigModel

from pygfdrivers.gf.models.digitizer_config import GFDigitizerConfigModel
from pygfdrivers.gf.models.digitizer_data import GFDigitizerDataModel
model_map = {
    'repos' : {
        'base' : BaseRepoModel
    },

    'scopes' : {
        'keysight_visa'     : KeysightScopeConfigModel,
        'dtacq'             : DtacqScopeConfigModel,
        'lecroy_visa'       : LecroyScopeConfigModel,
        'gf_digitizer'      : GFDigitizerConfigModel,
    },

    'cameras' : {
        'princeton_camera'     : PrincetonCameraConfigModel,
    },

    'scope_info' : {
        'keysight_visa'     : KeysightScopeDataModel,
        'dtacq'             : DtacqScopeDataModel,
        'lecroy_visa'       : LecroyScopeDataModel,
        'gf_digitizer'      : GFDigitizerDataModel,
    }
}