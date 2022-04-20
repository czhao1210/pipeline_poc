import sys

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.ac_power import AcPowerControlProvider
from dtaf_core.providers.flash_provider import FlashProvider
from dtaf_core.providers.provider_factory import ProviderFactory


class BaninoFlashProviderExample(BaseTestCase):
    def __init__(self, test_log, arguments, cfg_opts):
        super(BaninoFlashProviderExample, self).__init__(test_log, arguments, cfg_opts)
        phy_cfg = cfg_opts.find(FlashProvider.DEFAULT_CONFIG_PATH)
        self._flash = ProviderFactory.create(phy_cfg, test_log)
        ac_cfg = cfg_opts.find(AcPowerControlProvider.DEFAULT_CONFIG_PATH)
        self._ac = ProviderFactory.create(ac_cfg, test_log)

    def test_ac_power_off(self):
        ret = self._ac.ac_power_off()
        if (ret == True):
            self._log.info("System Testing Passed For AC Power Off For Detecting Chip")
        else:
            self._log.error("System Testing FAILED For AC Power Off")

    def test_chip_identify(self):
        ret = self._flash.chip_identify()
        if (ret == True):
            self._log.info("System Testing Passed For Identify Flash Chip")
        else:
            self._log.error("System Testing FAILED For Identify Flash Chip")

    def test_read(self):
        ret = self._flash.chip_identify()
        if (ret == True):
            ret = self._flash.read()
            if (ret == True):
                self._log.info("System Testing Passed For Reading Flash Chip")
            else:
                self._log.error("System Testing FAILED For Reading Flash Chip but Detected chip")
        else:
            self._log.error("System Testing FAILED For Reading Flash Chip")

    def test_flash_image(self):
        ret = self._flash.flash_image_bmc()
        if (ret == True):
            self._log.info("System Testing Passed For Flashing BMC Image To Flash Chip")
        else:
            self._log.error("System Testing FAILED For Flashing BMC Image To Flash Chip but Detected Chip")

    def execute(self):
        self.test_flash_image()
        return True


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if BaninoFlashProviderExample.main() else Framework.TEST_RESULT_FAIL)
