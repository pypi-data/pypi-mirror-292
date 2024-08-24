import ctypes
from ctypes import byref
import platform
import os
import pygfdrivers.princeton_instruments.picam.picam_ctypes as picam_ctypes
from pygfdrivers.princeton_instruments.picam.picam_error import *

"""
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/* General Library Usage - Error Codes, Version, Initialization and Strings   */
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
"""

LIBRARY_PATH = "C:/Program Files/Princeton Instruments/PICam/Runtime/Picam.dll"

def getDLLPath(subfolder):
    arch = platform.architecture()[0]
    winarch = "64bit" if platform.machine().endswith("64") else "32bit"
    if arch == "32bit" and winarch=="64bit":
        prgm = os.environ.get("PROGRAMFILES(X86)",r"C:\Program Files (x86)")
    else:
        prgm = os.environ.get("PROGRAMFILES",r"C:\Program Files")
    return os.path.join(prgm , subfolder)
    
def loadLibrary(path):
    add_paths=[os.path.abspath(p) for p in os.environ.get("PATH","").split(os.pathsep) if p]
    add_paths+=[os.path.abspath(".")]
    added_dirs=[]
    try:
        for p in add_paths:
            try:
                added_dirs.append(os.add_dll_directory(p))
            except OSError:  # missing folder
                pass
        return ctypes.windll.LoadLibrary(path)
    finally:
        for d in added_dirs:
            d.close()

def loadPicamLibrary():
    lib_name = "picam.dll" if platform.architecture()[0][:2] =="64" else "picam32.dll"
    subfolder = os.path.join("Princeton Instruments/PICam/Runtime", lib_name)
    path = getDLLPath(subfolder)
    return loadLibrary(path)

lib = loadPicamLibrary()

def GetVersion():
    major = picam_ctypes.piint()
    minor = picam_ctypes.piint()
    distribution = picam_ctypes.piint()
    released = picam_ctypes.piint()
    error(lib.Picam_GetVersion(byref(major), byref(minor), byref(distribution), byref(released)))
    return major.value, minor.value, distribution.value, released.value

def IsLibraryInitialized():
    inited = ctypes.pibln()
    error(lib.Picam_IsLibraryInitialized(byref(inited)))
    return bool(inited.value)

def InitializeLibrary():
    error(lib.Picam_InitializeLibrary())

def UninitializeLibrary():
    error(lib.Picam_UninitializeLibrary())

def DestroyString(s):
    error(lib.Picam_DestroyString(s))

def GetEnumerationString(type, value):
    s = picam_ctypes.pichar_p()
    error(lib.Picam_GetEnumerationString(type, value, byref(s)))
    return s.value.decode('utf-8') if s.value else None

"""
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/* Camera Identification, Access, Information and Demo                        */
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
"""

def CreateCameraID(serial_number = None, model = 1203, computer_interface = 3, sensor_name = b'Null'):
    try:
        if isinstance(model, str):
            model = picam_ctypes.PicamModelEnum.bysname[model]
        if isinstance(computer_interface, str):
            computer_interface = picam_ctypes.PicamComputerInterfaceEnum.bysname[computer_interface]

        serial_number = serial_number.encode() if isinstance(serial_number, str) else serial_number
        sensor_name = sensor_name.encode() if isinstance(sensor_name, str) else sensor_name
        return picam_ctypes.PicamCameraID(model, computer_interface, sensor_name, serial_number)
    except Exception as e:
        raise PicamError(f"invalid camera ID: {e}")

def DestroyCameraIDs(id_array):
    error(lib.Picam_DestroyCameraIDs(id_array))

def GetAvailableCameraIDs():
    id_array = ctypes.POINTER(picam_ctypes.PicamCameraID)()
    id_count = picam_ctypes.piint()
    error(lib.Picam_GetAvailableCameraIDs(byref(id_array), byref(id_count)))
    return id_array.contents, id_count.value

