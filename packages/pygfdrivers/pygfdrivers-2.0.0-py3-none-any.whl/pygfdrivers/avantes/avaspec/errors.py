from enum import Enum
from typing import Union, Tuple
from ctypes import Structure, Array


class AvsErrorEnum(Enum):
    """
    ENUM class for all known error codes that AVS function calls could return. The values for this
    class were obtained from the C header file for avaspec python module.
    """

    # Avs return error codes
    ERR_SUCCESS = 0     # Not an actual error, just a success code
    ERR_INVALID_PARAMETER = -1
    ERR_OPERATION_NOT_SUPPORTED = -2
    ERR_DEVICE_NOT_FOUND = -3
    ERR_INVALID_DEVICE_ID = -4
    ERR_OPERATION_PENDING = -5
    ERR_TIMEOUT = -6
    ERR_INVALID_PASSWORD = -7
    ERR_INVALID_MEAS_DATA = -8
    ERR_INVALID_SIZE = -9
    ERR_INVALID_PIXEL_RANGE = -10
    ERR_INVALID_INT_TIME = -11
    ERR_INVALID_COMBINATION = -12
    ERR_INVALID_CONFIGURATION = -13
    ERR_NO_MEAS_BUFFER_AVAIL = -14
    ERR_UNKNOWN = -15
    ERR_COMMUNICATION = -16
    ERR_NO_SPECTRA_IN_RAM = -17
    ERR_INVALID_DLL_VERSION = -18
    ERR_NO_MEMORY = -19
    ERR_DLL_INITIALISATION = -20
    ERR_INVALID_STATE = -21
    ERR_INVALID_REPLY = -22
    ERR_CONNECTION_FAILURE = ERR_COMMUNICATION
    ERR_ACCESS = -24
    ERR_INTERNAL_READ = -25
    ERR_INTERNAL_WRITE = -26
    ERR_ETHCONN_REUSE = -27
    ERR_INVALID_DEVICE_TYPE = -28
    ERR_SECURE_CFG_NOT_READ = -29
    ERR_UNEXPECTED_MEAS_RESPONSE = -30
    ERR_MEAS_STOPPED = -31

    # Return error codes; DeviceData check
    ERR_INVALID_PARAMETER_NR_PIXELS = -100
    ERR_INVALID_PARAMETER_ADC_GAIN = -101
    ERR_INVALID_PARAMETER_ADC_OFFSET = -102

    # Return error codes; PrepareMeasurement check
    ERR_INVALID_MEASPARAM_AVG_SAT2 = -110
    ERR_INVALID_MEASPARAM_AVG_RAM = -111
    ERR_INVALID_MEASPARAM_SYNC_RAM = -112
    ERR_INVALID_MEASPARAM_LEVEL_RAM = -113
    ERR_INVALID_MEASPARAM_SAT2_RAM = -114
    ERR_INVALID_MEASPARAM_FWVER_RAM = -115
    ERR_INVALID_MEASPARAM_DYNDARK = -116

    # Return error codes; SetSensitivityMode check
    ERR_NOT_SUPPORTED_BY_SENSOR_TYPE = -120
    ERR_NOT_SUPPORTED_BY_FW_VER = -121
    ERR_NOT_SUPPORTED_BY_FPGA_VER = -122

    # Return error codes; SuppressStrayLight check
    ERR_SL_CALIBRATION_NOT_AVAILABLE = -140
    ERR_SL_STARTPIXEL_NOT_IN_RANGE = -141
    ERR_SL_ENDPIXEL_NOT_IN_RANGE = -142
    ERR_SL_STARTPIX_GT_ENDPIX = -143
    ERR_SL_MFACTOR_OUT_OF_RANGE = -144

    # Connection status codes
    ETH_CONN_STATUS_CONNECTING = 0  # Waiting to establish ethernet connection
    ETH_CONN_STATUS_CONNECTED = 1  # Eth connection established, with recovery
    ETH_CONN_STATUS_CONNECTED_NOMON = 2  # Eth connection ready, no recovery
    ETH_CONN_STATUS_NOCONNECTION = 3  # Unrecoverable connection failure


class AvsError(Exception):
    """Base class for Avs errors."""
    def __init__(self, code: AvsErrorEnum, message="Avs error occurred"):
        self.code = code
        self.message = message or code.name
        super().__init__(f"AvaSpecError - [{code.name}({code.value})] - {message}")


