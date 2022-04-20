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

class RedfishPhysicalControlProviderExample(BaseTestCase):
    def __init__(self, test_log, arguments, cfg_opts):
        super(RedfishPhysicalControlProviderExample, self).__init__(test_log, arguments, cfg_opts)
        phy_cfg = cfg_opts.find(PhysicalControlProvider.DEFAULT_CONFIG_PATH)
        self._phy = ProviderFactory.create(phy_cfg, test_log)

    def test_get_platform_volt(self):
        ret= self._phy.get_platform_volt()
        if (ret[0] == True):
            self._log.info("System Testing Passed For Read Volt {}".format(ret[1]))
        else:
            self._log.error("System Testing FAILED For UnSet Jumper")

    def test_get_platform_postcode(self):
        ret = self._phy.read_postcode()
        if (ret[0] == True):
            self._log.info("System Testing Passed For Read postcode {0}".format(ret[1]))
        else:
            self._log.error("System Testing FAILED For reading postcode")

    def test_get_system_details(self):
        ret = self._phy.get_system_id()
        if (ret[0] == True):
            self._log.info("System Testing Passed For get Platform Details {0}".format(ret[1]))
        else:
            self._log.error("System Testing FAILED For get Platform Details via redfish bmc")

    def test_system_status_led(self):
        ret = self._phy.platform_health_status()
        if (ret[0] == True):
            self._log.info("System Testing Passed For get {0} Platform LED Status".format(ret[1]))
        else:
            self._log.error("System Testing FAILED For get Platform Details via redfish bmc")

    def test_sx_state_detection(self):
        ret = self._phy.get_power_state()
        print(ret)

    def test_virtual_media_mount(self,image, username, password):
        ret = self._phy.connect_usb_to_sut(image=image,username=username, password=password )
        if (ret == True):
            self._log.info("System Testing Passed For Virtual Media Mount")
        else:
            self._log.error("System Testing FAILED For Virtual Media Mount")

    def test_virtual_media_unmount(self):
        ret = self._phy.disconnect_usb()
        if (ret == True):
            self._log.info("System Testing Passed For Virtual Media unMount")
        else:
            self._log.error("System Testing FAILED For Virtual Media unMount")

    def test_bmc_mac(self):
        ret=self._phy.get_bmc_mac()
        if(ret[0] == True):
            self._log.info("System Testing Passed For Getting BMC MAC")
        else:
            self._log.error("System Testing FAILED to get BMC MAC")

    def execute(self):
        # self.test_get_platform_volt()
        #self.test_get_platform_postcode()
        # self.test_get_system_details()
        #self.test_system_status_led()
        #self.test_sx_state_detection()
        #self.test_virtual_media_mount(image="https://ubit-artifactory-ba.intel.com/artifactory/dcg-dea-srvplat-local/Automation_Tools/SPR/RHEL8-4_v2.iso",username="sys_degsi1",password="czhfi20$")
        #self.test_virtual_media_unmount()
        self.test_bmc_mac()
        return True


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if RedfishPhysicalControlProviderExample.main() else Framework.TEST_RESULT_FAIL)