def GetUnavailableCameraIDs():
    id_array = picam_ctypes.PicamCameraID()
    id_count = picam_ctypes.piint()
    error(lib.Picam_GetUnavailableCameraIDs(byref(id_array), byref(id_count)))
    return id_array, id_count.value

def IsCameraIDConnected(id):
    connected = picam_ctypes.pibln()
    error(lib.Picam_IsCameraIDConnected(id, byref(connected)))
    return bool(connected.value)

def IsCameraIDOpenElsewhere(id):
    open_elsewhere = picam_ctypes.pibln()
    error(lib.Picam_IsCameraIDOpenElsewhere(id, byref(open_elsewhere)))
    return bool(open_elsewhere.value)

def DestroyHandles(handle_array):
    error(lib.Picam_DestroyHandles(handle_array))

def OpenFirstCamera():
    camera = picam_ctypes.PicamHandle()
    error(lib.Picam_OpenFirstCamera(byref(camera)))
    return camera

def OpenCamera(camera_id = None, serial_number = None, model = 1203, computer_interface = 3, sensor_name = b'Null') -> picam_ctypes.PicamHandle:
    #defaults to model and interface for ProEMHS512BExcelon, Ethernet Connection

    if camera_id is None:
        camera_id = CreateCameraID(serial_number, model, computer_interface, sensor_name)
    camera = picam_ctypes.PicamHandle()
    error(lib.Picam_OpenCamera(camera_id, byref(camera)))
    return camera

def CloseCamera(camera):
    error(lib.Picam_CloseCamera(camera))

def GetOpenCameras():
    camera_array = picam_ctypes.PicamHandle_p()
    camera_count = picam_ctypes.piint()
    error(lib.Picam_GetOpenCameras(byref(camera_array), byref(camera_count)))
    return camera_array, camera_count.value

def IsCameraConnected(camera):
    connected = picam_ctypes.pibln()
    error(lib.Picam_IsCameraConnected(camera, byref(connected)))
    return bool(connected.value)

def IsCameraFaulted(camera):
    faulted = picam_ctypes.pibln()
    error(lib.Picam_IsCameraFaulted(camera, byref(faulted)))
    return bool(faulted.value)

def GetCameraID(camera):
    id = picam_ctypes.PicamCameraID()
    error(lib.Picam_GetCameraID(camera, byref(id)))
    return id

def DestroyFirmwareDetails(firmware_array):
    error(lib.Picam_DestroyFirmwareDetails(firmware_array))

def GetFirmwareDetails(id):
    firmware_array = picam_ctypes.PicamFirmwareDetail()
    firmware_count = picam_ctypes.piint()
    error(lib.Picam_GetFirmwareDetails(id, byref(firmware_array), byref(firmware_count)))
    return firmware_array, firmware_count.value

def DestroyCalibrations(calibration_array):
    error(lib.Picam_DestroyCalibrations(calibration_array))

def DestroyModels(model_array):
    error(lib.Picam_DestroyModels(model_array))

def GetAvailableDemoCameraModels():
    model_array = ctypes.POINTER(picam_ctypes.piint)()
    model_count = picam_ctypes.piint()
    error(lib.Picam_GetAvailableDemoCameraModels(byref(model_array), byref(model_count)))
    models = ctypes.cast(model_array, ctypes.POINTER(picam_ctypes.piint*model_count.value)).contents
    for i in models:
        if i in picam_ctypes.PicamModelEnum.bynums:
            print(i, ": ", picam_ctypes.PicamModelEnum.bynums[i])

def ConnectDemoCamera(model, serial_number):
    id = picam_ctypes.PicamCameraID()
    error(lib.Picam_ConnectDemoCamera(model, serial_number, byref(id)))
    return id

def DisconnectDemoCamera(id):
    error(lib.Picam_DisconnectDemoCamera(byref(id)))

def IsDemoCamera(id):
    demo = picam_ctypes.pibln()
    error(lib.Picam_IsDemoCamera(byref(id), byref(demo)))
    return bool(demo.value)

