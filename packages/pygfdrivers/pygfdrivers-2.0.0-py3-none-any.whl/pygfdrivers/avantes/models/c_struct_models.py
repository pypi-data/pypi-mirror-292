from ctypes import Array
from typing import List, Union, Optional
from pydantic import BaseModel, Field, AliasChoices, field_validator, BeforeValidator

from pygfdrivers.avantes.util.utilities import ctypes_array_to_list


class BaseStructModel(BaseModel):
    class Config:
        @staticmethod
        def before_validator(value):
            return ctypes_array_to_list(value)
        before_validator = BeforeValidator(before_validator)


class AvantesIdentityModel(BaseModel):
    serial_num: str = Field(
        default=None,
        alias='SerialNumber',
        validation_alias=AliasChoices('serial_num', 'SerialNumber'),
    )
    user_name: str = Field(
        default=None,
        alias='UserFriendlyName',
        validation_alias=AliasChoices('user_name', 'UserFriendlyName'),
    )
    status: str = Field(
        default=None,
        alias='Status',
        validation_alias=AliasChoices('status', 'Status'),
    )


class BroadcastAnswerModel(BaseStructModel):
    interface_type: int = Field(
        default=None,
        alias='InterfaceType',
        validation_alias=AliasChoices('total_scans', 'InterfaceType')
    )
    serial_num: bytes = Field(
        default=None,
        alias='serial',
        validation_alias=AliasChoices('serial_num', 'serial')
    )
    port_num: int = Field(
        default=None,
        alias='port',
        validation_alias=AliasChoices('port_num', 'port')
    )
    link_status: int = Field(
        default=None,
        alias='status',
        validation_alias=AliasChoices('link_status', 'status')
    )
    remote_host_ip: int = Field(
        default=None,
        alias='RemoteHostIp',
        validation_alias=AliasChoices('remote_host_ip', 'RemoteHostIp')
    )
    local_ip: int = Field(
        default=None,
        alias='LocalIp',
        validation_alias=AliasChoices('local_ip', 'LocalIp')
    )
    reserved: List[float] = Field(
        default_factory=lambda: list(),
        alias='Reserved',
        validation_alias=AliasChoices('reserved', 'Reserved')
    )


class ControlModel(BaseModel):
    strobe_control: int = Field(
        default=None,
        alias='StrobeControl',
        validation_alias=AliasChoices('strobe_control', 'strobe', 'StrobeControl')
    )
    laser_delay: int = Field(
        default=None,
        alias='LaserDelay',
        validation_alias=AliasChoices('laser_delay', 'LaserDelay')
    )
    laser_width: int = Field(
        default=None,
        alias='LaserWidth',
        validation_alias=AliasChoices('laser_width', 'LaserWidth')
    )
    laser_wavelength: float = Field(
        default=None,
        alias='LaserWaveLength',
        validation_alias=AliasChoices('laser_wavelength', 'LaserWaveLength')
    )
    store_to_ram: int = Field(
        default=None,
        alias='StoreToRam',
        validation_alias=AliasChoices('store_to_ram', 'StoreToRam')
    )

    @field_validator('laser_delay', 'laser_width', mode='after')
    def process_laser_fields(cls, value: int) -> int:
        value_int = int(6.0 * value / 125.0)
        return value_int


class DarkCorrectionModel(BaseModel):
    enable: bool = Field(
        default=None,
        alias='Enable',
        validation_alias=AliasChoices('enable', 'Enable')
    )
    forget_percent: int = Field(
        default=None,
        alias='ForgetPercentage',
        validation_alias=AliasChoices('forget_percent', 'ForgetPercentage')
    )


