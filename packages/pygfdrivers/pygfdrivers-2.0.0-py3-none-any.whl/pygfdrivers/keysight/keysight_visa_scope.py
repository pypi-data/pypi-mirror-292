from time import sleep, perf_counter
from pydantic import BaseModel

from pygfdrivers.common.visa.visa_scope import VisaScope
from pygfdrivers.common.util.fetch_device_models import fetch_keysight_series

from pygfdrivers.keysight.visa_commands.root import KeysightRoot
from pygfdrivers.keysight.visa_commands.common import KeysightCommon
from pygfdrivers.keysight.visa_commands.acquire import KeysightAcquire
from pygfdrivers.keysight.visa_commands.channel import KeysightChannel
from pygfdrivers.keysight.visa_commands.trigger import KeysightTrigger
from pygfdrivers.keysight.visa_commands.timebase import KeysightTimebase
from pygfdrivers.keysight.visa_commands.waveform import KeysightWaveform
from pygfdrivers.keysight.models.scope_config import KeysightScopeConfigModel


class KeysightVisaScope(VisaScope):
    def __init__(self, scope_config: KeysightScopeConfigModel = None) -> None:
        # Not all Keysight VISA devices are like this, so we may need something more dynamic than this in the future
        scope_config.device.visa_board_num = 0
        scope_config.device.visa_conn_type = 'ethernet'
        scope_config.device.visa_resource_type = 'INSTR'
        scope_config.device.eth_lan_device_name = 'inst0'
        super().__init__(scope_config)

    def init(self) -> None:
        super().init()
            
        try:
            if self.scope is None:
                raise ValueError("Keysight VISA scope did not connect properly.")

            self.keysight_model = self.scope_series
            self.max_chs = 8 if self.keysight_model == 'MXR' else 4

            self.root = KeysightRoot(self)
            self.common = KeysightCommon(self)
            self.acquire = KeysightAcquire(self)
            self.channel = KeysightChannel(self)
            self.trigger = KeysightTrigger(self)
            self.timebase = KeysightTimebase(self)
            self.waveform = KeysightWaveform(self)
            self.acquire.has_segment_mode = 'sgm' in self.common.options

            self.log.info(f"KEYSIGHT SCOPE TYPE FOR SCOPE NAME ---- {self.name}")
        except Exception as e:
            self.log.error(f"Initializing Keysight VISA scope encountered error: {e}")

    def apply_configurations(self) -> None:
        # When applying configurations, we do so in stop mode as the scope has certain settings that
        # can only be queried when in stop mode which is required as we set and verify the settings.
        self.log.info(f"Applying scope configurations...")

        try:
            self.root.stop_mode()

            self.log.info(f"Applying trigger configurations...")
            self.trigger.apply_trig_config(self.config.trigger)

            self.log.info(f"Applying timebase configurations...")
            self.timebase.apply_time_config(self.config.capture)

            self.log.info(f"Applying acquire configurations...")
            self.acquire.apply_acq_config(self.config.capture)

            self.log.info(f"Applying channel configurations...")
            self.channel.apply_ch_config(self.config.active_channels, self.config.channels)

            self.log.info(f"Applying waveform configurations...")
            self.waveform.apply_wave_config(self.config.active_channels, self.config.channels)

            self.log.info(f"Applying scope configurations has finished.")
            self.active_chs = self.config.active_channels
            self.is_configured = True
        except Exception as e:
            self.log.error(f"Applying scope configurations encountered error: {e}.")
            self.is_configured = False
            # Maybe set the scope to a known working setup here if the configuration fails so that we can ensure
            # that data is always collected regardless of the setting

    def arm(self) -> None:
        self.log.info(f"Arming scope...")
        try:
            self.prep_shot()
            self.root.single_mode()
            sleep(self.scope_talk_delay)

            self.is_armed = True
            self.log.info(f"Scope {'armed.' if self.arm_status else 'failed to arm.'}")
        except Exception as e:
            self.log.error(f"Arming scope encountered error: {e}.")

    def abort(self) -> None:
        """
        Stop any ongoing acquisition, clear status register and clear trigger flag
        """
        self.log.info(f"Aborting scope...")
        try:
            self.root.stop_mode()
            self.common.clear_status()
            self.is_aborted = True
            self.log.info(f"Scope aborted.")
        except Exception as e:
            self.log.error(f"Aborting scope encountered error: {e}.")

    def prep_shot(self) -> None:
        self.log.info(f"Preparing shot...")

        try:
            self.common.clear_status()

            # Putting the scope in run mode then stop mode clears the FIFO buffer, so we do this twice
            # to be doubly sure that the buffer is cleared from previous data.
            for _ in range(2):
                self.root.run_mode()
                self.root.stop_mode()

            # Reading arm and trigger status clears the flag, but for some reason, not all the time,
            # the flags don't clear, so we read them until they read false.
            while self.trigger_status or self.arm_status:
                sleep(self.scope_talk_delay)

            # Finally, clear the persistent flags and data values from parent class BaseScope
            self.clear_scope_info_data()
            self.is_downloaded = False
            self.is_triggered = False
            self.is_armed = False
            self.is_aborted = False
            self.data = None
            self.log.info(f"Finished preparing shot.")
        except Exception as e:
            self.log.error(f"Preparing shot encountered error: {e}.")
            # Maybe abort the scope settings or reapply with some default settings so that preparing the shot
            # does not impede the ability to capture data.

    def trigger_software(self) -> None:
        try:
            trig_count = self.segment_count_to_acq if self.in_segment_mode else 1
            for i in range(1, trig_count+1):
                self.trigger.trig_force()
                sleep(self.scope_talk_delay)
            self.is_triggered = True
            self.log.info(f"Software triggered.")
        except Exception as e:
            self.log.error(f"Software triggering scope encountered error: {e}.")

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
            _is_armed = self.root.arm_status
            self.log.debug(f"Armed Status: {_is_armed}")
            return _is_armed
        except Exception as e:
            self.log.error(f"Querying arm status encountered error: {e}")

    @property
    def trigger_status(self) -> bool:
        try:
            _trigger_status = self.all_segments_acqd if self.in_segment_mode else self.root.trigger_status
            self.log.debug(f"Trigger Status: {_trigger_status}")
            return _trigger_status
        except Exception as e:
            self.log.error(f"Querying trigger status encountered error: {e}")
            return False

    @property
    def in_segment_mode(self) -> bool:
        _in_segment_mode = 'segm' in self.acquire.acq_mode
        self.log.debug(f"in_segment_mode: {_in_segment_mode}")
        return _in_segment_mode

    @property
    def segment_count_to_acq(self) -> int:
        _segment_count_to_acq = self.acquire.acq_segment_count
        self.log.debug(f"segments_to_acq: {_segment_count_to_acq}")
        return _segment_count_to_acq

    @property
    def segment_count_acqd(self) -> int:
        _segment_count_acqd = self.waveform.wave_segment_count
        self.log.debug(f"segment_count_acqd: {_segment_count_acqd}")
        return _segment_count_acqd

    @property
    def all_segments_acqd(self) -> bool:
        _all_segments_acqd = self.segment_count_acqd == self.segment_count_to_acq
        self.log.debug(f"all_segments_acqd: {_all_segments_acqd}")
        return _all_segments_acqd

    # ------------------------------------------------------------------------------------
    #  Data Storage Methods
    # ------------------------------------------------------------------------------------

    def fetch_data(self) -> None:
        is_segmented = self.in_segment_mode
        self.log.info(f"Downloading {'segmented' if is_segmented else 'real-time'} data...")
        try:
            loop_start_time = perf_counter()
            for segment in range(1, (self.segment_count_acqd + 1) if is_segmented else 2):
                if is_segmented:
                    self.log.info(f"Downloading segment '{segment}' waveforms...")
                    setattr(self.acquire, 'acq_segment_index', segment)

                for ch in self.active_chs:
                    start_time = perf_counter()
                    self.log.info(f"Downloading segment '{segment}', wave source '{ch}' data...")
                    ch_info = self.scope_info.channels[str(ch)]
                    setattr(self.waveform, 'wave_source', ch)

                    data = getattr(self.waveform, 'wave_data')
                    ch_info.raw_data.append(data)

                    self.log.debug(f"Downloading wave source '{ch}' number of segments captured...")
                    segments = getattr(self.waveform, 'wave_segment_count')
                    ch_info.wave_segment_count = segments

                    self.log.debug(f"Downloading wave source '{ch}' total points captured...")
                    num_points = getattr(self.waveform, 'wave_points')
                    ch_info.wave_points = (ch_info.wave_points or 0) + num_points

                    self.log.debug(f"Downloading wave source '{ch}' trigger times...")
                    ttag = getattr(self.waveform, 'wave_segment_ttag')
                    ch_info.wave_segment_ttag.append(ttag)
                    self.log.debug(f"Time to download channel {ch} data: {perf_counter() - start_time:.3f} seconds.")

            elapsed_time = perf_counter() - loop_start_time
            self.log.debug(f"Time to download {len(self.active_chs)} channel(s) data: {elapsed_time:.3f} seconds.")
            self.fetch_metadata()
            self.data = self.scope_info
            self.is_downloaded = True
        except Exception as e:
            raise ValueError(f"Failed downloading {'segmented' if is_segmented else 'real-time'} data with error: {e}.")

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
                        self.waveform.fetch_wave_config(self.active_chs, self.scope_info.channels)
        except Exception as e:
            self.log.error(f"Fetching metadata encountered error: {e}")