"""
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/* Camera/Accessory Parameter Values, Information, Constraints and Commitment */
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
"""

def SetParameterValue(camera, pname, value):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    ptype = parameter.param_type
    if ptype in ['Integer', 'i','I', int]:
        if not CanSetParameterIntegerValue(camera, parameter.enum, value):
            raise ValueError(f"Failed Writing {pname}: {value} to {camera}" )
        SetParameterIntegerValue(camera, parameter.enum, value)
    elif ptype in ['FloatingPoint', 'f','F',float]:
        if not CanSetParameterFloatingPointValue(camera, parameter.enum, value):
            raise ValueError(f"Failed Writing {pname}: {value} to {camera}" )
        SetParameterFloatingPointValue(camera, parameter.enum, value)        
    elif ptype in ['Enumeration']:
        if type(value) is str:
            enum_obj = getattr(picam_ctypes, parameter.enum_type)
            value = enum_obj.bysname[value]
        if not CanSetParameterIntegerValue(camera, parameter.enum, value):
            raise ValueError(f"Failed Writing {pname}: {value} to {camera}" )
        SetParameterIntegerValue(camera, parameter.enum, value)
    elif ptype in ['Boolean']:
        if not CanSetParameterIntegerValue(camera, parameter.enum, value):
            raise ValueError(f"Failed Writing {pname}: {value} to {camera}" )
        SetParameterIntegerValue(camera, parameter.enum, value)
    elif ptype in ['LargeInteger']:
        if not CanSetParameterLargeIntegerValue(camera, parameter.enum, value):
            raise ValueError(f"Failed Writing {pname}: {value} to {camera}" )
        SetParameterLargeIntegerValue(camera, parameter.enum, value)
    elif ptype in ['Rois']:
        roi_array = (picam_ctypes.PicamRoi * len(value))()
        for i, roi_data in enumerate(value):
            roi = picam_ctypes.PicamRoi(
                roi_data["x"], roi_data["width"], roi_data["x_binning"],
                roi_data["y"], roi_data["height"], roi_data["y_binning"]
            )
            roi_array[i] = roi
        rois = picam_ctypes.PicamRois(roi_array, len(value))
        if not CanSetParameterRoisValue(camera, parameter.enum, rois):
            raise ValueError(f"Failed Writing {pname}: {value} to {camera}" )
        SetParameterRoisValue(camera, parameter.enum, rois)
    else:
        raise TypeError("Invalid Picam Parameter Type")
    
def GetParameterValue(camera, pname):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    ptype = parameter.param_type
    if ptype in ['Integer', 'i','I', int]:
        return GetParameterIntegerValue(camera, parameter.enum)
    elif ptype in ['LargeInteger']:
        return GetParameterLargeIntegerValue(camera, parameter.enum) 
    elif ptype in ['FloatingPoint', 'f','F',float]:  
        return GetParameterFloatingPointValue(camera, parameter.enum)
    elif ptype in ['Enumeration']:
        enum_obj = getattr(picam_ctypes, parameter.enum_type)
        value = GetParameterIntegerValue(camera, parameter.enum)
        return value
        # return enum_obj.bynums[value]
    elif ptype in ['Boolean']:
        value = GetParameterIntegerValue(camera, parameter.enum)
        return bool(value)
    elif ptype in ['Rois']:
        rois = []
        value = GetParameterRoisValue(camera)
        count = value.roi_count
        for i, roi in enumerate(value.roi_array):
            if i >= count:
                break
            roi = {"x": roi.x, "width": roi.width, "x_binning": roi.x_binning, "y": roi.y, "height": roi.height, "y_binning": roi.y_binning}
            rois.append(roi)
        return rois
    else:
        raise TypeError(f"{pname} Invalid Picam Parameter Type")
    