class DetectorModel(BaseStructModel):
    sensor_type: int = Field(
        default=None,
        alias='SensorType',
        validation_alias=AliasChoices('sensor_type', 'SensorType')
    )
    num_pixels: int = Field(
        default=None,
        alias='NrPixels',
        validation_alias=AliasChoices('num_pixels', 'NrPixels')
    )
    wavelength_calibration: List[float] = Field(
        default_factory=lambda: list(),
        alias='aFit',
        validation_alias=AliasChoices('wavelength_calibration', 'aFit')
    )
    gain: List[float] = Field(
        default_factory=lambda: list(),
        alias='Gain',
        validation_alias=AliasChoices('gain', 'detector_gain', 'Gain')
    )
    integration_offset: List[float] = Field(
        default_factory=lambda: list(),
        alias='Offset',
        validation_alias=AliasChoices('integration_offset', 'Offset')
    )
    external_offset: float = Field(
        default=None,
        alias='ExtOffset',
        validation_alias=AliasChoices('external_offset', 'ExtOffset')
    )
    defective_pixels: List[int] = Field(
        default_factory=lambda: list(),
        alias='DefectivePixels',
        validation_alias=AliasChoices('defective_pixels', 'DefectivePixels')
    )
    non_linear_enable: bool = Field(
        default=None,
        alias='NLEnable',
        validation_alias=AliasChoices('non_linear_enable', 'NLEnable')
    )
    non_linear_correction: List[float] = Field(
        default_factory=lambda: list(),
        alias='aNLCorrect',
        validation_alias=AliasChoices('non_linear_correction', 'aNLCorrect')
    )
    non_linear_lower_counts: float = Field(
        default=None,
        alias='aLowNLCounts',
        validation_alias=AliasChoices('non_linear_lower_counts', 'aLowNLCounts')
    )
    non_linear_higher_counts: float = Field(
        default=None,
        alias='aHighNLCounts',
        validation_alias=AliasChoices('non_linear_higher_counts', 'aHighNLCounts')
    )
    reserved: float = Field(
        default=None,
        alias='Reserved',
        validation_alias=AliasChoices('reserved', 'Reserved')
    )


class DstrStatusModel(BaseModel):
    total_scans: int = Field(
        default=None,
        alias='TotalScans',
        validation_alias=AliasChoices('total_scans', 'TotalScans')
    )
    used_scans: int = Field(
        default=None,
        alias='UsedScans',
        validation_alias=AliasChoices('used_scans', 'UsedScans')
    )
    flags: int = Field(
        default=None,
        alias='Flags',
        validation_alias=AliasChoices('flags', 'Flags')
    )
    is_stop_event: int = Field(
        default=None,
        alias='IsStopEvent',
        validation_alias=AliasChoices('is_stop_event', 'IsStopEvent')
    )
    is_overflow_event: int = Field(
        default=None,
        alias='IsOverflowEvent',
        validation_alias=AliasChoices('is_overflow_event', 'IsOverflowEvent')
    )
    is_internal_error_event: int = Field(
        default=None,
        alias='IsInternalErrorEvent',
        validation_alias=AliasChoices('is_internal_error_event', 'IsInternalErrorEvent')
    )
    reserved: int = Field(
        default=None,
        alias='Reserved',
        validation_alias=AliasChoices('reserved', 'Reserved')
    )


class EthernetSettingsModel(BaseModel):
    ip_addr: Union[int, str] = Field(
        default=None,
        alias='IpAddr',
        validation_alias=AliasChoices('ip_addr', 'IpAddr')
    )
    net_mask: Union[int, str] = Field(
        default=None,
        alias='NetMask',
        validation_alias=AliasChoices('net_mask', 'NetMask')
    )
    gateway: Union[int, str] = Field(
        default=None,
        alias='Gateway',
        validation_alias=AliasChoices('gateway', 'Gateway')
    )
    dhcp_enable: Union[int, bool] = Field(
        default=None,
        alias='DhcpEnabled',
        validation_alias=AliasChoices('dhcp_enable', 'DhcpEnabled')
    )
    tcp_port: int = Field(
        default=None,
        alias='TcpPort',
        validation_alias=AliasChoices('tcp_port', 'TcpPort')
    )
    link_status: Union[int, bool] = Field(
        default=None,
        alias='LinkStatus',
        validation_alias=AliasChoices('link_status', 'LinkStatus')
    )
    client_id_type: Union[bytes, str] = Field(
        default=None,
        alias='ClientIdCustom',
        validation_alias=AliasChoices('client_id_type', 'ClientIdCustom')
    )
    user_client_id: int = Field(
        default=None,
        alias='ClientIdType',
        validation_alias=AliasChoices('user_client_id_type', 'ClientIdType')
    )
    reserved: List[int] = Field(
        default_factory=lambda: list(),
        alias='Reserved',
        validation_alias=AliasChoices('reserved', 'Reserved')
    )


class ProcessControlModel(BaseStructModel):
    analog_low: List[float] = Field(
        default_factory=lambda: list(),
        alias='AnalogLow',
        validation_alias=AliasChoices('analog_low', 'AnalogLow')
    )
    analog_high: List[float] = Field(
        default_factory=lambda: list(),
        alias='AnalogHigh',
        validation_alias=AliasChoices('analog_high', 'AnalogHigh')
    )
    digital_low: List[float] = Field(
        default_factory=lambda: list(),
        alias='DigitalLow',
        validation_alias=AliasChoices('digital_low', 'DigitalLow')
    )
    digital_high: List[float] = Field(
        default_factory=lambda: list(),
        alias='DigitalHigh',
        validation_alias=AliasChoices('digital_high', 'DigitalHigh')
    )


