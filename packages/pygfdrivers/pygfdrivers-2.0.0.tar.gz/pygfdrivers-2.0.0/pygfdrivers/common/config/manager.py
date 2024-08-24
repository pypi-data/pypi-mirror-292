import os
from pydantic import BaseModel
from collections import defaultdict
from typing import Dict, ValuesView
from asyncio import AbstractEventLoop, get_event_loop

from pygfdrivers.common.model_map import model_map
from pygfdrivers.common.device_map import device_map
from pygfdrivers.common.base_device import BaseDevice
from pygfdrivers.common.util.utilities import open_yaml
from pygfdrivers.common.util.logger_manager import LoggerManager, LOGGING_MODE


# TODO: Need to save the config files after creating the device object
class ConfigManager:
    log = LoggerManager('ConfigManager', LOGGING_MODE.INFO).log

    def __init__(
            self,
            config_dir: str = None,
            loop: AbstractEventLoop = get_event_loop()
    ) -> None:
        self.loop = loop

        self.config_dir = config_dir    # or get_repo_config_dir()

        self.config_dicts = defaultdict(dict)
        self.connected_devices = defaultdict(list)

        self.init()

    def init(self) -> None:
        try:
            self.process_config_files()
            for config_type, configs in self.config_dicts.items():
                if config_type == 'clients':
                    self.client_name, self.client_config = list(configs.items())[0]
                else:
                    self.create_and_init_device_objs(configs.values(), config_type)
        except Exception as e:
            self.log.error(f"Initializing configuration manager encountered error: {e}")

    def process_config_files(self) -> None:
        """ Processes the configuration files in the config directory. """
        for entry in os.listdir(self.config_dir):
            entry_path = os.path.join(self.config_dir, entry)

            if os.path.isdir(entry_path):
                config_type = entry.rstrip('s')
                file_paths = [os.path.join(entry_path, file_name) for file_name in os.listdir(entry_path)]
            elif os.path.isfile(entry_path):
                config_type, _ = os.path.splitext(os.path.basename(entry))
                file_paths = [entry_path]
            else:
                raise ValueError(f"Invalid config file path: {entry_path}")

            for file_path in file_paths:
                config_dict = open_yaml(file_path)
                config_key = config_dict[f"{config_type}_settings"][f"{config_type}_type"]
                self.create_config_obj(config_dict, config_type, config_key)

    @staticmethod
    def get_config_name(config_obj: BaseModel, config_type: str) -> str:
        """ Determines the name of the configuration object. """
        config_type_obj = getattr(config_obj, config_type)
        for field in config_type_obj.model_fields:
            if field.startswith(('client', 'device')) and field.endswith('name'):
                return getattr(config_type_obj, field)

        raise ValueError("Missing 'device' or 'client' name field.")

    def create_config_obj(self, config_dict: Dict, config_type: str, config_key: str) -> None:
        """
        Create and store pydantic data class objects based on the configuration type which is denoted by "..._type"
        field in the yaml/yml file being passed into the method. Anything not mapped or named, we store anyway.
        """
        try:
            config_class = model_map[f"{config_type}s"].get(config_key)
            if not config_class:
                raise ValueError(f"No mapping associated to config type '{config_type}s'.")

            try:
                config_obj = config_class(**config_dict)
            except Exception as e:
                raise ValueError(f"Failed to instantiate config obj with error: {e}")

            # Defaultdict allows creation of new dictionaries if it doesn't exist, but appends the data if it does.
            # Avoid the need to check if the dictionary exists, handling its errors and then creating the dictionary.
            config_name = ConfigManager.get_config_name(config_obj, config_type)
            self.config_dicts[f"{config_type}s"][config_name] = config_obj

        except Exception as e:
            self.log.error(f"Creating config object for '{config_key}' encountered error: {e}.")

    def create_and_init_device_objs(self, device_configs: ValuesView, hw_type: str) -> None:
        """
        Creates and initializes (runs __init__ method) the objects based on the obj_type passed into the method
        and also runs the objects initalize() method.
        """
        device_type_map = device_map.get(hw_type)
        try:
            if device_type_map is None:
                raise ValueError(f"No mapping associated to device type '{hw_type}'.")

            for device_config in device_configs:
                device_key = getattr(device_config, f"{hw_type.rstrip('s')}").device_type

                device_class = device_type_map.get(device_key)
                if not device_class:
                    raise ValueError(f"No class or mapping associated to device key '{device_key}'.")

                device_obj = device_class(device_config, hw_type.rstrip('s'))
                self.init_device_obj(device_obj)
                self.store_device_obj(device_obj, hw_type)

        except Exception as e:
            self.log.error(f"Initializing '{hw_type}' encountered error: {e}")

    def init_device_obj(self, device_obj: BaseDevice) -> None:
        self.log.debug(f"Initializing device object '{device_obj}'.")

        try:
            device_obj.init()
        except Exception as e:
            self.log.error(f"Initializing device obj '{device_obj}' encountered error: {e}")

    def store_device_obj(self, device_obj: BaseDevice, device_type: str) -> None:
        """ Stores the initialized device object in the connected_devices dictionary. """
        self.log.debug(f"Adding '{device_obj}' to connected devices.")

        try:
            self.connected_devices.setdefault(device_type, []).append(device_obj)
        except Exception as e:
            self.log.error(f"Adding '{device_obj}' to connected_devices encountered error: {e}")
