import numpy as np
from typing import List
from math import ceil, log10
from logging import getLogger

from pygfdrivers.dtacq.models.scope_data import DtacqScopeDataModel

log = getLogger(__name__)


def pv(value: str) -> str:
    """ Parses the value from string and returns the value string """
    return value.split()[1]


def int_pv(value: str) -> int:
    """ Parses the value from string and returns it as an integer """
    return int(value.split()[1])


def float_pv(value: str) -> float:
    """ Parses the value from string and returns it as a float """
    return float(value.split()[1])


def format_raw_binary_data_for_channel(scope_info: DtacqScopeDataModel) -> None:
    try:
        for site, site_data in scope_info.sites.items():
            site_num = int(site.split('_')[1])
            site_chs = list(site_data.channels.keys())

            for ch in site_chs:
                ch_info = site_data.channels[ch]
                raw_data = ch_info.raw_data
                volt_range = ch_info.ch_range

                if raw_data is None:
                    raise ValueError(f"No raw data available for site {site_num} channel {ch}.")

                # Values are given in the range of a signed int16, and must be scaled using the voltage range
                int16_max = 2 ** 15

                # Always ensures that we can see the smallest resolution of the voltage range change.
                # One extra decimal place is added to avoid rounding errors.
                decimal_places = ceil(-log10(volt_range / int16_max)) + 1

                raw_data_array = np.array(raw_data)
                volts_array = np.round((raw_data_array / int16_max) * volt_range, decimal_places)
                volts: List[float] = volts_array.tolist()
                # volts = [round((x / int16_max) * volt_range, decimal_places) for x in raw_data]
                ch_info.volt_values.extend(volts)

                log.debug(f"Finished populating volt values for site '{site_num}' channel '{ch}'.")
    except Exception as e:
        log.error(f"Error formatting binary data : {e}")
