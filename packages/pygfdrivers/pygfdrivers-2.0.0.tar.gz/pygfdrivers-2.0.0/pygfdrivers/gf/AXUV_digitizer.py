# AXUV driver ported from Roberts Pi3 Script
# Author: Simon Marcotte
# Date: May 9 2024

import os
import paramiko

from pygfdrivers.gf.models.AXUV_digitizer_config import AXUVDigitizerConfig
from pygfdrivers.common.base_device import BaseDevice


class AXUV_digitizer(BaseDevice):
    def __init__(self, AXUV_config: AXUVDigitizerConfig = None) -> None:
        super().__init__(AXUV_config)
        self.apply_configurations()

    def init(self):
        self.connect()

    def connect(self) -> None:
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.hostname, username=self.username, password=self.password)
            self.sftp = self.ssh.open_sftp()
            self.is_connected = True
            self.log.info(f"Connected to AXUV digitizer at '{self.hostname}'.")
        except Exception as e:
            self.is_connected = False
            self.log.error(f"Failed to connect to AXUV digitizer at '{self.hostname}': {e}")

    def save_data(self):
        # Transfer the updated CSV file to the target folder within the local_folder
        target_folder = self.save_path

        if os.path.exists(target_folder) and os.path.isdir(target_folder):
            local_target_file = os.path.join(target_folder, 'AXUVDCH_DATA.csv')
            self.sftp.get(self.remote_file, local_target_file)
            self.log.info(f"Updated CSV file transferred successfully to folder '{target_folder}'.")
            self.is_downloaded = True
        else:
            self.log.error(f"Target folder '{target_folder}' does not exist.")

    def disconnect(self) -> None:
        if self.is_connected:
            try:
                if self.sftp:
                    try:
                        self.sftp.close()
                        self.log.info("SFTP connection closed.")
                    except Exception as e:
                        self.log.warning(f"Failed to close SFTP connection: {e}")
                if self.ssh:
                    try:
                        self.ssh.close()
                        self.log.info("SSH connection closed.")
                    except Exception as e:
                        self.log.warning(f"Failed to close SSH connection: {e}")
            except Exception as e:
                self.log.error(f"Failed to disconnect properly: {e}")
            finally:
                self.is_connected = False

    def check_connection(self) -> bool:
        try:
            if self.ssh is None or self.sftp is None:
                self.is_connected = False
            else:
                self.ssh.exec_command('ls')     # Use the exec_command to check SSH connection
                self.sftp.listdir('.')          # Check if SFTP connection is open
                self.is_connected = True
        except Exception as e:
            self.log.error(f"Checking connection encountered error: {e}")
            self.is_connected = False
        finally:
            return self.is_connected

    def apply_configurations(self) -> None:
        try:
            self.hostname = self.config.device.hostname
            self.username = self.config.device.username
            self.password = self.config.device.password
            self.remote_file = self.config.device.remote_file
            self.is_configured = True
        except Exception as e:
            self.log.error(f"Applying configuration encountered error: {e}")
            self.is_configured = False

    def arm(self):
        self.prep_shot()

    def prep_shot(self) -> None:
        self.is_downloaded = False
        self.is_aborted = False

    def fetch_data(self, *args, **kwargs) -> None:
        return super().fetch_data(*args, **kwargs)

    def fetch_metadata(self, *args, **kwargs) -> None:
        return super().fetch_metadata(*args, **kwargs)
    
    def abort(self) -> None:
        self.is_aborted = True

    def trigger_status(self) -> bool:
        return True
