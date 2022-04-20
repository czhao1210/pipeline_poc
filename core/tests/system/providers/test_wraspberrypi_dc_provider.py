import sys

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.dc_power import DcPowerControlProvider
from dtaf_core.providers.provider_factory import ProviderFactory


class RaspberrypiDcProviderExample(BaseTestCase):
    def __init__(self, test_log, arguments, cfg_opts):
        super(RaspberrypiDcProviderExample, self).__init__(test_log, arguments, cfg_opts)
        dc_cfg = cfg_opts.find(DcPowerControlProvider.DEFAULT_CONFIG_PATH)
        self._dc = ProviderFactory.create(dc_cfg, test_log)

    def test_dc_power_on(self):
        ret = self._dc.dc_power_on()
        if (ret == True):
            self._log.info("System Testing Passed For DC Power On")
        else:
            self._log.error("System Testing FAILED For For DC Power On")

    def test_dc_power_off(self):
        ret = self._dc.dc_power_off()
        if (ret == True):
            self._log.info("System Testing Passed For DC Power Off")
        else:
            self._log.error("Ssytem Testing FAILED For DC Power Off")

    def test_get_dc_power_state(self, output=None):
        ret = self._dc.get_dc_power_state()
        if (ret == output):
            self._log.info("System Testing Passed For Get DC POWER Detection Setting")
        else:
            self._log.error("System Testing FAILED For Get DC POWER Detection Setting")

    def execute(self):
        self.test_dc_power_off()
        self.test_get_dc_power_state(output=None)
        self.test_dc_power_on()
        self.test_get_dc_power_state(output=True)
        return True


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if RaspberrypiDcProviderExample.main() else Framework.TEST_RESULT_FAIL)
