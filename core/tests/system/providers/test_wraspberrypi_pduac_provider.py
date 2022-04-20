import sys

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.ac_power import AcPowerControlProvider
from dtaf_core.providers.provider_factory import ProviderFactory


class PduRaspberrypiAcProviderExample(BaseTestCase):
    def __init__(self, test_log, arguments, cfg_opts):
        super(PduRaspberrypiAcProviderExample, self).__init__(test_log, arguments, cfg_opts)
        ac_cfg = cfg_opts.find(AcPowerControlProvider.DEFAULT_CONFIG_PATH)
        self._ac = ProviderFactory.create(ac_cfg, test_log)

    def test_ac_power_on(self):
        ret = self._ac.ac_power_on(channel="ch1", timeout=3)
        if (ret == True):
            self._log.info("System Testing Passed For PDU AC Power On")
        else:
            self._log.error("System Testing FAILED For PDU For AC Power On")

    def test_ac_power_off(self):
        ret = self._ac.ac_power_off(channel="ch1")
        if (ret == True):
            self._log.info("System Testing Passed For PDU AC Power Off")
        else:
            self._log.error("Ssytem Testing FAILED For PDU AC Power Off")

    def test_get_ac_power_state(self):
        ret = self._ac.get_ac_power_state(channel="ch1")
        if (ret == True):
            self._log.info("System Testing Passed For Get AC POWER Detection Setting")
        else:
            self._log.error("Didn't Detect AC POWER")

    def test_reset_username_password(self):
        ret = self._ac.reset_username_password(channel="ch1", masterkey="smartrpipdu")
        if (ret == True):
            self._log.info("System Testing Passed For reset_username_password")
        else:
            self._log.error("Ssytem Testing FAILED For reset_username_password")

    def test_set_username_password(self):
        ret = self._ac.set_username_password("admin", "intel@1234", channel="ch1")
        if (ret == True):
            self._log.info("System Testing Passed For set_username_password")
        else:
            self._log.error("Ssytem Testing FAILED For set_username_password")

    def execute(self):
        self.test_reset_username_password()
        self.test_set_username_password()
        self.test_ac_power_off()
        self.test_ac_power_on()
        self.test_get_ac_power_state()

        return True


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if PduRaspberrypiAcProviderExample.main() else Framework.TEST_RESULT_FAIL)