def GetAllParameters(camera):
        param_dict = {}
        param_array, count = GetParameters(camera)
        parameters = ctypes.cast(param_array, ctypes.POINTER(ctypes.c_int * count)).contents
        for i in parameters:
            if i in picam_ctypes.PicamParameterEnum.bynums:
                pname = picam_ctypes.PicamParameterEnum.bynums[i]
                value = GetParameterValue(camera, pname)
                param_dict[pname] = value
        DestroyParameters(param_array)
        return param_dict

def ReadParameterValue(camera, pname):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    ptype = parameter.param_type
    if not CanReadParameter(camera, parameter.enum):
        raise ValueError(f"{pname} is not a read-only parameter")
    if ptype in ['Integer', 'i','I', int]:
        return ReadParameterIntegerValue(camera, parameter.enum)
    elif ptype in ['FloatingPoint', 'f','F',float]:  
        return ReadParameterFloatingPointValue(camera, parameter.enum)
    elif ptype in ['Enumeration']:
        enum_obj = getattr(picam_ctypes, parameter.enum_type)
        value = ReadParameterIntegerValue(camera, parameter.enum)
        return enum_obj.bynums[value]
    elif ptype in ['Boolean']:
        value = ReadParameterIntegerValue(camera, parameter.enum)
        return bool(value)
    else:
        raise TypeError(f"{pname} Invalid Picam Parameter Type")

def GetParameterIntegerValue(camera, parameter):
    value = picam_ctypes.piint()
    error(lib.Picam_GetParameterIntegerValue(camera, parameter, byref(value)))
    return value.value

def SetParameterIntegerValue(camera, parameter, value):
    error(lib.Picam_SetParameterIntegerValue(camera, parameter, picam_ctypes.piint(value)))

def CanSetParameterIntegerValue(camera, parameter, value):
    settable = picam_ctypes.piint()
    error(lib.Picam_CanSetParameterIntegerValue(camera, parameter, picam_ctypes.piint(value), byref(settable)))
    return bool(settable.value)

def GetParameterLargeIntegerValue(camera, parameter):
    value = picam_ctypes.pi64s()
    error(lib.Picam_GetParameterLargeIntegerValue(camera, parameter, byref(value)))
    return value.value

def SetParameterLargeIntegerValue(camera, parameter, value):
    error(lib.Picam_SetParameterLargeIntegerValue(camera, parameter, picam_ctypes.pi64s(value)))

def CanSetParameterLargeIntegerValue(camera, parameter, value):
    settable = picam_ctypes.piint()
    error(lib.Picam_CanSetParameterLargeIntegerValue(camera, parameter, picam_ctypes.pi64s(value), byref(settable)))
    return bool(settable.value)

def GetParameterFloatingPointValue(camera, parameter):
    value = picam_ctypes.piflt()
    error(lib.Picam_GetParameterFloatingPointValue(camera, parameter, byref(value)))
    return value.value

def SetParameterFloatingPointValue(camera, parameter, value):
    error(lib.Picam_SetParameterFloatingPointValue(camera, parameter, picam_ctypes.piflt(value)))

def CanSetParameterFloatingPointValue(camera, parameter, value):
    settable = picam_ctypes.piint()
    error(lib.Picam_CanSetParameterFloatingPointValue(camera, parameter, picam_ctypes.piflt(value), byref(settable)))
    return bool(settable.value)

def DestroyRois(rois):
    error(lib.Picam_DestroyRois(rois))

def GetParameterRoisValue(camera):
    parameter = picam_ctypes.PicamParameter["PicamParameter_Rois"]
    value = ctypes.POINTER(picam_ctypes.PicamRois)()
    error(lib.Picam_GetParameterRoisValue(camera, parameter.enum, byref(value)))
    return value.contents

def SetParameterRoisValue(camera, parameter, rois):
    error(lib.Picam_SetParameterRoisValue(camera, parameter, byref(rois)))

def CanSetParameterRoisValue(camera, parameter, rois):
    settable = picam_ctypes.piint()
    error(lib.Picam_CanSetParameterRoisValue(camera, parameter, byref(rois), byref(settable)))
    return bool(settable.value)

