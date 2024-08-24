from typing import Union
from logging import getLogger
from fuzzywuzzy.fuzz import partial_ratio

# custom packages
from pygfdrivers.common.models.device.cmd import CmdClassType
from pygfdrivers.common.util.exceptions import SettingExceptions as set_err

log = getLogger(__name__)


def is_config_match(set_value: Union[str, int, float], query_value: Union[str, int, float]) -> bool:
    if isinstance(set_value, (int, float)) and query_value == set_value:
        log.debug(f"Query'{query_value}' and set '{set_value}' match.")
        return True

    elif isinstance(set_value, str) and partial_ratio(query_value, set_value) >= 80:
        log.debug(f"Query '{query_value}' and set '{set_value}' match.")
        return True

    else:
        log.warning(f"Query '{query_value}' and set '{set_value}' do not match.")
        return False


def is_valid_setting(cmd_obj: CmdClassType, cmd_key: str, setting: Union[str, int, float]) -> bool:
    cmd_args = cmd_obj.fetch_args(cmd_key)

    try:
        if cmd_args is not None and isinstance(cmd_args, (list, dict)):
            if isinstance(cmd_args, list) and setting not in cmd_args:
                raise set_err.SettingOptionError(setting, cmd_args)

            else:
                _max = cmd_args.get('max')
                _min = cmd_args.get('min')
                if _max is None or _min is None:
                    raise ValueError(f"Cannot validate setting without both 'max' and 'min' values.")
                if not (_min <= setting <= _max):
                    raise set_err.SettingRangeError(setting, _min, _max)
        return True

    except (set_err.SettingOptionError, set_err.SettingRangeError, ValueError) as e:
        log.warning(f"{e}")
        return False