class TecControlModel(BaseStructModel):
    enable: bool = Field(
        default=None,
        alias='Enable',
        validation_alias=AliasChoices('enable', 'Enable')
    )
    set_point: float = Field(
        default=None,
        alias='Setpoint',
        validation_alias=AliasChoices('set_point', 'Setpoint')
    )
    tec_cal: List[float] = Field(
        default_factory=lambda: list(),
        alias='aFit',
        validation_alias=AliasChoices('tec_cal', 'tec_calibration', 'aFit')
    )


class TemperatureModel(BaseStructModel):
    temp_cal: List[float] = Field(
        default_factory=lambda: list(),
        alias='aFit',
        validation_alias=AliasChoices('temp_cal', 'temp_calibration', 'aFit')
    )


class TriggerModel(BaseModel):
    mode: Union[int, str] = Field(
        default=None,
        alias='Mode',
        validation_alias=AliasChoices('mode', 'Mode')
    )
    source: Union[int, str] = Field(
        default=None,
        alias='Source',
        validation_alias=AliasChoices('source', 'Source')
    )
    source_type: Union[int, str] = Field(
        default=None,
        alias='SourceType',
        validation_alias=AliasChoices('source_type', 'type', 'SourceType')
    )


class SmoothingModel(BaseModel):
    pixels: int = Field(
        default=None,
        alias='SmoothPix',
        validation_alias=AliasChoices('pixels', 'SmoothPix')
    )
    model: Union[int, str] = Field(
        default=None,
        alias='SmoothModel',
        validation_alias=AliasChoices('model', 'SmoothModel')
    )


class ReflectanceModel(BaseStructModel):
    smoothing: SmoothingModel = Field(
        default_factory=lambda: SmoothingModel(),
        alias='Smoothing',
        validation_alias=AliasChoices('smoothing', 'Smoothing')
    )
    integration_time: float = Field(
        default=None,
        alias='CalInttime',
        validation_alias=AliasChoices('integration_time', 'int_time', 'CalInttime')
    )
    conversion: List[float] = Field(
        default_factory=lambda: list(),
        alias='aCalibConvers',
        validation_alias=AliasChoices('conversion', 'aCalibConvers')
    )


class IntensityCalModel(ReflectanceModel):
    pass


class IrradianceModel(BaseModel):
    intensity_cal: IntensityCalModel = Field(
        default_factory=lambda: IntensityCalModel(),
        alias='IntensityCalib',
        validation_alias=AliasChoices('intensity_cal', 'IntensityCalib')
    )
    cal_type: int = Field(
        default=None,
        alias='CalibrationType',
        validation_alias=AliasChoices('cal_type', 'CalibrationType')
    )
    fiber_diameter: int = Field(
        default=None,
        alias='FiberDiameter',
        validation_alias=AliasChoices('diameter', 'FiberDiameter')
    )



class MeasConfigModel(BaseStructModel):
    start_pixel: int = Field(
        default=0,
        alias='StartPixel',
        validation_alias=AliasChoices('start_pixel', 'StartPixel')
    )
    stop_pixel: int = Field(
        default=2048,
        alias='StopPixel',
        validation_alias=AliasChoices('stop_pixel', 'StopPixel')
    )
    integration_time: float = Field(
        default=None,
        alias='IntegrationTime',
        validation_alias=AliasChoices('integration_time', 'int_time', 'IntegrationTime')
    )
    integration_delay_time: float = Field(
        default=None,
        alias='IntegrationDelay',
        validation_alias=AliasChoices('integration_delay_time', 'int_delay_time', 'IntegrationDelay')
    )
    num_avg: int = Field(
        default=1,
        alias='NrAverages',
        validation_alias=AliasChoices('num_avg', 'NrAverages')
    )
    dark_correct: DarkCorrectionModel = Field(
        default_factory=lambda: DarkCorrectionModel(),
        alias='CorDynDark',
        validation_alias=AliasChoices('dark_correct', 'dark_correction', 'CorDynDark')
    )
    smoothing: SmoothingModel = Field(
        default_factory=lambda: SmoothingModel(),
        alias='Smoothing',
        validation_alias=AliasChoices('smoothing', 'Smoothing')
    )
    saturation_detect: int = Field(
        default=None,
        alias='SaturationDetection',
        validation_alias=AliasChoices('saturation_detect_enable', 'sat_detect', 'SaturationDetection')
    )
    trigger: TriggerModel = Field(
        default_factory=lambda: TriggerModel(),
        alias='Trigger',
        validation_alias=AliasChoices('trigger', 'trigger_settings', 'Trigger')
    )
    control: ControlModel = Field(
        default_factory=lambda: ControlModel(),
        alias='Control',
        validation_alias=AliasChoices('control', 'control_settings', 'Control')
    )

    @field_validator('integration_delay_time', mode='after')
    def process_int_delay_time(cls, value: float) -> int:
        value_int = int(6.0 * (value + 20.84) / 125.0)
        return value_int