def DestroyPulses(pulses):
    lib.Picam_DestroyPulses(pulses)

def GetParameterPulseValue(camera, pname):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    value = ctypes.POINTER(picam_ctypes.PicamPulse)()
    error(lib.Picam_GetParameterPulseValue(camera, parameter.enum, byref(value)))
    return value.contents

def SetParameterPulseValue(camera, pname, value):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    error(lib.Picam_SetParameterPulseValue(camera, parameter.enum, value))

def CanSetParameterPulseValue(camera, pname, value):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    settable = ctypes.c_int()
    error(lib.Picam_CanSetParameterPulseValue(camera, parameter.enum, value, byref(settable)))
    return bool(settable.value)

def DestroyModulations(modulations):
    lib.Picam_DestroyModulations(modulations)

def GetParameterModulationsValue(camera, pname):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    value = ctypes.POINTER(picam_ctypes.PicamModulations)()
    error(lib.Picam_GetParameterModulationsValue(camera, parameter.enum, byref(value)))
    return value.contents

def SetParameterModulationsValue(camera, pname, value):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    error(lib.Picam_SetParameterModulationsValue(camera, parameter.enum, value))

def CanSetParameterModulationsValue(camera, pname, value):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    settable = ctypes.c_int()
    error(lib.Picam_CanSetParameterModulationsValue(camera, parameter.enum, value, byref(settable)))
    return bool(settable.value)

def GetParameterIntegerDefaultValue(camera, pname):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    value = ctypes.c_int()
    error(lib.Picam_GetParameterIntegerDefaultValue(camera, parameter.enum, byref(value)))
    return value.value

def GetParameterLargeIntegerDefaultValue(camera, pname):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    value = ctypes.c_int64()
    error(lib.Picam_GetParameterLargeIntegerDefaultValue(camera, parameter.enum, byref(value)))
    return value.value

def GetParameterFloatingPointDefaultValue(camera, pname):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    value = ctypes.c_double()
    error(lib.Picam_GetParameterFloatingPointDefaultValue(camera, parameter.enum, byref(value)))
    return value.value

def GetParameterRoisDefaultValue(camera, pname):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    value = ctypes.POINTER(picam_ctypes.PicamRois)()
    error(lib.Picam_GetParameterRoisDefaultValue(camera, parameter.enum, byref(value)))
    return value.contents

def GetParameterPulseDefaultValue(camera, pname):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    value = ctypes.POINTER(picam_ctypes.PicamPulse)()
    error(lib.Picam_GetParameterPulseDefaultValue(camera, parameter.enum, byref(value)))
    return value.contents

def GetParameterModulationsDefaultValue(camera, pname):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    value = ctypes.POINTER(picam_ctypes.PicamModulations)()
    error(lib.Picam_GetParameterModulationsDefaultValue(camera, parameter.enum, byref(value)))
    return value.contents

def RestoreParametersToDefaultValues(camera):
    error(lib.Picam_RestoreParametersToDefaultValues(camera))

def CanSetParameterOnline(camera, pname):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    onlineable = ctypes.c_int()
    error(lib.Picam_CanSetParameterOnline(camera, parameter.enum, byref(onlineable)))
    return bool(onlineable.value)

def SetParameterIntegerValueOnline(camera, pname, value):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    error(lib.Picam_SetParameterIntegerValueOnline(camera, parameter.enum, picam_ctypes.piint(value)))

def SetParameterFloatingPointValueOnline(camera, pname, value):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    error(lib.Picam_SetParameterFloatingPointValueOnline(camera, parameter.enum, picam_ctypes.piflt(value)))

def SetParameterPulseValueOnline(camera, pname, value):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    error(lib.Picam_SetParameterPulseValueOnline(camera, parameter.enum, value))

def CanReadParameter(camera, parameter):
    readable = ctypes.c_int()
    error(lib.Picam_CanReadParameter(camera, parameter, byref(readable)))
    return bool(readable.value)

