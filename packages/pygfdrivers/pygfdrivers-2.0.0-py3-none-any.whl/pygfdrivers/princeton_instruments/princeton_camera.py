# Created By: Ethan Labbe
# Date: February 10th

import csv
import json
import bson
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from typing import Tuple, List, Dict, Union, Any

from pygfdrivers.common.util.utilities import has_setter
from pygfdrivers.common.base_device import BaseDevice, BaseModel

from pygfdrivers.princeton_instruments.picam.picam import *
from pygfdrivers.princeton_instruments.models.princeton_camera_config import PrincetonCameraConfigModel


class CONSTANTS:
    TIME_STAMP_STRIDE = 8
    KINETICS = 3
    EXPOSURE_STARTED = 0x1
    EXPOSURE_ENDED = 0x2
    SOFTWARE_TRIG = 1


class PrincetonCamera(BaseDevice):
    def __init__(self, camera_config: PrincetonCameraConfigModel = None, demo: bool = False) -> None:
        super().__init__(camera_config)
        self.demo = demo

    # ------------------------------------------------------------------------------------
    # Class Creation Methods
    # ------------------------------------------------------------------------------------   

    def init(self) -> None:
        try:
            InitializeLibrary()
            self.conn_str = self.config.device.device_conn_str
            self.connect()
        except Exception as e:
            self.log.error(f"Failed to initialize camera: {e}")
            self.is_connected = False

    def apply_configurations(self) -> None:
        """
        Set all parameters from configuration file in the camera
        """
        try:
            config = self.config
            for _ , model in config:
                if isinstance(model, BaseModel):
                    for field, setting in model.model_fields:
                        if has_setter(self, field) and setting is not None:
                            setattr(self, field, setting)
            self.commit_parameters()
            self.is_configured = True
            self.log.info(f"Frame Rate After Configuration: {self.frame_rate}")
        except Exception as e:
            self.log.error(f"Applying configuration encountered error: {e}")
            self.is_configured = False

    # ------------------------------------------------------------------------------------
    # Camera Operation Methods
    # For all of these methods, if there is no value set when we query, we try to set it to the 
    # configurationObject's value.
    # ------------------------------------------------------------------------------------   
        
    def connect(self) -> None:
        """
        Connect to Picam camera
        """
        try:
            if not self.demo:
                self.device = OpenCamera(serial_number=self.conn_str)
                self.is_connected = True
                self.log.info("Camera connected")
            else:
                self.demo_id = ConnectDemoCamera(1203, '1')
                self.device = OpenCamera(camera_id=self.demo_id)
                self.is_connected = True
                self.log.info("Demo Camera connected")

        except Exception as e:
            self.is_connected = False
            self.log.error(f"Connecting to device encountered error: {e}")

    def commit_parameters(self) -> None:
        """
        Commit parameters after setting (required before capturing data)
        """
        try:
            CommitParameters(self.device)
        except PicamFatalError as e:
            self.is_connected = False    
            self.log.error(f"Committing parameters encountered fatal PICam error: {e}")
        except Exception as e:
            self.log.error(f"Committing parameters encountered error: {e}")

    def prep_shot(self) -> None:
        try:
            self.stop_acquisition()
            self.clear_data()
            self.is_triggered = False
            self.is_armed = False
            self.log.info(f"Finished preparing shot.")
        except Exception as e:
            self.log.error(f"Preparing shot encountered error: {e}.")

    def arm(self) -> None:
        """
        Capture an image using the camera and store data to self.raw_data
        """
        try:
            self.prep_shot()
            self.log.info(f"Waiting for temperature to reach -70, current temp: {self.sensor_temperature}")
            self.wait_for_temp_status()
            StartAcquisition(self.device)
            self.is_armed = True
            self.is_triggered = False
            self.log.info("Camera Armed")
        except PicamFatalError as e:
            self.is_connected = False
            self.log.error(f"Arming camera encountered fatal PICam error: {e}")
        except Exception as e:
            self.log.error(f"Arming camera encountered error: {e}")

    def abort(self) -> None:
        try:
            self.raw_data, _ = self.get_acquisition_update()
            self.stop_acquisition()
            self.is_armed = False
            self.is_triggered = False
            self.log.info("Acquistion Aborted")
        except Exception as e:
            self.log.error(f"Aborting camera encountered error: {e}.")

    def stop_acquisition(self) -> None:
        # Have to loop because camera requires stop multiple times for some reason
        while IsAcquisitionRunning(self.device):
            StopAcquisition(self.device)
            WaitForAcquisitionUpdate(self.device, -1)

    def get_acquisition_update(self) -> Tuple:
        if IsAcquisitionRunning(self.device):
            StopAcquisition(self.device)
            return WaitForAcquisitionUpdate(self.device, -1)
        else:
            return None, None

    def disconnect(self) -> None:
        """
        Disconnect from camera
        """
        try:
            if self.is_connected:
                CloseCamera(self.device)
                self.is_connected = False

                if self.demo:
                    DisconnectDemoCamera(self.demo_id)

                self.log.info(f"Disconnect attempt successful")
        except Exception as e:
            self.log.error(f"Disconnecting device encountered error: {e}")

    def check_connection(self) -> None:
        """
        checks connection status of camera and updates variable
        """
        try:
            self.is_connected = IsCameraConnected(self.device)
        except Exception as e:
            self.log.error(f"Checking connection encountered error: {e}")
            self.is_connected = False
        finally:
            return self.is_connected

    def wait_for_temp_status(self) -> None:
        locked = 2
        WaitForStatusParameterValue(self.device, "SensorTemperatureStatus", locked, time_out=-1)

    # ------------------------------------------------------------------------------------
    # Get & Set Methods
    # ------------------------------------------------------------------------------------ 

    def get_parameter(self, name: str) -> Union[int, float, str, bool, Dict, List]:
        try:
            return GetParameterValue(self.device, name)
        except PicamFatalError as e:
            self.is_connected = False
            self.log.error(f"Failed getting parameter {name}: {e}")
        except Exception as e:
            self.log.error(f"Failed getting parameter {name}: {e}")

    def get_all_parameters(self) -> Dict[str, Union[str, bool, List[Dict[str, Any]]]]:
        """
        Get all parameters from the camera
        """
        try:
            return GetAllParameters(self.device)
        except PicamFatalError as e:
            self.is_connected = False
            self.log.error(f"Failed getting all parameters: {e}")
        except Exception as e:
            self.log.error(f"Failed getting all parameters: {e}")

    def set_parameter(self, name: str, value: Any) -> None:
        """
        General set method for camera parameters
        """
        try:
            SetParameterValue(self.device, name, value)
        except PicamFatalError as e:
            self.is_connected = False
            self.log.error(f"Failed setting {name} to {value}: {e}")
        except Exception as e:
            self.log.error(f"Failed setting {name} to {value}: {e}")

    @staticmethod
    def trigger_status() -> bool:
        # TODO try to make trigger status work possibly using WaitForAcquistionUpdate
        return False

    @property
    def time_exposure(self) -> float:
        _time_exposure = self.get_parameter("ExposureTime")
        return _time_exposure

    @time_exposure.setter
    def time_exposure(self, t_exposure: float) -> None:
        self.set_parameter("ExposureTime", t_exposure)

    @property
    def adc_gain(self) -> int:
        _adc_gain = self.get_parameter("AdcEMGain")
        return _adc_gain

    @adc_gain.setter
    def adc_gain(self, gain: int) -> None:
        self.set_parameter("AdcEMGain", gain)

    @property
    def adc_speed(self) -> float:
        _adc_speed = self.get_parameter("AdcSpeed")
        return _adc_speed

    @adc_speed.setter
    def adc_speed(self, speed: float) -> None:
        self.set_parameter("AdcSpeed", speed)

    @property
    def vertical_shift_rate(self) -> float:
        _shift_rate = self.get_parameter("VerticalShiftRate")
        return _shift_rate

    @vertical_shift_rate.setter
    def vertical_shift_rate(self, shift_rate: float) -> None:
        self.set_parameter("VerticalShiftRate", shift_rate) 

    @property
    def rois(self) -> List:
        _roi_array = self.get_parameter("Rois")
        return _roi_array

    @rois.setter
    def rois(self, roi_array: List) -> None:
        self.set_parameter("Rois", roi_array)

    @property
    def sensor_height(self) -> int:
        _sensor_height = self.get_parameter("ActiveHeight")
        return _sensor_height

    @sensor_height.setter
    def sensor_height(self, height: int) -> None:
        self.set_parameter("ActiveHeight", height)

    @property
    def sensor_width(self) -> int:
        _sensor_width = self.get_parameter("ActiveWidth")
        return _sensor_width

    @sensor_width.setter
    def sensor_width(self, width: int) -> None:
        self.set_parameter("ActiveWidth", width)

    @property
    def sensor_margin(self) -> List:
        _left_margin = self.get_parameter("ActiveLeftMargin")
        _right_margin = self.get_parameter("ActiveRightMargin")
        _top_margin = self.get_parameter("ActiveTopMargin")
        _bottom_margin = self.get_parameter("ActiveBottomMargin")
        return [_left_margin, _right_margin, _top_margin, _bottom_margin]

    @sensor_margin.setter
    def sensor_margin(self, margin: List) -> None:
        self.set_parameter("ActiveLeftMargin", margin[0])
        self.set_parameter("ActiveRightMargin", margin[1])
        self.set_parameter("ActiveTopMargin", margin[2])
        self.set_parameter("ActiveBottomMargin", margin[3])

    @property
    def kinetics_height(self) -> int:
        _kinetics_height = self.get_parameter("KineticsWindowHeight")
        return _kinetics_height

    @kinetics_height.setter
    def kinetics_height(self, height: int) -> None:
        self.set_parameter("KineticsWindowHeight", height)

    @property
    def mask_height(self) -> int:
        _mask_height = self.get_parameter("MaskedHeight")
        return _mask_height

    @mask_height.setter
    def mask_height(self, height: int) -> None:
        self.set_parameter("MaskedHeight", height)

    @property
    def mask_margin(self) -> List:
        _top_margin = self.get_parameter("MaskedTopMargin")
        _bottom_margin = self.get_parameter("MaskedBottomMargin")
        return [_top_margin, _bottom_margin]

    @mask_margin.setter
    def mask_margin(self, margin: List) -> None:
        self.set_parameter("MaskedTopMargin", margin[0])
        self.set_parameter("MaskedBottomMargin", margin[1])

    @property
    def time_stamps(self) -> int:
        _mode = self.get_parameter("TimeStamps")
        return _mode

    @time_stamps.setter
    def time_stamps(self, mode: int) -> None:
        self.set_parameter("TimeStamps", mode)

    @property
    def readout_mode(self) -> int:
        _mode = self.get_parameter("ReadoutControlMode")
        return _mode

    @readout_mode.setter
    def readout_mode(self, mode: int) -> None:
        self.set_parameter("ReadoutControlMode", mode)

    @property
    def trig_mode(self) -> int:
        _mode = self.get_parameter("TriggerResponse")
        return _mode

    @trig_mode.setter
    def trig_mode(self, mode: int) -> None:
        self.set_parameter("TriggerResponse", mode)

    @property
    def trig_slope(self) -> str:
        _trig_slope = self.get_parameter("TriggerDetermination")
        return _trig_slope

    @trig_slope.setter
    def trig_slope(self, slope: str) -> None:
        self.set_parameter("TriggerDetermination", slope)
    
    @property
    def clean_until_trigger(self) -> bool:
        _clean_until_trigger = self.get_parameter("CleanUntilTrigger")
        return _clean_until_trigger

    @clean_until_trigger.setter
    def clean_until_trigger(self, clean_until_trigger: bool):
        self.set_parameter("CleanUntilTrigger", clean_until_trigger)

    @property
    def readout_count(self) -> int:
        _readout_count = self.get_parameter("ReadoutCount")
        return _readout_count

    @readout_count.setter
    def readout_count(self, count: int) -> None:
        self.set_parameter("ReadoutCount", count)

    # Read Only Properties
    
    @property
    def sensor_temperature(self) -> float:
        _sensor_temperature = ReadParameterValue(self.device, "SensorTemperatureReading")
        return _sensor_temperature
    
    @property
    def frame_rate(self) -> float:
        _frame_rate = self.get_parameter("FrameRateCalculation")
        return _frame_rate
    
    @property
    def readout_stride(self) -> int:
        _readout_stride = self.get_parameter("ReadoutStride")
        return _readout_stride
    
    @property
    def frame_count(self) -> int:
        _frame_count = self.get_parameter("FramesPerReadout")
        return _frame_count
    
    @property
    def frame_size(self) -> int:
        _frame_size = self.get_parameter("FrameSize")
        return _frame_size
    
    @property
    def frame_stride(self) -> int:
        _frame_stride = self.get_parameter("FrameStride")
        return _frame_stride
    
    @property
    def time_stamp_resolution(self) -> int:
        _time_stamp_resolution = self.get_parameter("TimeStampResolution")
        return _time_stamp_resolution

    # ------------------------------------------------------------------------------------
    # Data Methods
    # ------------------------------------------------------------------------------------

    def format_raw_data(self) -> None:
        """
        Gets raw data pointer from the camera and reads the data per readout stride (size of readout)
        each readout can include multiple frames each with its own ROIs and metadata
        """
        try:
            readout_stride = self.readout_stride
            readout_count = self.raw_data.readout_count
            readout_pointer = self.raw_data.initial_readout
            readouts = []

            for i in range(readout_count):
                readout = self.read_readout(readout_pointer)
                readout_pointer += readout_stride
                readouts.append(readout)

            self.readouts = readouts
        except Exception as e:
            self.log.error(f"Failed to format raw data {e}")

    def read_readout(self, frame_pointer: int) -> List:
        """
        Takes a readout pointer input, increments pointer for both the frame and metadata and reads data from both pointers
        """
        frames = []
        frame_count = self.frame_count
        frame_size = self.frame_size
        frame_stride = self.frame_stride
        metadata_pointer = frame_pointer + frame_size

        for i in range(frame_count):
            # get frame data from the pointer in the format of uint16 of size frame_stride divided
            # by 2 as size of uint16 is 2 bytes
            frame = ctypes.cast(frame_pointer, ctypes.POINTER(ctypes.c_uint16 * (frame_stride // 2))).contents

            # convert frame data into a numpy array with data type of unit16
            frame = np.frombuffer(frame, dtype=np.uint16)
            rois = self.read_frame(frame)
            time_stamp = self.read_metadata(metadata_pointer)
            frames.append({"rois": rois, "time_stamp": time_stamp})
            frame_pointer += frame_stride
            metadata_pointer = frame_pointer + frame_size

        return frames

    def read_frame(self, frame: List) -> List:
        """
        takes frame data and splits data at the size of each ROI and reshapes data for the ROI to obtain png writable data
        """
        start = 0
        end = 0
        rois = []

        for roi in self.rois:
            height = roi["height"] // roi["x_binning"]
            width = roi["width"] // roi["y_binning"]
            end += height * width
            roi_array = frame[start:end]
            start = end
            roi_array = roi_array.reshape(height, width)
            rois.append(roi_array)

        return rois

    def read_metadata(self, pointer: int) -> Dict:
        """
        Reads metadata from the pointer and based of time stamp settings processes the metadata
        """
        time_stamp = {}
        resolution = self.time_stamp_resolution

        if self.time_stamps & CONSTANTS.EXPOSURE_STARTED:
            time = ctypes.cast(pointer, ctypes.POINTER(ctypes.c_int64)).contents.value
            time_stamp["Exposure Started"] = time/resolution
            pointer += CONSTANTS.TIME_STAMP_STRIDE

        if self.time_stamps & CONSTANTS.EXPOSURE_ENDED:
            time = ctypes.cast(pointer, ctypes.POINTER(ctypes.c_int64)).contents.value
            time_stamp["Exposure Ended"] = time/resolution
            pointer += CONSTANTS.TIME_STAMP_STRIDE

        return time_stamp

    def fetch_data(self) -> Dict:
        try:
            self.raw_data, _ = self.get_acquisition_update()
            self.stop_acquisition()
            self.format_raw_data()
            self.is_downloaded = True
            self.log.info("Sucesfully fetched data from camera")
            return {'readouts': self.format_json(self.readouts)}
        except PicamFatalError as e:
            self.is_connected = False
            self.log.error(f"Fetching data encountered fatal PICam error: {e}")
        except Exception as e:
            self.log.error(f"Fetching data encountered error: {e}")

    def fetch_metadata(self) -> Dict:
        return self.get_all_parameters()

    def clear_data(self) -> None:
        self.raw_data = None
        self.readouts = None
        self.is_downloaded = False

    def save_data_to_file(self) -> None:
        """
        Saves data in either format png, csv or json
        """
        path = self.config.device.file_save_path
        file_format = self.config.device.file_format

        if file_format == "PNG":
            self.save_to_png(path)
        elif file_format == "CSV":
            self.save_to_csv(path)
        elif file_format == "JSON":
            self.save_to_json(path)
        elif file_format == "BSON":
            self.save_to_bson(path)
        else:
            raise ValueError("Incorrect YAML file format configuration")

        self.is_downloaded = True
        self.log.info("Data Saved Sucessfully")

    def save_to_png(self, path: str):
        """
        Save roi data to a png and append metadata
        """
        try:
            for i, readout in enumerate(self.readouts):
                for j, frame in enumerate(readout):
                    rois = frame["rois"]
                    time_stamp = frame["time_stamp"]
                    metadata = None

                    for k, roi in enumerate(rois):
                        filepath = os.path.join(path, f"r{i}f{j}r{k}.png")
                        image = Image.fromarray(roi)

                        if time_stamp:
                            metadata = PngInfo()

                            for key, value in time_stamp.items():
                                metadata.add_text(key, str(value))

                        image.save(filepath, pnginfo = metadata)
        except Exception as e:
            self.log.error(f"Error writing to PNG: {e}")
    
    def save_to_csv(self, path: str) -> None:
        """
        Save frame data to a png and append metadata
        """
        try:
            for i, readout in enumerate(self.readouts):
                for j, frame in enumerate(readout):
                    filepath = os.path.join(path, f"r{i}f{j}.csv")
                    rois = frame["rois"]
                    time_stamp = frame["time_stamp"]

                    with open(filepath, mode='w', newline='') as csvfile:
                        writer = csv.writer(csvfile)

                        for roi in rois:
                            writer.writerows(roi)
                            writer.writerow([])

                        if time_stamp:
                            for key, value in time_stamp.items():
                                writer.writerow([key, value])

        except Exception as e:
            self.log.error(f"Error writing to CSV: {e}")

    def save_to_json(self, path: str) -> None:
        try:
            data = self.format_json(self.readouts)
            filepath = os.path.join(path, "ProEM.json")

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)

        except Exception as e:
            self.log.error(f"Error writing to JSON: {e}")

    def save_to_bson(self, path: str) -> None:
        try:
            data = self.format_json(self.readouts)
            data = {"readouts": data}
            filepath = os.path.join(path, "ProEM.bin")

            with open(filepath, 'wb') as f:
                f.write(bson.encode(data))

        except Exception as e:
            self.log.error(f"Error writing to BSON: {e}")

    def format_json(self, obj: Union[np.ndarray, List, Dict]) -> Union[np.ndarray, List, Dict]:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self.format_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.format_json(item) for item in obj]
        else:
            return obj