class StandAloneModel(BaseModel):
    enable: bool = Field(
        default=False,
        alias='Enable',
        validation_alias=AliasChoices('enable', 'Enable'),
    )
    measure_config: MeasConfigModel = Field(
        default_factory=lambda: MeasConfigModel(),
        alias='Meas',
        validation_alias=AliasChoices('measure_config', 'measure_settings', 'Meas', 'measure'),
    )
    nmsr: int = Field(
        default=1,
        alias='Nmsr',
        validation_alias=AliasChoices('nmsr', 'Nmsr')
    )


class DeviceConfigModel(BaseStructModel):
    length: int = Field(
        default=None,
        alias='Len',
        validation_alias=AliasChoices('length', 'len', 'Len')
    )
    config_version: int = Field(
        default=None,
        alias='ConfigVersion',
        validation_alias=AliasChoices('config_version', 'ConfigVersion')
    )
    user_friendly_id: str = Field(
        default=None,
        alias='aUserFriendlyId',
        validation_alias=AliasChoices('user_friendly_id', 'aUserFriendlyId')
    )
    detector: DetectorModel = Field(
        default_factory=lambda: DetectorModel(),
        alias='Detector',
        validation_alias=AliasChoices('detector', 'Detector')
    )
    irradiance: IrradianceModel = Field(
        default_factory=lambda: IrradianceModel(),
        alias='Irradiance',
        validation_alias=AliasChoices('irradiance', 'Irradiance')
    )
    reflectance: ReflectanceModel = Field(
        default_factory=lambda: ReflectanceModel(),
        alias='Reflectance',
        validation_alias=AliasChoices('reflectance', 'Reflectance')
    )
    spectrum_correct: Optional[List] = Field(
        default_factory=lambda: list(),
        alias='SpectrumCorrect',
        validation_alias=AliasChoices('spectrum_correct', 'spectrum_correction', 'SpectrumCorrect')
    )
    standalone: StandAloneModel = Field(
        default_factory=lambda: StandAloneModel(),
        alias='StandAlone',
        validation_alias=AliasChoices('standalone', 'StandAlone', 'standalone_settings')
    )
    dynamic_storage: Optional[List] = Field(
        default_factory=lambda: list(),
        alias='DynamicStorage',
        validation_alias=AliasChoices('dynamic_storage', 'DynamicStorage')
    )
    temp_1: TemperatureModel = Field(
        default_factory=lambda: TemperatureModel(),
        alias='Temperature_1',
        validation_alias=AliasChoices('temp_1', 'Temperature_1')
    )
    temp_2: TemperatureModel = Field(
        default_factory=lambda: TemperatureModel(),
        alias='Temperature_2',
        validation_alias=AliasChoices('temp_2', 'Temperature_2')
    )
    temp_3: TemperatureModel = Field(
        default_factory=lambda: TemperatureModel(),
        alias='Temperature_3',
        validation_alias=AliasChoices('temp_3', 'Temperature_3')
    )
    tec_control: TecControlModel = Field(
        default_factory=lambda: TecControlModel(),
        alias='TecControl',
        validation_alias=AliasChoices('tec_control', 'TecControl')
    )
    process_control: ProcessControlModel = Field(
        default_factory=lambda: ProcessControlModel(),
        alias='ProcessControl',
        validation_alias=AliasChoices('process_control', 'ProcessControl')
    )
    eth_settings: EthernetSettingsModel = Field(
        default_factory=lambda: EthernetSettingsModel(),
        alias='EthernetSettings',
        validation_alias=AliasChoices('ethernet_settings', 'EthernetSettings', 'ethernet')
    )
    reserved: Optional[List] = Field(
        default_factory=lambda: list(),
        alias='Reserved',
        validation_alias=AliasChoices('reserved', 'Reserved')
    )
    oem_data: Optional[List] = Field(
        default_factory=lambda: list(),
        alias='OemData',
        validation_alias=AliasChoices('oem_data', 'OemData')
    )

    @field_validator(
        'spectrum_correct',
        'dynamic_storage',
        'reserved',
        'oem_data',
        mode='before'
    )
    def to_list(cls, value_array: Array) -> List:
        value_list = ctypes_array_to_list(value_array)
        return value_list

    @field_validator('user_friendly_id', mode='before')
    def to_str(cls, value_bytes: bytes) -> str:
        value_str = value_bytes.decode('utf-8')
        return value_str
