from time import sleep
from pydantic import BaseModel
from ctypes import Array, Structure
from typing import Tuple, List, Dict, Callable, Any

from pygfdrivers.common.base_device import BaseDevice

from pygfdrivers.avantes.avaspec.avaspec import *
from pygfdrivers.avantes.avaspec.errors import enum_avs_err

from pygfdrivers.avantes.util.param_maps import conn_type_map
from pygfdrivers.avantes.util.utilities import model_to_ctypes_struct, ctypes_struct_to_model

from pygfdrivers.avantes.models.spectro_model import AvantesSpectroModel
from pygfdrivers.avantes.models.c_struct_models import DeviceConfigModel


class AvantesSpectrometer(BaseDevice):
    def __init__(self, spectro_config: AvantesSpectroModel) -> None:
        super().__init__(spectro_config)

        self.user_device_config = self.config.device
        self.user_measure_config = self.user_device_config.standalone.measure_config

        self.config_conn_type = self.user_device_config.device_conn_type
        self.config_serial_num = self.user_device_config.device_serial_num

        # NOTE: Completely redudant to create a new object, but just to stay consistent with how
        # other device classes create their data models, this will have to do. Hoping to change
        # this at some point.
        self.data = AvantesSpectroModel()
        self.data.device = self.user_device_config
        self.scan_data = self.data.data.scan_data
        self.scan_times = self.data.data.scan_times

        self.avs_handle = None
        self.meas_cb = AVS_MeasureCallbackFunc(self.measure_callback)

    def __getattribute__(self, name: str) -> Any:
        if name in {'handle_exceptions', 'log', 'avs_run'} or name.startswith('__'):
            return super().__getattribute__(name)

        attr = super().__getattribute__(name)

        if callable(attr) and not name.startswith('__'):
            return lambda *args, **kwargs: self.handle_exceptions(attr, *args, **kwargs)

        return attr

    def init(self) -> None:
        self.log.info("Initializing AVS spectrometer object...")

        try:
            self.avs_handle = self.activate()

            if self.avs_handle is None:
                raise ValueError("Avantes spectrometer did not connect properly.")

            self.log.info(f"AVANTES SPECTROMETER TYPE FOR SPECTROMETER NAME ---- {self.name}")
            self.is_connected = True
        except Exception as e:
            self.log.error(f"Initializing Avantes spectrometer encountered error: {e}")
            self.is_connected = False

    # ------------------------------------------------------------------------------------
    #  Shot Control Methods
    # ------------------------------------------------------------------------------------

    def apply_configurations(self) -> None:
        try:
            self.log.info("Applying configurations to device...")

            self.use_high_res_adc(True)

            # Convert pydantic model to a ctypes structure as avaspec functions
            # only accept ctype structures, but configurations are pydantic models
            user_meas_config = model_to_ctypes_struct(self.user_measure_config, MeasConfigType)
            self.prepare_measure(user_meas_config)
            self.is_configured = True
        except Exception as e:
            self.log.error(f"Applying configurations to device encountered error: {e}")
            self.is_configured = False

    def arm(self) -> None:
        self.log.info("Arming device...")
        self.prep_shot()
        self.start_measure()
        self.is_armed = True

    def abort(self) -> None:
        self.log.info("Aborting pending measurements...")
        self.stop_measure()
        self.is_aborted = True

    def prep_shot(self) -> None:
        self.log.info("Clearing shot related variables...")
        self.abort()
        self.is_armed = False
        self.is_triggered = False
        self.is_downloaded = False
        self.is_aborted = False

    def check_connection(self) -> bool:
        try:
            if self.match_serial_num(self.find_devices(self.config_conn_type), self.config_serial_num):
                self.is_connected = True
            else:
                self.is_connected = False
        except Exception as e:
            self.log.error(f"Checking connection encountered error: {e}")
            self.is_connected = False
        finally:
            self.log.debug(f"Avantes spectrometer is: {'ONLINE' if self.is_connected else 'OFFLINE'}")
            return self.is_connected

    # ------------------------------------------------------------------------------------
    #  Read Only Methods
    # ------------------------------------------------------------------------------------

    @property
    def wavelengths(self) -> List[float]:
        _wavelengths = self.avs_run(AVS_GetLambda, self.avs_handle)
        _wavelengths = list(_wavelengths)[:self.pixels]
        return _wavelengths

    @property
    def pixels(self) -> int:
        _device_config = self.device_config
        _pixels = _device_config.m_Detector_m_NrPixels
        return _pixels

    @property
    def device_config(self) -> ctypes.Structure:
        _device_config = self.avs_run(AVS_GetParameter, self.avs_handle, 63484)
        return _device_config

    @property
    def detector(self) -> str:
        device_config = self.device_config
        sensor = device_config.m_Detector_m_SensorType
        _detector = self.avs_run(AVS_GetDetectorName, self.avs_handle, sensor)
        _detector_name = _detector.value.decode('utf-8')
        self.log.debug(f"Detector name: {_detector_name}")
        return _detector_name

    @property
    def fw_versions(self) -> List[str]:
        version_map = ['FPGA', 'Firmware', 'DLL']
        _fw_versions = self.avs_run(AVS_GetVersionInfo, self.avs_handle)

        for index, version in enumerate(version_map):
            self.log.debug(f"{version} version: {_fw_versions[index].value.decode('utf-8')}")

        return _fw_versions

    @property
    def dstr_stats(self) -> ctypes.Structure:
        _dstr_stats = AVS_GetDstrStatus(self.avs_handle)
        self.log.debug(
            f"total_scans: {_dstr_stats.m_TotalScans}, "
            f"used_scans: {_dstr_stats.m_UsedScans}, "
            f"event_flags: {_dstr_stats.m_Flags}, "
            f"dss_event: {_dstr_stats.m_Flags & DSTR_STATUS_DSS_MASK}, "
            f"foe_event: {_dstr_stats.m_Flags & DSTR_STATUS_FOE_MASK}, "
            f"internal_error_event: {_dstr_stats.m_Flags & DSTR_STATUS_IERR_MASK}"
        )
        return _dstr_stats

    @property
    def poll_scan(self) -> bool:
        # AVS_PollScan() without a delay causes heavy CPU loads. P.24 AvaSpec Library
        # Manual suggests that 1 ms delay will suffice between each polling check.
        new_scan = self.avs_run(AVS_PollScan, self.avs_handle)
        sleep(0.001)
        return bool(new_scan)

    @property
    def scope_data(self) -> Tuple:
        # P.25 AvaSpec Library Manual - Return value of timestamp from AVS_GetScopeData() are
        # Ticks count (aka clock cycles) last pixel of spectrum is received by microcontroller
        # ticks in 10us units since spectrometer power on.
        timestamp, scan_data = self.avs_run(AVS_GetScopeData, self.avs_handle)
        timestamp *= 10e-6
        return timestamp, scan_data

    @property
    def trigger_status(self) -> bool:
        _trigger_status = self.poll_scan and self.is_triggered
        return _trigger_status

    @property
    def arm_status(self) -> bool:
        return self.is_armed

    # ------------------------------------------------------------------------------------
    #  Data Methods
    # ------------------------------------------------------------------------------------

    def fetch_data(self) -> None:
        self.log.info("Fetching data from device...")
        num_pixels = self.pixels
        num_scans = self.measure_result

        for scan in range(num_scans):
            timestamp, data = self.scope_data
            self.scan_times.append(timestamp)
            self.scan_data.append(list(data)[:num_pixels])

        self.data.data.wavelengths = self.wavelengths
        self.is_downloaded = True

    def fetch_metadata(self) -> None:
        raise NotImplementedError("fetch_metadata not yet implemented.")

    # ------------------------------------------------------------------------------------
    #  Device Configuration Methods
    # ------------------------------------------------------------------------------------

    def measure_callback(self, cb_handle, cb_result) -> None:
        """
        Callback function called when measurement has finished taking in
        number of scans set in StoreToRam in MeasConfigType ctypes structure.
        """
        if not cb_handle:
            raise ValueError("Measure callback function avs_handle is NULL.")

        if not cb_result:
            raise ValueError("Measure callback function err_code is NULL.")

        self.measure_handle = cb_handle.contents.value
        self.measure_result = cb_result.contents.value
        self.is_triggered = True

    def prepare_measure(self, measure_config: Structure) -> None:
        self.avs_run(AVS_PrepareMeasure, self.avs_handle, measure_config)

    def start_measure(self) -> None:
        self.log.info("Starting measurement operation...")
        self.avs_run(AVS_MeasureCallback, self.avs_handle, self.meas_cb, 1)

    def stop_measure(self) -> None:
        self.log.info("Stopping measurement operation...")
        self.avs_run(AVS_StopMeasure, self.avs_handle)

    def use_high_res_adc(self, state: bool) -> None:
        self.avs_run(AVS_UseHighResAdc, self.avs_handle, state)

    # ------------------------------------------------------------------------------------
    #  Device Connection Methods
    # ------------------------------------------------------------------------------------

    def activate(self):
        self.log.info(f"Activating AVS spectrometer '{self.config_serial_num}' through '{self.config_conn_type}'...")

        spectro_handle = self.match_serial_num(self.connect(self.config_conn_type), self.config_serial_num)
        if spectro_handle:
            self.is_connected = True
            return spectro_handle

        raise ValueError(f"Spectrometer {self.config_serial_num} not found.")

    def connect(self, conn_type: str = 'ethernet') -> Array:
        self.log.info(f"Connecting to AVS spectrometer through '{conn_type.upper()}' connection...")
        num_devices_found = self.avs_run(AVS_Init, conn_type_map[conn_type])

        if num_devices_found:
            self.log.debug(f"Found '{num_devices_found}' spectrometers through '{conn_type}' network.")
            return self.find_devices(conn_type)

        raise ValueError(f"No spectrometers found connected through {conn_type}.")

    def find_devices(self, conn_type: str = 'ethernet') -> Array:
        self.log.info(f"Locating all AVS spectrometers connected through '{conn_type.upper()}'...")
        update_func = AVS_UpdateUSBDevices if conn_type.lower() == 'usb' else AVS_UpdateETHDevices
        spectro_list = self.avs_run(update_func)

        if not isinstance(spectro_list, int):
            spectro_list = len(spectro_list)

        return self.avs_run(AVS_GetList, spectro_list)

    def match_serial_num(self, spectros_found: Array, serial_num: str) -> bool:
        for spectro in spectros_found:
            current_serial_num = spectro.SerialNumber.decode('utf-8')

            if current_serial_num == serial_num:
                spectro_handle = self.avs_run(AVS_Activate, spectro)

                if spectro_handle == INVALID_AVS_HANDLE_VALUE:
                    raise ValueError(f"Could not activate AVS spectrometer {serial_num}.")

                self.log.debug(f"Spectrometer '{spectro_handle}' activated successfully")
                return spectro_handle

    def disconnect(self) -> None:
        self.log.info("Closing communication and disconnecting AVS spectrometer.")

        if self.avs_handle != INVALID_AVS_HANDLE_VALUE:
            self.avs_run(AVS_Deactivate, self.avs_handle)
            self.avs_run(AVS_Done)
            self.is_connected = False
            self.avs_handle = INVALID_AVS_HANDLE_VALUE

    def reset(self) -> None:
        self.log.info("Resetting AVS spectrometer...")
        self.avs_run(AVS_ResetDevice, self.avs_handle)
        sleep(10)
        self.log.info("Finished resetting AVS spectrometer.")

    # ------------------------------------------------------------------------------------
    #  Misc. Methods
    # ------------------------------------------------------------------------------------

    @staticmethod
    def avs_run(avs_method: Callable[..., Any], *args, **kwargs) -> Any:
        err_code = avs_method(*args, **kwargs)
        enum_avs_err(err_code)
        return err_code

    def apply_device_configuration(self) -> None:
        self.log.info("Applying AVS spectrometer device configuration...")
        current_struct = self.device_config
        current_model = ctypes_struct_to_model(DeviceConfigModel, current_struct)

        def set_model(user_model: BaseModel, new_model: BaseModel) -> BaseModel:
            fields_set = list(getattr(user_model, 'model_fields_set'))

            for field in fields_set:
                field_value = getattr(user_model, field)

                if isinstance(field_value, BaseModel):
                    set_model(field_value, getattr(new_model, field))

                setattr(new_model, field, field_value)

            return new_model

        # Apply only "set" values from the model to the ctypes structure
        config_model = set_model(self.user_device_config, current_model)

        # Convert the "set" model created from the user configuration model to a structure
        # and compare with the previous structure to monitor differences
        config_struct = model_to_ctypes_struct(config_model, DeviceConfigType)

        # Apply settings to device
        # ret = AVS_SetParameter(self.avs_handle, config_struct)
        # enum_avs_err(ret)

    def factory_reset(self, config: Dict) -> None:
        self.log.info("Applying factory default settings...")
        device_config = DeviceConfigType()

        for setting, set_value in config.items():
            setting_dtype = type(getattr(device_config, setting))

            if isinstance(set_value, list):
                set_value = setting_dtype(*set_value)
            elif isinstance(set_value, str):
                set_value = setting_dtype(set_value.encode('utf-8'))
            else:
                setting_dtype(set_value)

            setattr(device_config, setting, set_value)
        AVS_SetParameter(self.avs_handle, device_config)
        self.log.info("Finished applying factory default settings.")
