from typing import List, Dict, Union
from functools import cached_property

from acq400_hapi.acq400 import Acq400

from pygfdrivers.common.util.utilities import has_prop, has_setter
from pygfdrivers.dtacq.models.scope_data import DtacqSiteDataModel
from pygfdrivers.dtacq.models.scope_config import DtacqScopeConfigModel, DtacqSiteModel


class BaseSite:
    def __init__(self, dtacq: Acq400 = None, config: DtacqScopeConfigModel = None) -> None:
        self.dtacq = dtacq
        self.log = self.dtacq.log
        self.carrier = self.dtacq.carrier
        self.config = config or self.dtacq.config

        self.master_site = None
        self.site_configs = self.dtacq.config.sites
        self.site_infos = self.dtacq.scope_info.sites
        self.sites_dict = self.carrier.modules.copy()
        self.active_sites = self.config.active_sites

    def apply_site_config(
            self,
            active_sites: Dict[str, List[int]] = None,
            site_configs: Dict[str, DtacqSiteModel] = None
    ) -> None:
        configs = site_configs or self.site_configs
        active_sites = active_sites or self.active_sites

        try:
            for site in active_sites:
                site_num = int(site.split('_')[1])
                self.site = self.sites_dict.get(site_num)
                if self.site is None:
                    raise ValueError(f"Site '{site_num}' not installed in carrier.")

                active_chs = active_sites[site]
                site_config = configs[site]

                for ch in active_chs:
                    self.site_ch = str(ch).zfill(2)
                    ch_config = site_config.channels[ch]
                    for field, setting in ch_config.dict().items():
                        if has_setter(self, field) and setting is not None:
                            self.log.debug(f"[SITE: {site_num}] Setting channel '{ch}' '{field}' to '{setting}'...")
                            setattr(self, field, setting)

        except Exception as e:
            self.log.error(f"Applying site configuration encountered error: {e}")

    def fetch_site_config(
            self,
            active_sites: Dict[str, List[int]] = None,
            site_infos: Dict[str, DtacqSiteDataModel] = None
    ) -> None:

        infos = site_infos or self.site_infos
        active_sites = active_sites or self.active_sites

        try:
            for site in active_sites:
                site_num = int(site.split('_')[1])
                self.site = self.sites_dict.get(site_num)
                if self.site is None:
                    raise ValueError(f"Site '{site_num}' not installed in carrier.")

                active_chs = active_sites[site]
                site_info = infos[site]

                for ch in active_chs:
                    self.site_ch = str(ch).zfill(2)
                    ch_info = site_info.channels[str(ch)]
                    for field in ch_info.model_fields:
                        if has_prop(self, field):
                            self.log.debug(f"[SITE: {site_num}] Fetching channel '{ch}' '{field}'...")
                            setattr(ch_info, field, getattr(self, field))

        except Exception as e:
            self.log.error(f"Fetching site configuration encountered error: {e}")

    def set_site(self, site: int = None, abs_ch: int = None) -> None:
        if site is None and abs_ch is not None:
            site, _ = divmod(abs_ch - 1, self.nchan)
            site += 1  # Adjust site number to start from 1

        self.site = self.sites_dict.get(site)

        if self.site is None:
            raise ValueError(f"No daq module, or wrong module type installed in this site.")

    def set_site_knob(self, setter: str, site: int, setting: Union[int, float, bool, str], site_ch: int = None) -> None:
        self.site_ch = str(site_ch).zfill(2) if site_ch is not None else None
        try:
            self.set_site(site)
            setattr(self, setter, setting)
        except Exception as e:
            self.log.error(f"Setting '{setter}' for site '{site}', channel '{site_ch}' encountered error: {e}")

    def get_site_knob(self, getter: str, site: int, site_ch: int = None) -> Union[int, float, bool, str]:
        self.site_ch = str(site_ch).zfill(2) if site_ch is not None else None
        try:
            self.set_site(site)
            return getattr(self, getter)
        except Exception as e:
            self.log.error(f"Fetching '{getter}' for site '{site}', channel '{site_ch}' encountered error: {e}")

    # ------------------------------------------------------------------------------------
    # Read Only Methods
    # ------------------------------------------------------------------------------------

    @cached_property
    def max_srate(self) -> int:
        _max_srate = int(self.master_site.get_knob('MAX_KHZ')) * 1000
        return _max_srate

    @cached_property
    def min_srate(self) -> int:
        _min_srate = int(self.master_site.get_knob('MIN_KHZ')) * 1000
        return _min_srate

    @cached_property
    def nchan(self) -> int:
        _nchan = int(self.master_site.get_knob('NCHAN'))
        return _nchan
