class PI_Enum(object):
    
    def __init__(self, name, byname_dict):
        self.name = name
        self.byname = dict(byname_dict)
        self.bysname = dict() # ShortName
        self.bynum  = dict()
        self.bynums  = dict()
        for name, num in self.byname.items():
            self.bynum[num] = name
            sname = name.split('_')[1]
            self.bysname[sname] = num
            self.bynums[num] = sname

PicamErrorEnum = PI_Enum(
    "PicamError", dict (
    #/*------------------------------------------------------------------------*/
    #/* Success ---------------------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamError_None                                  =  0,
    #/*------------------------------------------------------------------------*/
    #/* General Errors --------------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamError_UnexpectedError                       =  4,
    PicamError_UnexpectedNullPointer                 =  3,
    PicamError_InvalidPointer                        = 35,
    PicamError_InvalidCount                          = 39,
    PicamError_EnumerationValueNotDefined            = 17,
    PicamError_InvalidOperation                      = 42,
    PicamError_OperationCanceled                     = 43,
    #/*------------------------------------------------------------------------*/
    #/* Library Initialization Errors -----------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamError_LibraryNotInitialized                 =  1,
    PicamError_LibraryAlreadyInitialized             =  5,
    #/*------------------------------------------------------------------------*/
    #/* General String Handling Errors ----------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamError_InvalidEnumeratedType                 = 16,
    #/*------------------------------------------------------------------------*/
    #/* Camera/Accessory Plug 'n Play Discovery Errors ------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamError_NotDiscoveringCameras                 = 18,
    PicamError_AlreadyDiscoveringCameras             = 19,
    PicamError_NotDiscoveringAccessories             = 48,
    PicamError_AlreadyDiscoveringAccessories         = 49,
    #/*------------------------------------------------------------------------*/
    #/* Camera/Accessory Access Errors ----------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamError_NoCamerasAvailable                    = 34,
    PicamError_CameraAlreadyOpened                   =  7,
    PicamError_InvalidCameraID                       =  8,
    PicamError_NoAccessoriesAvailable                = 45,
    PicamError_AccessoryAlreadyOpened                = 46,
    PicamError_InvalidAccessoryID                    = 47,
    PicamError_InvalidHandle                         =  9,
    PicamError_DeviceCommunicationFailed             = 15,
    PicamError_DeviceDisconnected                    = 23,
    PicamError_DeviceOpenElsewhere                   = 24,
    #/*------------------------------------------------------------------------*/
    #/* Demo Camera Errors ----------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamError_InvalidDemoModel                      =  6,
    PicamError_InvalidDemoSerialNumber               = 21,
    PicamError_DemoAlreadyConnected                  = 22,
    PicamError_DemoNotSupported                      = 40,
    #/*------------------------------------------------------------------------*/
    #/* Camera/Accessory Parameter Access Errors ------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamError_ParameterHasInvalidValueType          = 11,
    PicamError_ParameterHasInvalidConstraintType     = 13,
    PicamError_ParameterDoesNotExist                 = 12,
    PicamError_ParameterValueIsReadOnly              = 10,
    PicamError_InvalidParameterValue                 =  2,
    PicamError_InvalidConstraintCategory             = 38,
    PicamError_ParameterValueIsIrrelevant            = 14,
    PicamError_ParameterIsNotOnlineable              = 25,
    PicamError_ParameterIsNotReadable                = 26,
    PicamError_ParameterIsNotWaitableStatus          = 50,
    PicamError_InvalidWaitableStatusParameterTimeOut = 51,
    #/*------------------------------------------------------------------------*/
    #/* Camera Data Acquisition Errors ----------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamError_InvalidParameterValues                = 28,
    PicamError_ParametersNotCommitted                = 29,
    PicamError_InvalidAcquisitionBuffer              = 30,
    PicamError_InvalidReadoutCount                   = 36,
    PicamError_InvalidReadoutTimeOut                 = 37,
    PicamError_InsufficientMemory                    = 31,
    PicamError_AcquisitionInProgress                 = 20,
    PicamError_AcquisitionNotInProgress              = 27,
    PicamError_TimeOutOccurred                       = 32,
    PicamError_AcquisitionUpdatedHandlerRegistered   = 33,
    PicamError_InvalidAcquisitionState               = 44,
    PicamError_NondestructiveReadoutEnabled          = 41,
    PicamError_ShutterOverheated                     = 52,
    PicamError_CenterWavelengthFaulted               = 54,
    PicamError_CameraFaulted                         = 53
    #/*------------------------------------------------------------------------*/          
    )
)

class PicamError(Exception):
    pass

class PicamFatalError(Exception):
    pass

def error(error):
    if error == 0:
        return error
    elif error in [23, 24]:
        err_str = PicamErrorEnum.bynums[error]
        raise PicamFatalError(err_str)
    else:
        err_str = PicamErrorEnum.bynums[error]
        raise PicamError(err_str)

PicamAcquisitionErrorsMaskEnum = PI_Enum(
    "PicamAcquisitionErrorsMask", dict(
    PicamAcquisitionErrorsMask_None              = 0x00,
    PicamAcquisitionErrorsMask_CameraFaulted     = 0x10,
    PicamAcquisitionErrorsMask_ConnectionLost    = 0x02,
    PicamAcquisitionErrorsMask_ShutterOverheated = 0x08,
    PicamAcquisitionErrorsMask_DataLost          = 0x01,
    PicamAcquisitionErrorsMask_DataNotArriving   = 0x04
    ))

class PicamAcquisitionError(Exception):
    pass
    
def error_acquisition(error):
    if error == 0:
        return error
    else:
        err_str = PicamAcquisitionErrorsMaskEnum.bynums[error]
        raise PicamAcquisitionError(err_str)
    