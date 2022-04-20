import sys

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.flash_provider import FlashProvider
from dtaf_core.providers.provider_factory import ProviderFactory


class UsbblasterCpldProviderExample(BaseTestCase):
    def __init__(self, test_log, arguments, cfg_opts):
        super(UsbblasterCpldProviderExample, self).__init__(test_log, arguments, cfg_opts)
        flash_cfg = cfg_opts.find(FlashProvider.DEFAULT_CONFIG_PATH)
        self._flash = ProviderFactory.create(flash_cfg, test_log)

    def test_flash_image(self):
        ret = self._flash.flash_image(target="cpld2")
        if (ret == True):
            self._log.info("System Testing Passed For Flashing Image To Flash Chip")
        else:
            self._log.error("System Testing FAILED For Flashing Image To Flash Chip but Detected Chip")

    def execute(self):
        self.test_flash_image()
        return True


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if UsbblasterCpldProviderExample.main() else Framework.TEST_RESULT_FAIL)