class ErrSuccess(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_SUCCESS, "Success")


class ErrInvalidParameter(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_PARAMETER, "Invalid parameter")


class ErrOperationNotSupported(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_OPERATION_NOT_SUPPORTED, "Operation not supported")


class ErrDeviceNotFound(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_DEVICE_NOT_FOUND, "Device not found")


class ErrInvalidDeviceId(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_DEVICE_ID, "Invalid device ID")


class ErrOperationPending(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_OPERATION_PENDING, "Operation pending")


class ErrTimeout(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_TIMEOUT, "Timeout")


class ErrInvalidPassword(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_PASSWORD, "Invalid password")


class ErrInvalidMeasData(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_MEAS_DATA, "Invalid measurement data")


class ErrInvalidSize(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_SIZE, "Invalid size")


class ErrInvalidPixelRange(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_PIXEL_RANGE, "Invalid pixel range")


class ErrInvalidIntTime(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_INT_TIME, "Invalid integration time")


class ErrInvalidCombination(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_COMBINATION, "Invalid combination")


class ErrInvalidConfiguration(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_CONFIGURATION, "Invalid configuration")


class ErrNoMeasBufferAvail(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_NO_MEAS_BUFFER_AVAIL, "No measurement buffer available")


class ErrUnknown(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_UNKNOWN, "Unknown error")


class ErrCommunication(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_COMMUNICATION, "Communication error")


class ErrNoSpectraInRam(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_NO_SPECTRA_IN_RAM, "No spectra in RAM")


class ErrInvalidDllVersion(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_DLL_VERSION, "Invalid DLL version")


class ErrNoMemory(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_NO_MEMORY, "No memory")


class ErrDllInitialisation(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_DLL_INITIALISATION, "DLL initialisation error")


class ErrInvalidState(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_STATE, "Invalid state")


class ErrInvalidReply(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_REPLY, "Invalid reply")


class ErrConnectionFailure(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_CONNECTION_FAILURE, "Connection failure")


class ErrAccess(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_ACCESS, "Access error")


class ErrInternalRead(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INTERNAL_READ, "Internal read error")


class ErrInternalWrite(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INTERNAL_WRITE, "Internal write error")


class ErrEthConnReuse(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_ETHCONN_REUSE, "Ethernet connection reuse error")


class ErrInvalidDeviceType(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_DEVICE_TYPE, "Invalid device type")


class ErrSecureCfgNotRead(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_SECURE_CFG_NOT_READ, "Secure configuration not read")


class ErrUnexpectedMeasResponse(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_UNEXPECTED_MEAS_RESPONSE, "Unexpected measurement response")


class ErrMeasStopped(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_MEAS_STOPPED, "Measurement stopped")


# DeviceData check error codes
class ErrInvalidParameterNrPixels(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_PARAMETER_NR_PIXELS, "Invalid parameter: number of pixels")


class ErrInvalidParameterAdcGain(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_PARAMETER_ADC_GAIN, "Invalid parameter: ADC gain")


class ErrInvalidParameterAdcOffset(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_PARAMETER_ADC_OFFSET, "Invalid parameter: ADC offset")


# PrepareMeasurement check error codes
class ErrInvalidMeasParamAvgSat2(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_MEASPARAM_AVG_SAT2, "Invalid measurement parameter: AVG SAT2")


class ErrInvalidMeasParamAvgRam(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_MEASPARAM_AVG_RAM, "Invalid measurement parameter: AVG RAM")


class ErrInvalidMeasParamSyncRam(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_MEASPARAM_SYNC_RAM, "Invalid measurement parameter: SYNC RAM")


class ErrInvalidMeasParamLevelRam(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_MEASPARAM_LEVEL_RAM, "Invalid measurement parameter: LEVEL RAM")


class ErrInvalidMeasParamSat2Ram(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_MEASPARAM_SAT2_RAM, "Invalid measurement parameter: SAT2 RAM")


class ErrInvalidMeasParamFwverRam(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_MEASPARAM_FWVER_RAM, "Invalid measurement parameter: FWVER RAM")


class ErrInvalidMeasParamDynDark(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_INVALID_MEASPARAM_DYNDARK, "Invalid measurement parameter: Dynamic dark")


