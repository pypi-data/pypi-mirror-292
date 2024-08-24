from pygfdrivers.common.visa.visa_cmd import BaseVisaScopeCommand
from pygfdrivers.common.visa.visa_scope import VisaScope
from pygfdrivers.common.util.utilities import has_prop, has_setter
from pygfdrivers.gf.models.digitizer_config import GFCaptureModel


class GFDigitizerCapture(BaseVisaScopeCommand):
    def __init__(self, visa_scope: VisaScope) -> None:
        super().__init__(visa_scope)

    def apply_capture_config(self, config: GFCaptureModel) -> None:
        try:  
            for field, setting in config.dict().items():
                if has_setter(self, field) and setting is not None:
                    setattr(self, field, setting)
        except Exception as e:
            self.log.error(f"Applying capture configuration encountered error: {e}")

    def fetch_capture_config(self, config: GFCaptureModel):
        try:
            for field in self.capture_fields:
                if has_prop(self, field):
                    setattr(config, field, getattr(self, field))
        except Exception as e:
            self.log.error(f"Fetching capture configuration encountered error: {e}")


    def format_channel(self, channel):
        """
        Checks format of command input is of channel = xx, as required by digitizer
        i.e channel must be a number in range [1,10]
        """
        try:
            if (1 <= int(channel) <= 10 ) & (len(str(channel)) <= 2):
                return str(channel).zfill(2)
            else:
                self.log.error(f"Incorrect data format for channel input")
        except Exception as e:
            self.log.error(f"Incorrect data format for channel input: {e}")

    def format_start(self, start):
        try:
            if (len(str(start)) <= 6) & (isinstance(start, (int, str))):
                return str(start).zfill(6)
            else:
                self.log.error(f"Incorrect data format for start input")
        except Exception as e:
            self.log.error(f"Incorrect data format for start input: {e}")

    def format_averages(self, averages):
        try:
            if (len(str(averages)) <= 3) & (isinstance(averages, (int, str))):
                return str(averages).zfill(3)
            else:
                self.log.error(f"Incorrect data format for averages input")
        except Exception as e:
            self.log.error(f"Incorrect data format for averages input: {e}")

    def format_num_points(self, points):
        try:
            points = int(32.0 * (int(points) // 32.0))
            if points >= 0:
                return str(points)
            else:
                self.log.error(f"Incorrect data format for gain input")
        except Exception as e:
            self.log.error(f"Incorrect data format for gain input: {e}")

    def get_data(self, channel: int, averages: int = None, start: int = None, points: int = None):
        channel= self.format_channel(channel)
        averages= self.format_averages(averages or self.acq_count)
        start= self.format_start(start or self.acq_start_sample)
        points = self.format_num_points(points or self.acq_total_samples)
        self.write(cmd=f"readdata chan={channel} avgs={averages} start={start} number={points}")

    @property
    def acq_count(self) -> int:
        return self._samples_to_avg
    
    @acq_count.setter
    def acq_count(self, count:int) -> None:
        self._samples_to_avg = count

    @property
    def time_range(self) -> float:
        return self._time_range
    
    @time_range.setter
    def time_range(self, range:int) -> None:
        self._time_range = range

    @property
    def time_zero(self) -> float:
        return self._time_zero
    
    @time_zero.setter
    def time_zero(self, value: float) -> None:
        self._time_zero = value

    @property
    def volt_range(self) -> float:
        return self._volt_range
    
    @volt_range.setter
    def volt_range(self, range: float) -> None:
        self._volt_range = range   

    @property
    def acq_total_samples(self) -> int:
        _samples = int(self.acq_srate * self.time_range)
        return _samples
    
    @acq_total_samples.setter
    def acq_total_samples(self, samples: int) -> None:
        self.time_range = float(samples/self.acq_srate) 

    @property
    def acq_start_sample(self) -> int:
        _start = int(self.acq_srate * self.time_zero)
        return _start
    
    @acq_start_sample.setter
    def acq_start_sample(self, start: int) -> None:
        self.time_zero = float(start/self.acq_srate)

    @property
    def acq_srate(self) -> int:
        return 5e6
