import os
import sys
import time
import platform
import subprocess
from subprocess import Popen,PIPE,STDOUT
from pathlib import Path
from dtaf_core.drivers.base_driver import BaseDriver
from dtaf_core.lib.configuration import ConfigurationHelper

class UsbblasterDriver(BaseDriver):
    def __init__(self, cfg_opts, log):
        super(UsbblasterDriver, self).__init__(cfg_opts, log)
        self.__cpld_app_path = self._driver_cfg_model.cpld_application_path

    def __enter__(self):
        return super(UsbblasterDriver, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(UsbblasterDriver, self).__exit__(exc_type, exc_val, exc_tb)

    def health_status_check_usbblaster(self):
        self.__cpld_app_path += "\quartus_pgm.exe"
        cmd = (self.__cpld_app_path + " -c 1 -a")
        try:
            ret = subprocess.check_output(cmd, shell=True)
            self._log.info("{0}".format(ret))
            if "Quartus Prime Programmer was successful. 0 errors, 0 warnings" in str(ret):
                self._log.info("Quartus Programming USB Blaster is Detected In Host Machine")
                return True
        except Exception as ex:
            self._log.error("Errors Quartus USB Blaster Is Not Detected {0}".format(ex))
            return False

    def chip_flash_primary(self, path=None, image_name=None):
        if(self.health_status_check_usbblaster() != True):
            return False
        cpld_image_name = path+"\\"+image_name
        cmd=(self.__cpld_app_path+" -c 1 --mode=JTAG --operation="+"\"p;"+cpld_image_name+"\"")
        try:
            self._log.info("CPLD Primary Frimware Flashing Is In Progress")
            ret=subprocess.check_output(cmd,shell=True)
            self._log.info("output {0}".format(ret))
            if "0 errors" in str(ret):
                self._log.info("CPLD Flashing for Primary Chip is Successful")
                return True
            else:
                self._log.error("Failed To Flash CPLD Primary Chip")
                return False
        except Exception as ex:
            self._log.error("Errors Caught During CPLD Primary firmware Flashing {0}".format(ex))
            raise

    def chip_flash_secondary(self, path=None, image_name=None):
        if (self.health_status_check_usbblaster() != True):
            return False
        cpld_image_name = path + "\\" + image_name
        cmd = (self.__cpld_app_path + " -c 1 --mode=JTAG --operation=" + "\"p;" + cpld_image_name + "\"@2")
        try:
            self._log.info("CPLD  Secondary Frimware Flashing Is In Progress")
            ret = subprocess.check_output(cmd, shell=True)
            self._log.info("output {0}".format(ret))
            if "0 errors" in str(ret):
                self._log.info("CPLD Flashing for Secondary Chip is Successful")
                return True
            else:
                self._log.error("Failed To Flash CPLD Secondary Chip")
                return False
        except Exception as ex:
            self._log.error("Errors Caught During CPLD Secondary firmware Flashing {0}".format(ex))
            raise

    def read_postcode(self):
        self.__cpld_app_path += "\quartus_stp_tcl -t rfat_modified.tcl"
        try:
            self.__cpld_app_path = "cd C:\postcode &&" + self.__cpld_app_path
            output = Popen(self.__cpld_app_path, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
            cmd = output.stdout.read()
            cmd = str(cmd)
            ind = (str(cmd).index("BIOS CODE:"))
            ind1 = (str(cmd).index("FPGA CODE:"))
            psd=[]
            post_code = (cmd[int(ind + 11):int(ind + 13)])
            fpga_code = (cmd[int(ind1 + 11):int(ind1 + 13)])
            psd = post_code,fpga_code
            self._log.debug("Platform FPGA Code {0} Platform BIOS Code {1}".format(psd[0],psd[1]))
            return True,post_code,fpga_code
        except Exception as ex:
            self._log.error("Errors Caught While Reading Postcode {0}".format(ex))
            raise