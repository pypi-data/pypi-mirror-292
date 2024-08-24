import bson
import orjson
import yaml
import pandas as pd
from typing import Dict, Union
from pydantic import BaseModel

from pygfdrivers.common.util.logger_manager import LOGGING_MODE, LoggerManager


class SaveUtil:
    def __init__(self) -> None:
        self.log = LoggerManager("SaveUtil", LOGGING_MODE.DEBUG).log
        self.FILE_OPTIONS = {
            'csv': SaveUtil.save_csv,
            'yaml': SaveUtil.save_yaml,
            'bson': SaveUtil.save_bson,
            'json': SaveUtil.save_json,
        }

    def save_file(self, data: Union[Dict, BaseModel], file_path: str, file_option: str = 'bson') -> None:
        """
        Save the data to a file.
        """
        # To allow for the saving of a dictionary or a data object
        try:
            if not isinstance(data, dict):
                data = data.model_dump(by_alias=True, exclude_none=True)

            assert (isinstance(file_option, str))
            file_option = file_option.lower()

            if file_option not in self.FILE_OPTIONS:
                raise ValueError(f"File Option was {file_option}, but must be: {self.FILE_OPTIONS.keys()}")

            self.FILE_OPTIONS[file_option](data, file_path)
            self.log.info(f"File saved to: {file_path}.{file_option}")
        except (FileNotFoundError, FileExistsError) as e:
            self.log.error(f"Saving file encountered error with file location: {e}")
        except Exception as e:
            self.log.error(f"Saving file encountered error: {e}")

    @staticmethod
    def save_bson(data: Dict, file_path: str) -> None:
        """
        Save the data to a bson file.
        """
        file_path += '.bson'
        with open(file_path, 'wb') as file:
            file.write(bson.BSON.encode(data))

    @staticmethod
    def save_json(data: Dict, file_path: str) -> None:
        """
        Save the data to a json file.
        """
        file_path += '.json'

        with open(file_path, 'wb') as json_file:
            json_file.write(orjson.dumps(data, option=orjson.OPT_SERIALIZE_NUMPY))

    @staticmethod
    def save_csv(data: Dict, file_path: str) -> None:
        """
        Save the data to a csv file.
        """
        file_path += '.csv'
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)

    @staticmethod
    def save_yaml(data: Dict, file_path: str) -> None:
        """
        Save the data to a yaml file.
        """
        file_path += '.yaml'

        with open(file_path, 'w') as file:
            yaml.dump(data, file, default_flow_style=False)
