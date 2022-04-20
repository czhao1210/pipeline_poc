import sys

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.ac_power import AcPowerControlProvider
from dtaf_core.providers.provider_factory import ProviderFactory


class RaspberrypiAcProviderExample(BaseTestCase):
    def __init__(self, test_log, arguments, cfg_opts):
        super(RaspberrypiAcProviderExample, self).__init__(test_log, arguments, cfg_opts)
        ac_cfg = cfg_opts.find(AcPowerControlProvider.DEFAULT_CONFIG_PATH)
        self._ac = ProviderFactory.create(ac_cfg, test_log)

    def test_ac_power_on(self):
        ret = self._ac.ac_power_on()
        if (ret == True):
            self._log.info("System Testing Passed For AC Power On")
        else:
            self._log.error("System Testing FAILED For For AC Power On")

    def test_ac_power_off(self):
        ret = self._ac.ac_power_off()
        if (ret == True):
            self._log.info("System Testing Passed For AC Power Off")
        else:
            self._log.error("Ssytem Testing FAILED For AC Power Off")

    def test_get_ac_power_state(self, output=None):
        ret = self._ac.get_ac_power_state()
        if (ret == output):
            self._log.info("System Testing Passed For Get AC POWER Detection Setting")
        else:
            self._log.error("System Testing FAILED For Get AC POWER Detection Setting")

    def execute(self):
        self.test_ac_power_off()
        self.test_get_ac_power_state(output=None)
        self.test_ac_power_on()
        self.test_get_ac_power_state(output=True)
        return True


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if RaspberrypiAcProviderExample.main() else Framework.TEST_RESULT_FAIL)