def ReadParameterIntegerValue(camera, parameter):
    value = ctypes.c_int()
    error(lib.Picam_ReadParameterIntegerValue(camera, parameter, byref(value)))
    return value.value

def ReadParameterFloatingPointValue(camera, parameter):
    value = ctypes.c_double()
    error(lib.Picam_ReadParameterFloatingPointValue(camera, parameter, byref(value)))
    return value.value

def CanWaitForStatusParameter(camera, pname):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    waitable = ctypes.c_int()
    error(lib.Picam_CanWaitForStatusParameter(camera, parameter.enum, byref(waitable)))
    return bool(waitable.value)

def DestroyStatusPurviews(purviews_array):
    lib.Picam_DestroyStatusPurviews(purviews_array)

def GetStatusParameterPurview(camera, pname):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    purview = ctypes.POINTER(picam_ctypes.PicamStatusPurview)()
    error(lib.Picam_GetStatusParameterPurview(camera, parameter.enum, byref(purview)))
    return purview.contents

def EstimateTimeToStatusParameterValue(camera, parameter, value):
    estimated_time = ctypes.c_int()
    error(lib.Picam_EstimateTimeToStatusParameterValue(camera, parameter, value, byref(estimated_time)))
    return estimated_time.value

def WaitForStatusParameterValue(camera, pname, value, time_out):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    error(lib.Picam_WaitForStatusParameterValue(camera, parameter.enum, value, time_out))

def DestroyParameters(parameter_array):
    error(lib.Picam_DestroyParameters(parameter_array))

def GetParameters(camera):
    parameter_array = ctypes.POINTER(ctypes.c_int)()
    parameter_count = ctypes.c_int()
    error(lib.Picam_GetParameters(camera, byref(parameter_array), byref(parameter_count)))
    return parameter_array, parameter_count.value

def DoesParameterExist(camera, pname):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    exists = ctypes.c_int()
    error(lib.Picam_DoesParameterExist(camera, parameter.enum, byref(exists)))
    return bool(exists.value)

def IsParameterRelevant(camera, pname):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    relevant = ctypes.c_int()
    error(lib.Picam_IsParameterRelevant(camera, parameter.enum, byref(relevant)))
    return bool(relevant.value)

def GetParameterValueType(camera, pname):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    value_type = ctypes.c_int()
    error(lib.Picam_GetParameterValueType(camera, parameter.enum, byref(value_type)))
    return value_type.value

def GetParameterEnumeratedType(camera, pname):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    enumerated_type = ctypes.c_int()
    error(lib.Picam_GetParameterEnumeratedType(camera, parameter.enum, byref(enumerated_type)))
    return enumerated_type.value

def GetParameterValueAccess(camera, pname):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    access = ctypes.c_int()
    error(lib.Picam_GetParameterValueAccess(camera, parameter.enum, byref(access)))
    return access.value

def GetParameterConstraintType(camera, pname):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    constraint_type = ctypes.c_int()
    error(lib.Picam_GetParameterConstraintType(camera, parameter.enum, byref(constraint_type)))
    return constraint_type.value

def GetParameterValueAccess(camera, pname):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    access = picam_ctypes.PicamValueAccess()
    error(lib.Picam_GetParameterValueAccess(camera, parameter.enum, byref(access)))
    return access.value

def GetParameterConstraintType(camera, pname):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    constraint_type = picam_ctypes.PicamConstraintType()
    error(lib.Picam_GetParameterConstraintType(camera, parameter.enum, byref(constraint_type)))
    return constraint_type.value

def DestroyCollectionConstraints(constraint_array):
    lib.Picam_DestroyCollectionConstraints(constraint_array)

def GetParameterCollectionConstraint(camera, pname, category):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    constraint = ctypes.POINTER(ctypes.POINTER(picam_ctypes.PicamCollectionConstraint))()
    error(lib.Picam_GetParameterCollectionConstraint(camera, parameter.enum, category, byref(constraint)))
    return constraint.contents

