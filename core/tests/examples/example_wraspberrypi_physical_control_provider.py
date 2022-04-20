import sys
import time
import os
from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.provider_factory import ProviderFactory
from xml.etree import ElementTree as ET
import unittest
from dtaf_core.providers.physical_control import PhysicalControlProvider
from dtaf_core.lib.configuration import ConfigurationHelper

class PiPhysicalControlProviderExample(BaseTestCase):
    def __init__(self, test_log, arguments, cfg_opts):
        super(PiPhysicalControlProviderExample, self).__init__(test_log, arguments, cfg_opts)
        phy_cfg = cfg_opts.find(PhysicalControlProvider.DEFAULT_CONFIG_PATH)
        self._phy = ProviderFactory.create(phy_cfg, test_log)

    def test_set_clear_cmos(self):
        ret=self._phy.set_clear_cmos()
        if(ret == True):
            self._log.info("System Testing Passed For set_clear_cmos Functionality")
        else:
            self._log.error("System Testing FAILED For set_clear_cmos Functionality")

    def test_connect_usb_to_sut(self):
        ret=self._phy.connect_usb_to_sut()
        if(ret == True):
            self._log.info("System Testing Passed For connect_usb_to_sut")
        else:
            self._log.error("Ssytem Testing FAILED For connect_usb_to_sut")

    def test_connect_usb_to_host(self):
        ret=self._phy.connect_usb_to_host()
        if(ret == True):
            self._log.info("System Testing Passed For connect_usb_to_host")
        else:
            self._log.error("Ssytem Testing FAILED For connect_usb_to_host")

    def test_disconnect_usb(self):
        ret=self._phy.disconnect_usb()
        if(ret == True):
            self._log.info("System Testing Passed For disconnect_usb")
        else:
            self._log.error("Ssytem Testing FAILED For disconnect_usb")

    def test_read_postcode(self):
        ret=self._phy.read_postcode()
        if ret == None:
            self._log.error("Ssytem Testing FAILED For Reading Post Code")
        else:
            self._log.info("System Testing Passed For Reading Platform Post Code ==>"+ret+"<==")

    def test_read_s3_pin(self):
        ret=self._phy.read_s3_pin()
        if(ret == True):
            self._log.info("System Testing Passed For Reading S3 State")
        else:
            self._log.error("System Testing FAILED For Reading S3 State")

    def test_read_s4_pin(self):
        ret=self._phy.read_s4_pin()
        if(ret == True):
            self._log.info("System Testing Passed For Reading S4 State")
        else:
            self._log.error("System Testing FAILED For Reading S4 State")

    def test_program_jumper(self,mode=None):
        if(mode=="set"):
            ret=self._phy.program_jumper(state="set",gpio_pin_number=32,timeout=4)
            if(ret == True):
                self._log.info("System Testing Passed For Set Jumper")
            else:
                self._log.error("System Testing FAILED For Set Jumper")
        else:
            ret=self._phy.program_jumper(state="unset",gpio_pin_number=32,timeout=4)
            if(ret == True):
                self._log.info("System Testing Passed For UnSet Jumper")
            else:
                self._log.error("System Testing FAILED For UnSet Jumper")
            
        
    
    def execute(self):
        self.test_connect_usb_to_sut()
        self.test_connect_usb_to_host()
        self.test_disconnect_usb()
        self.test_read_postcode()
        #self.test_read_s3_pin()
        #self.test_read_s4_pin()
        self.test_program_jumper(mode="set")
        self.test_program_jumper()
        self.test_set_clear_cmos()
        return True

if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if PiPhysicalControlProviderExample.main() else Framework.TEST_RESULT_FAIL)
