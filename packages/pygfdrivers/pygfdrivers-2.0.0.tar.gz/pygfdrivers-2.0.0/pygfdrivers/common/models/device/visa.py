from typing import Any
from pydantic import BaseModel, Field, field_validator, AliasChoices
from pygfdrivers.common.models.device.device import BaseDeviceModel


class BaseVisaResourceModel(BaseModel):
    visa_conn_type: str = Field(default='ethernet')
    visa_resource_type: str = Field(default='INSTR')
    visa_board_num: int = Field(default=0)

    eth_ip_addr: str = Field(
        default=None,
        alias='ip_addr',
        validation_alias=AliasChoices('eth_ip_addr', 'ip_addr')
    )
    eth_lan_device_name: str = Field(default='inst0')

    gpib_primary_addr: str = Field(default=None)
    gpib_secondary_addr: str = Field(default=None)

    serial_port: int = Field(default=None)

    usb_vendor_id: str = Field(default=None)
    usb_model_code: str = Field(default=None)
    usb_serial_num: str = Field(default=None)
    usb_interface_num: str = Field(default=None)

    vxi_logical_addr: str = Field(default=None)

    pxi_device: str = Field(default=None)
    pxi_bus_num: str = Field(default=None)
    pxi_function: str = Field(default=None)

    @field_validator('visa_conn_type')
    @classmethod
    def is_valid_conn_type(cls, value: str) -> str:
        if value.lower() not in ['gpib', 'serial', 'usb', 'ethernet', 'vxi', 'pxi']:
            raise ValueError('Invalid connection type')
        return value.lower()

    def create_resource_str(self) -> str:
        # Any values within the [] are optional arguments for the manufacturer to define, however if you fetch
        # values for these arguments from the device, they are required.

        # TCPIP[visa_board_num]::eth_ip_addr[::eth_lan_device_name][::visa_resource_type]
        if self.visa_conn_type == 'ethernet':
            visa_str = f"TCPIP{self.visa_board_num}::{self.eth_ip_addr}"
            if self.eth_lan_device_name is not None:
                visa_str += f"::{self.eth_lan_device_name}"

        # GPIB[visa_board_num]::primary_addr[::secondary_addr][::resource_type]
        elif self.visa_conn_type == 'gpib':
            visa_str = f"GPIB{self.visa_board_num}::{self.gpib_primary_addr}"
            if self.gpib_secondary_addr is not None:
                visa_str += f"::{self.gpib_secondary_addr}"

        # ASRL[serial_port][::visa_resource_type]
        elif self.visa_conn_type == 'serial':
            visa_str = f"ASRL{self.serial_port}"

        # USB[visa_board_num]::usb_mfr_id::usb_model_code::usb_serial_num[::usb_interface_num][::visa_resource_type]
        elif self.visa_conn_type == 'usb':
            visa_str = f"USB{self.visa_board_num}::{self.usb_vendor_id}::{self.usb_model_code}::{self.usb_serial_num}"
            if self.usb_interface_num is not None:
                visa_str += f"::{self.usb_interface_num}"

        # VXI[visa_board_num]::vxi_logical_addr[::visa_resource_type]
        elif self.visa_conn_type == 'vxi':
            visa_str = f"VXI{self.visa_board_num}::{self.vxi_logical_addr}"

        # PXI[visa_board_num]::pxi_device[::pxi_bus_num][::pxi_function][::visa_resource_type]
        elif self.visa_conn_type == 'pxi':
            visa_str = f"PXI{self.visa_board_num}::{self.pxi_device}"
            if self.pxi_bus_num is not None:
                visa_str += f"::{self.pxi_bus_num}"
            if self.pxi_function is not None:
                visa_str += f"::{self.pxi_function}"

        else:
            raise ValueError('Unsupported connection type')

        return f"{visa_str}::{self.visa_resource_type}"


class BaseVisaDeviceModel(BaseVisaResourceModel, BaseDeviceModel):
    pass