# SetSensitivityMode check error codes
class ErrNotSupportedBySensorType(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_NOT_SUPPORTED_BY_SENSOR_TYPE, "Not supported by sensor type")


class ErrNotSupportedByFwVer(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_NOT_SUPPORTED_BY_FW_VER, "Not supported by firmware version")


class ErrNotSupportedByFpgaVer(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_NOT_SUPPORTED_BY_FPGA_VER, "Not supported by FPGA version")


# SuppressStrayLight check error codes
class ErrSlCalibrationNotAvailable(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_SL_CALIBRATION_NOT_AVAILABLE, "Stray light calibration not available")


class ErrSlStartPixelNotInRange(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_SL_STARTPIXEL_NOT_IN_RANGE, "Stray light start pixel not in range")


class ErrSlEndPixelNotInRange(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_SL_ENDPIXEL_NOT_IN_RANGE, "Stray light end pixel not in range")


class ErrSlStartPixGtEndPix(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_SL_STARTPIX_GT_ENDPIX, "Stray light start pixel greater than end pixel")


class ErrSlMfactorOutOfRange(AvsError):
    def __init__(self):
        super().__init__(AvsErrorEnum.ERR_SL_MFACTOR_OUT_OF_RANGE, "Stray light MFactor out of range")


def enum_avs_err(ret: Union[str, int]) -> Union[int, Tuple[int, Array], Structure, Array]:
    """
    Check the return value of an Avs function call and raise the appropriate exception if an error occurred.

    Args:
        ret (Union[str, int]): The return value of an AVS function call.

    Return:
        Union[int, Tuple[int, Array], Structure, Array]: The return value of an AVS function call if
        return value of an AVS function is not an integer below 0.

    Notes:
        - More information about possible return value can be found in avaspec.py
    """

    # Return value from AVS_GetScopeData() so we treat this one differently as it is never an error code
    if isinstance(ret, tuple):
        return ret[0], ret[1]

    # Error message passed can sometimes either be a single integer or string, so we have
    # to account for both cases, as we need to extract the integer error code.
    elif isinstance(ret, (int, str)):
        try:
            ret = int(ret)

            # Return values equal 0 or higher mean a success and as a quantity of something
            if ret >= 0:
                return ret

        except (ValueError, TypeError):
            # For a string, generally the error code is the last value of a string, so we
            # parse the string and store the last value and convert to an integer.
            if isinstance(ret, str):
                try:
                    ret = int(ret.split()[-1])
                except ValueError:
                    raise ValueError(f"Avs err_code could not be extracted from string: {ret}")

    # Likely the return value is a ctypes Array of a Structure or just a singular Structure
    else:
        return ret

    # Map of error codes to exceptions
    error_map = {
        AvsErrorEnum.ERR_INVALID_PARAMETER.value: ErrInvalidParameter,
        AvsErrorEnum.ERR_OPERATION_NOT_SUPPORTED.value: ErrOperationNotSupported,
        AvsErrorEnum.ERR_DEVICE_NOT_FOUND.value: ErrDeviceNotFound,
        AvsErrorEnum.ERR_INVALID_DEVICE_ID.value: ErrInvalidDeviceId,
        AvsErrorEnum.ERR_OPERATION_PENDING.value: ErrOperationPending,
        AvsErrorEnum.ERR_TIMEOUT.value: ErrTimeout,
        AvsErrorEnum.ERR_INVALID_PASSWORD.value: ErrInvalidPassword,
        AvsErrorEnum.ERR_INVALID_MEAS_DATA.value: ErrInvalidMeasData,
        AvsErrorEnum.ERR_INVALID_SIZE.value: ErrInvalidSize,
        AvsErrorEnum.ERR_INVALID_PIXEL_RANGE.value: ErrInvalidPixelRange,
        AvsErrorEnum.ERR_INVALID_INT_TIME.value: ErrInvalidIntTime,
        AvsErrorEnum.ERR_INVALID_COMBINATION.value: ErrInvalidCombination,
        AvsErrorEnum.ERR_INVALID_CONFIGURATION.value: ErrInvalidConfiguration,
        AvsErrorEnum.ERR_NO_MEAS_BUFFER_AVAIL.value: ErrNoMeasBufferAvail,
        AvsErrorEnum.ERR_UNKNOWN.value: ErrUnknown,
        AvsErrorEnum.ERR_COMMUNICATION.value: ErrCommunication,
        AvsErrorEnum.ERR_NO_SPECTRA_IN_RAM.value: ErrNoSpectraInRam,
        AvsErrorEnum.ERR_INVALID_DLL_VERSION.value: ErrInvalidDllVersion,
        AvsErrorEnum.ERR_NO_MEMORY.value: ErrNoMemory,
        AvsErrorEnum.ERR_DLL_INITIALISATION.value: ErrDllInitialisation,
        AvsErrorEnum.ERR_INVALID_STATE.value: ErrInvalidState,
        AvsErrorEnum.ERR_INVALID_REPLY.value: ErrInvalidReply,
        AvsErrorEnum.ERR_CONNECTION_FAILURE.value: ErrConnectionFailure,
        AvsErrorEnum.ERR_ACCESS.value: ErrAccess,
        AvsErrorEnum.ERR_INTERNAL_READ.value: ErrInternalRead,
        AvsErrorEnum.ERR_INTERNAL_WRITE.value: ErrInternalWrite,
        AvsErrorEnum.ERR_ETHCONN_REUSE.value: ErrEthConnReuse,
        AvsErrorEnum.ERR_INVALID_DEVICE_TYPE.value: ErrInvalidDeviceType,
        AvsErrorEnum.ERR_SECURE_CFG_NOT_READ.value: ErrSecureCfgNotRead,
        AvsErrorEnum.ERR_UNEXPECTED_MEAS_RESPONSE.value: ErrUnexpectedMeasResponse,
        AvsErrorEnum.ERR_MEAS_STOPPED.value: ErrMeasStopped,
        AvsErrorEnum.ERR_INVALID_PARAMETER_NR_PIXELS.value: ErrInvalidParameterNrPixels,
        AvsErrorEnum.ERR_INVALID_PARAMETER_ADC_GAIN.value: ErrInvalidParameterAdcGain,
        AvsErrorEnum.ERR_INVALID_PARAMETER_ADC_OFFSET.value: ErrInvalidParameterAdcOffset,
        AvsErrorEnum.ERR_INVALID_MEASPARAM_AVG_RAM.value: ErrInvalidMeasParamAvgRam,
        AvsErrorEnum.ERR_INVALID_MEASPARAM_SYNC_RAM.value: ErrInvalidMeasParamSyncRam,
        AvsErrorEnum.ERR_INVALID_MEASPARAM_SAT2_RAM.value: ErrInvalidMeasParamSat2Ram,
        AvsErrorEnum.ERR_INVALID_MEASPARAM_FWVER_RAM.value: ErrInvalidMeasParamFwverRam,
        AvsErrorEnum.ERR_INVALID_MEASPARAM_DYNDARK.value: ErrInvalidMeasParamDynDark,
        AvsErrorEnum.ERR_NOT_SUPPORTED_BY_SENSOR_TYPE.value: ErrNotSupportedBySensorType,
        AvsErrorEnum.ERR_NOT_SUPPORTED_BY_FW_VER.value: ErrNotSupportedByFwVer,
        AvsErrorEnum.ERR_NOT_SUPPORTED_BY_FPGA_VER.value: ErrNotSupportedByFpgaVer,
        AvsErrorEnum.ERR_SL_CALIBRATION_NOT_AVAILABLE.value: ErrSlCalibrationNotAvailable,
        AvsErrorEnum.ERR_SL_STARTPIXEL_NOT_IN_RANGE.value: ErrSlStartPixelNotInRange,
        AvsErrorEnum.ERR_SL_ENDPIXEL_NOT_IN_RANGE.value: ErrSlEndPixelNotInRange,
        AvsErrorEnum.ERR_SL_STARTPIX_GT_ENDPIX.value: ErrSlStartPixGtEndPix,
        AvsErrorEnum.ERR_SL_MFACTOR_OUT_OF_RANGE.value: ErrSlMfactorOutOfRange,
    }

    if ret in error_map:
        raise error_map[ret]()
    else:
        # If it's an unknown error code, raise a generic exception
        raise AvsError(AvsErrorEnum.ERR_UNKNOWN, f"Unknown error code: {ret}")
