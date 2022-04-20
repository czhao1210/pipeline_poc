import sys

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.flash_provider import FlashProvider
from dtaf_core.providers.provider_factory import ProviderFactory


class BmcFlashProviderExample(BaseTestCase):
    def __init__(self, test_log, arguments, cfg_opts):
        super(BmcFlashProviderExample, self).__init__(test_log, arguments, cfg_opts)
        flash_cfg = cfg_opts.find(FlashProvider.DEFAULT_CONFIG_PATH)
        self._flash = ProviderFactory.create(flash_cfg, test_log)



    def test_flash_image(self):

        ret = self._flash.flash_image(r"C:\bmc\WhitleyOBMC-wht-0.59-0-gbb4e18-83ecb75\WhitleyOBMC-wht-0.59-0-gbb4e18-83ecb75-oob.bin")
        if (ret == True):
            self._log.info("System Testing Passed For Flashing Image To Flash Chip")
        else:
            self._log.error("System Testing FAILED For Flashing Image To Flash Chip but Detected Chip")


    def execute(self):
        self.test_flash_image()
        return True


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if BmcFlashProviderExample.main() else Framework.TEST_RESULT_FAIL)
