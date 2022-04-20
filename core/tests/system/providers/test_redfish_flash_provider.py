import sys
import time
import os
from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.provider_factory import ProviderFactory
from dtaf_core.providers.flash_provider import FlashProvider
from dtaf_core.lib.configuration import ConfigurationHelper

class RedfishFlashProviderExample(BaseTestCase):
    def __init__(self, test_log, arguments, cfg_opts):
        super(RedfishFlashProviderExample, self).__init__(test_log, arguments, cfg_opts)
        flash_cfg = cfg_opts.find(FlashProvider.DEFAULT_CONFIG_PATH)
        self._flash = ProviderFactory.create(flash_cfg, test_log)

    def test_flash_image(self):
        ret=self._flash.flash_image_bmc()
        if(ret == True):
            self._log.info("System Testing Passed For Flashing Image To Flash Chip")
        else:
            self._log.error("System Testing FAILED For Flashing Image To Flash Chip but Detected Chip")

    def test_current_bmc_version(self):
        ret=self._flash.current_bmc_version_check()
        if(ret[0] == True):
            self._log.info("System Testing Passed For Flashing Image To Flash Chi {0}".format(ret[1]))
        else:
            self._log.error("System Testing FAILED For Flashing Image To Flash Chip but Detected Chip")

    def test_flash_image_bios(self):
        ret=self._flash.flash_image()
        if(ret == True):
            self._log.info("System Testing Passed For Flashing Image To bios Flash Chip")
        else:
            self._log.error("System Testing FAILED For Flashing Image To bios Flash Chip but Detected Chip")

    def test_current_bios_version(self):
        ret=self._flash.current_bios_version_check()
        if(ret[0] == True):
            self._log.info("System Testing Passed For Flashing Image To Flash Chi {0}".format(ret[1]))
        else:
            self._log.error("System Testing FAILED For Flashing Image To Flash Chip but Detected Chip")


    def test_current_cpld_version(self):
        ret=self._flash.current_cpld_version_check()
        if(ret[0] == True):
            self._log.info("System Testing Passed For getting CPLD FRIMWARE Version {0}".format(ret[1]))
        else:
            self._log.error("System Testing FAILED For getting CPLD FRIMWARE Version")

    def test_flash_image_cpld(self):
        ret=self._flash.flash_image(target="cpld")
        if(ret[0] == True):
            self._log.info("System Testing Passed For Flashing CPLD Image")
        else:
            self._log.error("System Testing FAILED For Flashing CPLD Image")

    def execute(self):
        #self.test_flash_image()
        #self.test_current_bmc_version()
        #self.test_flash_image_bios()
        self.test_current_bios_version()
        #self.test_current_cpld_version()
        #self.test_flash_image_cpld()
        return True

if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if RedfishFlashProviderExample.main() else Framework.TEST_RESULT_FAIL)
