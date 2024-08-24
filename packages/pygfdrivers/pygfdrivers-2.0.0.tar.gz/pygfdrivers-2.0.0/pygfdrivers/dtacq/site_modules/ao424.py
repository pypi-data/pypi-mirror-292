import numpy as np
from time import sleep

from acq400_hapi.acq400 import Acq400

from pygfdrivers.dtacq.site_modules.base_site import BaseSite
from pygfdrivers.dtacq.models.scope_config import DtacqScopeConfigModel


class AO424(BaseSite):
    def __init__(self, dtacq: Acq400 = None, config: DtacqScopeConfigModel = None) -> None:
        super().__init__(dtacq, config)
        
        self.init()

    def init(self):
        raise NotImplementedError

    def stop_awg(self):
        self.master_site.awg_abort = "1"

    def load_wave(self):
        # file = "C:/py-sandbox/32interleaved_sine.dat"
        file = "C:/py-sandbox/waveform_test.dat"
        reps = 1
        extend = 1
        self.awg = self.master_site.modules[self.master_site.awg_site]
        
        self.awg.trg = "1,1,1"
        self.awg.CLKDIV = 1
        
        for rep in range(0, reps):
            if rep > 0:
                print("rep {}".format(rep))
                
            self.awg.awg_abort = "1"
            loaded = 0
            
            while loaded != 1:
                try:
                    with open(file, "rb") as fd:
                        self.master_site.load_awg(self.extend_wave(fd, extend))
                        loaded = 1 
                except Exception as e:
                    if loaded == 0:
                        print("First time: caught {}, abort and retry".format(e))
                        loaded = -1
                        self.awg.playloop_oneshot = "1"
                        self.awg.awg_abort = "1"
                        sleep(0.1)
                    else:
                        print("Retry failed: caught {} FAIL".format(e))
                        exit(1)
                        
        print("playloop_length {}".format(self.awg.playloop_length))

    def wait_for_completion(self):
        """
        Waits for trigger to be received.
        """
        mode = self.config.AWG["mode"]
        if mode == 1:
            while self.awg.task_active == '1' or  self.awg.completed_shot == '0':
                sleep(0.1)
            print("Polling completion")
        if mode == 2:
            print(f"Mode is {self.config.AWG['mode']}")
            pass

    @staticmethod
    def extend_wave(fd, ext_count):
        buf = fd.read()
        buf0 = buf

        while ext_count > 1:
            buf += buf0
            ext_count -= 1

        return buf

    @staticmethod
    def make_wave():
        """
        Sends a single software trigger to begin sampling.
        """
        fileName = "waveform_test.dat"
        amplitude = 1
        length = 100000
        nchan = 16
        offset = 0.1
        
        x = np.linspace(0, 8*np.pi, length)
        y = amplitude * np.sin(x) 
        volts = np.zeros([length, nchan])
        for ch in range(nchan):
            volts[:, ch] = np.add(y, ch * offset)
        
        raw = (volts * 32767/10).astype(np.int16)
        raw.tofile(fileName)
        
        # x = np.linspace(0, 8*np.pi, int(1e5))
        # y = 32767 * np.sin(x) # full scale in 16 bit DAC codec
        
        # # Extend since wave over nchan channels
        # interleaved_waves = []
        # nchan = 16
        # for elem in y:
        #     interleaved_waves.extend(nchan*[elem])
        
        # interleaved_waves = np.array((interleaved_waves)).astype(np.int16)
        # interleaved_waves.tofile(fileName)
