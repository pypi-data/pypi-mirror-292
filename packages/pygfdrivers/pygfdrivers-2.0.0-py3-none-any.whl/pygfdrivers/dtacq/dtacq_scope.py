import numpy as np
from time import sleep, time
from typing import Dict, List
from pydantic import BaseModel
from collections import defaultdict
from functools import cached_property

from acq400_hapi.acq400 import STATE, factory

from pygfdrivers.common.base_scope import BaseScope
from pygfdrivers.common.util.utilities import has_prop

from pygfdrivers.dtacq.util.utilities import pv
from pygfdrivers.dtacq.acq400_commands.trigger import DtacqTrigger
from pygfdrivers.dtacq.acq400_commands.acquire import DtacqAcquire
from pygfdrivers.dtacq.site_modules.modules_map import modules_map
from pygfdrivers.dtacq.models.scope_config import DtacqScopeConfigModel


class TIMEOUT:
    ARM = 10
    ABORT = 5
    DOWNLOAD = 10


class DtacqScope(BaseScope):
    def __init__(self, scope_config: DtacqScopeConfigModel = None) -> None:
        super().__init__(scope_config)

    def init(self):
        try:
            self.connect()
        except Exception as e:
            self.log.error(f"Initializing DTACQ scope encountered error: {e}")
            self.is_connected = False

    def apply_configurations(self):
        try:
            self.log.info("Applying scope configurations...")

            # Ensure that the DTACQ is in idle state before applying configurations
            target_state = STATE.str(STATE.IDLE)
            if self.transient_state != target_state:
                self.log.debug(f"Scope in '{self.transient_state}' and not '{target_state}'.")
                self.abort()

            self.log.info("Applying capture configurations...")
            self.acq_srate = self.config.capture.acq_srate
            self.acquire.set_time_range(self.config.capture.time_pre, self.config.capture.time_post)

            self.log.info("Applying trigger configurations...")
            self.trig_slope = self.config.trigger.trig_slope
            self.trig_source = self.config.trigger.trig_source

            self.log.info("Applying site channel configurations...")
            self.ai_modules.apply_site_config()

            self.log.info(f"Appyling transient configurations...")
            try:
                self.carrier.configure_transient(
                    pre                 = self.acquire.acq_pre_samples,
                    post                = self.acquire.acq_post_samples,
                    sig_DX              = self.trigger.trig_source,
                    auto_soft_trigger   = 1 if self.acquire.acq_pre_samples > 0 else 0,
                    demux               = 1,
                    edge                = self.trig_slope
                    )
            except Exception as e:
                self.log.error(f"Applying transient config encountered error: {e}")
                
            self.is_configured = True
            self.log.info("Finished applying scope configurations.")
        except Exception as e:
            self.log.error(f"Applying scope configurations encountered error: {e}.")
            self.is_configured = False

    def connect(self):
        try:
            # Function from pygfdrivers.dtacq to determine if ACQ2106 or some other acq400_commands
            self.carrier = factory(self.config.device.device_conn_str)
            # site 0 is always the motherboard
            self.motherboard = self.carrier.s0

            # Determine the site locations of the different modules and create appropriate module objects
            site_type_dict = self.carrier.get_site_types()
            self.init_site_obj(site_type_dict)
            self.master_site = self.ai_modules.master_site

            # Max constants required by acq400_commands to configure memory and clock
            self.min_clock = self.ai_modules.min_srate
            self.max_clock = self.ai_modules.max_srate
            self.max_samples = self.ai_modules.max_samples

            self.acquire = DtacqAcquire(self)
            self.trigger = DtacqTrigger(self)

            self.log.info(f"DTACQ SCOPE TYPE FOR SCOPE NAME ---- {self.name}")
            self.is_connected = True
        except Exception as e:
            self.log.info(f"DTACQ {self.name} failed to connect: {e}")
            self.is_connected = False

    def arm(self):
        self.log.info("Arming scope...")

        self.prep_shot()
        self.motherboard.set_knob('set_arm', True)

        state = STATE.RUNPRE if self.acquire.acq_pre_samples > 0 else STATE.ARM
        self.is_armed = self.wait_for_state(STATE.str(state), TIMEOUT.ARM)
        self.log.info(f"{'Scope armed.' if self.is_armed else 'Scope failed to arm.'}")

    def abort(self):
        self.log.info("Aborting scope...")
        self.motherboard.set_knob('TIM_CTRL_LOCK', 0)
        self.motherboard.set_knob('TRANSIENT_SET_ABORT', 1)
        sleep(1)
        self.motherboard.set_knob('streamtonowhered', 'stop')
        self.motherboard.set_abort = 1

        success = self.wait_for_state(STATE.str(STATE.IDLE))
        self.is_aborted = not success
        self.log.info(f"{'Scope aborted.' if success else 'Scope failed to abort.'}")

    def prep_shot(self) -> None:
        self.log.debug("Preparing shot...")
        self.carrier.statmon.stopped.clear()
        self.carrier.statmon.armed.clear()

        self.last_shot_num = self.shot_num
        self.clear_scope_info_data()
        self.is_downloaded = False
        self.is_triggered = False
        self.is_armed = False
        self.is_aborted = False
        self.data = None

    def trigger_software(self):
        self.log.debug("Software triggering scope...")
        self.motherboard.set_knob('soft_trigger', 1)
        self.is_triggered = True

    def disconnect(self):
        try:
            if self.is_connected:
                self.carrier.close()
                self.is_connected = False
                self.log.info("Disconnect attempt sucessful")
        except Exception as e:
            self.log.info(f"DTACQ {self.name} failed to disconnect: {e}")

    # ------------------------------------------------------------------------------------
    #  Read only methods
    # ------------------------------------------------------------------------------------

    @property
    def trigger_status(self) -> bool:
        # If we successfully triggered, our shot number should have increased.
        current_shot_num = self.shot_num
        trigger_status = (current_shot_num != self.last_shot_num)
        return trigger_status

    @property
    def transient_state(self) -> str:
        _transient_state = pv(self.motherboard.get_knob("TRANS_ACT_STATE"))
        if '_' in _transient_state:
            _transient_state = _transient_state.replace('_', '')
        # _transient_state = STATE.str(self.scope.statmon.get_state())
        self.log.debug(f"transient_state: '{_transient_state}'")
        return _transient_state

    @property
    def shot_num(self) -> int:
        try:
            _shot_num = int(self.motherboard.get_knob('shot_complete'))
            self.log.debug(f"shot_num: '{_shot_num}'")
            return _shot_num
        except Exception as e:
            self.log.error(f"Querying shot number encountered error: {e}")

    @property
    def idn(self) -> str:
        return self.carrier.get_sys_info()

    @cached_property
    def serial_num(self) -> str:
        return self.motherboard.get_knob('SERIAL')

    @cached_property
    def model(self) -> str:
        return self.motherboard.get_knob('MODEL')

    @cached_property
    def nchan(self) -> int:
        return int(self.motherboard.get_knob('NCHAN'))

    @property
    def sys_temps(self) -> Dict:
        _sys_temps = defaultdict(float)
        sys_temps = self.motherboard.get_knob('SYS_TEMP').split(',')
        for sys_temp in sys_temps:
            sys, value = sys_temp.split('=')
            _sys_temps[sys] = float(value)
        return _sys_temps

    # ------------------------------------------------------------------------------------
    # Data Capture Methods
    # ------------------------------------------------------------------------------------

    def fetch_data(self) -> None:
        try:
            self.log.debug(f"Populating data for active channels...")
            self.fetch_metadata()
            self.ai_modules.fetch_site_config()

            is_acq480 = 'acq480' in self.master_site.get_knob('module_name')
            pre_samples = self.acquire.acq_pre_samples if is_acq480 else None
            site_chs = 4 if is_acq480 else 16

            active_chs = []
            active_sites = self.config.active_sites
            for index, (_, chs) in enumerate(active_sites.items()):
                active_chs.extend([ch + (index * 16) for ch in chs])

            self.log.debug(f"Reading data from active_channels '{active_chs}'...")
            data_array = self.carrier.read_channels(active_chs)
            if data_array is None:
                raise ValueError("No data was obtained from the scope.")

            for index, ch in enumerate(active_chs):
                self.log.debug(f"Parsing read data and storing for channel '{ch}'.")
                site, site_ch = divmod(ch - 1, site_chs)
                site += 1

                if not is_acq480:
                    data = data_array[index]
                else:
                    data = np.concatenate([
                        data_array[index][:pre_samples],
                        data_array[(index + 2) % len(active_chs)][pre_samples:]
                    ])

                self.scope_info.sites[f"site_{site}"].channels[str(site_ch)].raw_data.extend(data.tolist())

            self.log.debug(f"Finished populating data for active channels.")
            self.fetch_metadata()
            self.data = self.scope_info
            self.is_downloaded = True
        except Exception as e:
            self.log.error(f"Downloading raw data encountered error: {e}")

    def fetch_metadata(self):
        self.log.info("Fetching site metadata...")

        try:
            for top_field in self.scope_info.model_fields:
                if top_field not in ['scope', 'active_sites', 'sites']:
                    config = getattr(self.scope_info, top_field)
                    for field in config.model_fields:
                        if has_prop(self, field):
                            setattr(config, field, getattr(self, field))
        except Exception as e:
            self.log.error(f"Fetching metadata encountered error: {e}")

    # ------------------------------------------------------------------------------------
    #  Helper Methods
    # ------------------------------------------------------------------------------------

    def wait_for_state(self, state: str = None, timeout: float = None) -> bool:
        self.log.debug(f"Waiting for scope to reach state '{state}' within timeout '{timeout}'.")
        success = False

        try:
            start = time()
            while self.transient_state != state:
                if timeout is not None and (time() - start) > timeout:
                    raise TimeoutError(f"Timeout occurred while waiting for transient state '{state}'.")
                sleep(0.1)
            success = True
        except TimeoutError:
            self.log.error(f"Timeout occurred while waiting for transient state '{state}'.")
        except Exception as e:
            self.log.error(f"Waiting for transient state '{state}' encountered error: {e}.")
        finally:
            return success

    def check_connection(self) -> bool:
        self.log.debug("Checking scope connection status...")

        try:
            self.is_connected = False if self.carrier.get_sys_info() is None else True
            self.log.debug(f"Scope connection status: {self.is_connected}.")
        except Exception as e:
            self.log.error(f"Checking connection encountered error: {e}")
            self.is_connected = False
        finally:
            return self.is_connected

    def init_site_obj(self, site_type_dict: Dict[str, List[int]]) -> None:
        self.log.debug("Creating site objects...")

        try:
            for site_type, site_list in site_type_dict.items():
                if site_list:
                    module_type = self.carrier.svc[f's{site_list[0]}'].get_knob('MTYPE')
                    sites_obj = modules_map[module_type](self, self.config)

                    if site_type == 'AISITES':
                        self.ai_modules = sites_obj
                    elif site_type == 'AOSITES':
                        self.ao_modules = sites_obj
                    elif site_type == 'DIOSITES':
                        self.dio_modules = sites_obj
                    else:
                        raise ValueError(f"Site type '{site_type}' not yet supported.")

                    self.find_master_site(sites_obj)
        except Exception as e:
            self.log.error(f"Creating site object encountered error: {e}.")

    def find_master_site(self, sites_obj) -> None:
        self.log.debug("Locating master site...")
        try:
            for site in sites_obj.sites_dict.values():
                if site.get_knob('module_role') == 'MASTER':
                    sites_obj.master_site = site
                    self.log.debug(f"master_site: '{site}'")
                    return

            raise ValueError("Cannot find 'MASTER' site.")
        except Exception as e:
            self.log.error(f"Finding master site encountered error: {e}.")
