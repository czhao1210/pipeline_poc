import sys

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.ac_power import AcPowerControlProvider
from dtaf_core.providers.provider_factory import ProviderFactory


class RedfishACProviderExample(BaseTestCase):
    def __init__(self, test_log, arguments, cfg_opts):
        super(RedfishACProviderExample, self).__init__(test_log, arguments, cfg_opts)
        flash_cfg = cfg_opts.find(AcPowerControlProvider.DEFAULT_CONFIG_PATH)
        self._ac = ProviderFactory.create(flash_cfg, test_log)

    def test_ac_power_on(self):
        ret = self._ac.ac_power_on()
        if (ret == True):
            self._log.info("System Testing Passed For REDFISH AC POWER ON")
        else:
            self._log.error("System Testing FAILED For REDFISH AC POWER ON")

    def test_ac_power_off(self):
        ret = self._ac.ac_power_off()
        if (ret == True):
            self._log.info("System Testing Passed For REDFISH AC POWER OFF")
        else:
            self._log.error("System Testing FAILED For REDFISH AC POWER OFF")

    def test_get_ac_power_state(self):
        ret = self._ac.get_ac_power_state()
        if (ret == True):
            self._log.info("AC power is Detected system testing passed")
        else:
            self._log.error("AC power is Not Detected system testing passed")

    def execute(self):
        self.test_ac_power_on()
        self.test_ac_power_off()
        self.test_get_ac_power_state()
        return True


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if RedfishACProviderExample.main() else Framework.TEST_RESULT_FAIL)
