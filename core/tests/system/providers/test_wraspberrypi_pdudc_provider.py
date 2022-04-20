import sys

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.ac_power import AcPowerControlProvider
from dtaf_core.providers.dc_power import DcPowerControlProvider
from dtaf_core.providers.provider_factory import ProviderFactory


class PduRaspberrypiDcProviderExample(BaseTestCase):
    def __init__(self, test_log, arguments, cfg_opts):
        super(PduRaspberrypiDcProviderExample, self).__init__(test_log, arguments, cfg_opts)
        ac_cfg = cfg_opts.find(AcPowerControlProvider.DEFAULT_CONFIG_PATH)
        self._ac = ProviderFactory.create(ac_cfg, test_log)
        dc_cfg = cfg_opts.find(DcPowerControlProvider.DEFAULT_CONFIG_PATH)
        self._dc = ProviderFactory.create(dc_cfg, test_log)

    def test_ac_power_on(self):
        ret = self._ac.ac_power_on(channel="ch1", timeout=3)
        if (ret == True):
            self._log.info("System Testing Passed For PDU AC Power On")
        else:
            self._log.error("System Testing FAILED For PDU For AC Power On")

    def test_get_ac_power_state(self):
        ret = self._ac.get_ac_power_state(channel="ch1")
        if (ret == True):
            self._log.info("System Testing Passed For Get AC POWER Detection Setting")
        else:
            self._log.error("Didn't Detect AC POWER")

    def test_dc_power_off(self):
        ret = self._dc.dc_power_off(channel="ch1")
        if (ret == True):
            self._log.info("System Testing Passed For PDU DC Power Off")
        else:
            self._log.error("Ssytem Testing FAILED For PDU DC Power Off")

    def test_dc_power_on(self):
        ret = self._dc.dc_power_on(channel="ch1", timeout=3)
        if (ret == True):
            self._log.info("System Testing Passed For PDU DC Power On")
        else:
            self._log.error("System Testing FAILED For PDU For DC Power On")

    def test_get_dc_power_state(self, output=None):
        ret = self._dc.get_dc_power_state()
        if (ret == output):
            self._log.info("System Testing Passed For Get DC PDU POWER Detection")
        else:
            self._log.error("System Testing FAILED For Get DC PDU POWER Detection")

    def execute(self):
        self.test_ac_power_on()
        self.test_get_ac_power_state()
        self.test_dc_power_off()
        self.test_get_dc_power_state(output=None)
        self.test_dc_power_on()
        self.test_get_dc_power_state(output=True)
        return True


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if PduRaspberrypiAcProviderExample.main() else Framework.TEST_RESULT_FAIL)
