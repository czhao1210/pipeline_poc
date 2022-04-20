import sys

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.physical_control import PhysicalControlProvider
from dtaf_core.providers.provider_factory import ProviderFactory


class UsbblasterPhysicalControlProviderExample(BaseTestCase):
    def __init__(self, test_log, arguments, cfg_opts):
        super(UsbblasterPhysicalControlProviderExample, self).__init__(test_log, arguments, cfg_opts)
        phy_cfg = cfg_opts.find(PhysicalControlProvider.DEFAULT_CONFIG_PATH)
        self._phy = ProviderFactory.create(phy_cfg, test_log)

    def test_read_postcode(self):
        ret = self._phy.read_postcode()
        if ret[0] == None:
            self._log.error("Ssytem Testing FAILED For Reading Post Code")
        else:
            self._log.info("System Testing Passed For Reading Platform Post Code ==>" + ret[1] + "<==")

    def execute(self):
        self.test_read_postcode()
        return True


if __name__ == "__main__":
    sys.exit(
        Framework.TEST_RESULT_PASS if UsbblasterPhysicalControlProviderExample.main() else Framework.TEST_RESULT_FAIL)
