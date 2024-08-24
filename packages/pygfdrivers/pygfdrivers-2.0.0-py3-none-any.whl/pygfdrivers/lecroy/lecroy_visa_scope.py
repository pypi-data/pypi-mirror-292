from time import sleep

from pygfdrivers.common.visa.visa_scope import VisaScope

from pygfdrivers.lecroy.visa_commands.common import LecroyCommon
from pygfdrivers.lecroy.visa_commands.acquire import LecroyAcquire
from pygfdrivers.lecroy.visa_commands.channel import LecroyChannel
from pygfdrivers.lecroy.visa_commands.trigger import LecroyTrigger
from pygfdrivers.lecroy.visa_commands.timebase import LecroyTimebase
from pygfdrivers.lecroy.visa_commands.waveform import LecroyWaveform

from pygfdrivers.lecroy.models.scope_config import LecroyScopeConfigModel


class LecroyVisaScope(VisaScope):
    def __init__(self, scope_config: LecroyScopeConfigModel = None) -> None:
        # Not all LeCroy VISA devices are like this, so we may need something more dynamic than this in the future
        scope_config.device.visa_board_num = 0
        scope_config.device.visa_conn_type = 'ethernet'
        scope_config.device.visa_resource_type = 'INSTR'
        scope_config.device.eth_lan_device_name = 'inst0'
        super().__init__(scope_config)
    
    def init(self) -> None:
        super().init()

        try:
            if self.scope is None:
                raise ValueError("LeCroy VISA scope did not connect properly.")

            self.scope.timeout = 60_000  # 1 minute in milliseconds
            self.scope.chunk_size = 20 * 1024 * 1024

            self.common = LecroyCommon(self)
            self.acquire = LecroyAcquire(self)
            self.channel = LecroyChannel(self)
            self.trigger = LecroyTrigger(self)
            self.timebase = LecroyTimebase(self)
            self.waveform = LecroyWaveform(self)

            self.common.comm_header('off')
            self.active_chs = self.config.active_channels

            self.log.info(f"LECROY SCOPE TYPE FOR SCOPE NAME ---- {self.name}")
        except Exception as e:
            self.log.error(f"Initializing LeCroy VISA scope encountered error: {e}")

    def apply_configurations(self):
        self.log.info("Applying scope configurations...")

        try:
            self.log.info("Applying trigger configurations...")
            self.trigger.apply_trig_config(self.config.trigger)

            self.log.info("Applying capture configurations...")
            self.timebase.apply_time_config(self.config.capture)
            self.acquire.apply_acq_config(self.config.capture)

            self.log.info("Applying channel configurations...")
            self.channel.apply_ch_config(self.active_chs, self.config.channels)

            self.log.info("Applying scope configurations has finished.")
            self.is_configured = True
        except Exception as e:
            self.log.error(f"Applying scope configurations encountered error: {e}.")
            self.is_configured = False

    def arm(self):
        self.log.info("Arming scope...")
        try:
            self.prep_shot()
            self.common.single_mode()
            sleep(self.scope_talk_delay)

            self.is_armed = True
            self.log.info(f"Scope {'armed.' if self.arm_status else 'failed to arm.'}")
        except Exception as e:
            self.log.info(f"Arming scope encountered error: {e}")

    def abort(self) -> None:
        self.log.info("Aborting scope...")
        try:
            self.common.stop_mode()
            self.log.info("Scope aborted.")
            self.is_aborted = True
        except Exception as e:
            self.log.error(f"Aborting scope encountered error: {e}")

    def trigger_software(self) -> None:
        self.trigger.trig_force()
        self.is_triggered = True

    def prep_shot(self) -> None:
        self.clear_scope_info_data()
        self.is_armed = False
        self.is_aborted = False
        self.is_triggered = False
        self.is_downloaded = False

    def check_connection(self) -> bool:
        try:
            query = self.common.idn
            self.is_connected = True if query is not None else False
        except Exception as e:
            self.log.error(f"Checking connection encountered error: {e}")
            self.is_connected = False
        finally:
            return self.is_connected

    # ------------------------------------------------------------------------------------
    #  Read Only Methods
    # ------------------------------------------------------------------------------------

    @property
    def arm_status(self) -> bool:
        try:
            status_code = self.common.status
            _arm_status = status_code == 8192
            self.log.info(f"Armed Status: {_arm_status}")
            return _arm_status
        except Exception as e:
            self.log.error(f"Querying arm status encountered error: {e}")

    @property
    def trigger_status(self) -> bool:
        try:
            status_code = self.common.status
            _trigger_status = status_code == 8193
            self.log.info(f"Trigger Status: {_trigger_status}")
            return _trigger_status
        except Exception as e:
            self.log.error(f"Querying trigger status encountered error: {e}")
            return False

    # ------------------------------------------------------------------------------------
    #  Data Storage Methods
    # ------------------------------------------------------------------------------------

    def fetch_data(self) -> None:
        self.log.info("Downloading real-time data...")
        try:
            for ch in self.active_chs:
                self.log.info(f"Downloading wave source '{ch}'...")
                data = self.waveform.wave_data(f"c{ch}")
                self.scope_info.channels[str(ch)].raw_data.append(data)

            self.fetch_metadata()
            self.data = self.scope_info
            self.is_downloaded = True
        except Exception as e:
            raise ValueError(f"Failed downloading data with error: {e}.")

    def fetch_metadata(self) -> None:
        self.log.info("Fetching channel metadata...")

        try:
            for top_field in self.scope_info.model_fields:
                if top_field not in ['scope', 'active_channels']:
                    if top_field == 'capture':
                        self.acquire.fetch_acq_config(self.scope_info.capture)
                        self.timebase.fetch_time_config(self.scope_info.capture)
                    elif top_field == 'trigger':
                        self.trigger.fetch_trig_config(self.scope_info.trigger)
                    elif top_field == 'channels':
                        self.channel.fetch_ch_config(self.active_chs, self.scope_info.channels)
        except Exception as e:
            self.log.error(f"Fetching metadata encountered error: {e}")