def DestroyRangeConstraints(constraint_array):
    lib.Picam_DestroyRangeConstraints(constraint_array)

def GetParameterRangeConstraint(camera, pname, category):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    constraint = ctypes.POINTER(ctypes.POINTER(picam_ctypes.PicamRangeConstraint))()
    error(lib.Picam_GetParameterRangeConstraint(camera, parameter.enum, category, byref(constraint)))
    return constraint.contents

def DestroyRoisConstraints(constraint_array):
    lib.Picam_DestroyRoisConstraints(constraint_array)

def GetParameterRoisConstraint(camera, pname, category):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    constraint = ctypes.POINTER(ctypes.POINTER(picam_ctypes.PicamRoisConstraint))()
    error(lib.Picam_GetParameterRoisConstraint(camera, parameter.enum, category, byref(constraint)))
    return constraint.contents

def DestroyPulseConstraints(constraint_array):
    lib.Picam_DestroyPulseConstraints(constraint_array)

def GetParameterPulseConstraint(camera, pname, category):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    constraint = ctypes.POINTER(ctypes.POINTER(picam_ctypes.PicamPulseConstraint))()
    error(lib.Picam_GetParameterPulseConstraint(camera, parameter.enum, category, byref(constraint)))
    return constraint.contents

def DestroyModulationsConstraints(constraint_array):
    lib.Picam_DestroyModulationsConstraints(constraint_array)

def GetParameterModulationsConstraint(camera, pname, category):
    parameter = picam_ctypes.PicamParameter["PicamParameter_" + pname]
    constraint = ctypes.POINTER(ctypes.POINTER(picam_ctypes.PicamModulationsConstraint))()
    error(lib.Picam_GetParameterModulationsConstraint(camera, parameter.enum, category, byref(constraint)))
    return constraint.contents

def AreParametersCommitted(camera):
    committed = ctypes.c_int()
    error(lib.Picam_AreParametersCommitted(camera, byref(committed)))
    return bool(committed.value)

def CommitParameters(camera):
    parameter_pointer = ctypes.POINTER(picam_ctypes.piint)()
    parameter_count = picam_ctypes.piint()
    failed_parameters = []
    try:
        error(lib.Picam_CommitParameters(camera, byref(parameter_pointer), byref(parameter_count)))
    except Exception as e:
        parameters = ctypes.cast(parameter_pointer, ctypes.POINTER(picam_ctypes.piint*parameter_count.value)).contents
        for i in parameters:
            if i in picam_ctypes.PicamParameterEnum.bynums:
                failed_parameters.append(picam_ctypes.PicamParameterEnum.bynums[i])
        raise PicamError(f"{e}: {failed_parameters}")
    
"""
/*----------------------------------------------------------------------------*/

/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/* Camera Data Acquisition                                                    */
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
"""

def Acquire(camera, readout_count, readout_time_out):
    readout_count = picam_ctypes.pi64s(readout_count)
    readout_time_out = picam_ctypes.piint(readout_time_out)
    available = picam_ctypes.PicamAvailableData()
    errors = picam_ctypes.piint()
    error(lib.Picam_Acquire(camera, readout_count, readout_time_out, byref(available), byref(errors)))
    return available, errors.value

def StartAcquisition(camera):
    error(lib.Picam_StartAcquisition(camera))

def StopAcquisition(camera):
    error(lib.Picam_StopAcquisition(camera))

def IsAcquisitionRunning(camera):
    running = ctypes.c_int()
    error(lib.Picam_IsAcquisitionRunning(camera, byref(running)))
    return bool(running.value)

def WaitForAcquisitionUpdate(camera, readout_time_out):
    readout_time_out = picam_ctypes.piint(readout_time_out)
    available = picam_ctypes.PicamAvailableData()
    status = picam_ctypes.PicamAcquisitionStatus()
    error(lib.Picam_WaitForAcquisitionUpdate(camera, readout_time_out, byref(available), byref(status)))
    return available, status

