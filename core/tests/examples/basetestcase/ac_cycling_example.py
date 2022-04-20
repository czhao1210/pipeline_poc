import sys

from dtaf_core.providers.ac_power import AcPowerControlProvider
from dtaf_core.providers.provider_factory import ProviderFactory

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.dtaf_constants import Framework


class AcCyclingExample(BaseTestCase):
    """
    Command Reference:
    Run in IPU iDRAC infrastructure:
    python3 ac_cycling_example.py --cfg_file tests/system/data/system/data/ac_cycling_example_idrac.xml
    Run /w Soundwave:
    python3 ac_cycling_example.py --cfg_file tests/system/data/system/data/ac_cycling_example.xml
    """

    def __init__(self, test_log, arguments, cfg_opts):
        super().__init__(test_log, arguments, cfg_opts)
        self._log = test_log
        suf_config = ConfigurationHelper.get_sut_config(
            cfg_opts)  # parse the sut configuration from the configuration file
        self._ac_cfg = ConfigurationHelper.get_provider_config(provider_name="ac", sut=suf_config)  # parse AC Provider Configuration

    def prepare(self):
        super().prepare()
        self._ac = ProviderFactory.create(cfg_opts=self._ac_cfg, logger=self._log)  # type: AcPowerControlProvider

    def execute(self):
        if not self._ac.get_ac_power_state():
            assert self._ac.ac_power_on()
        assert self._ac.get_ac_power_state()
        assert self._ac.ac_power_off()
        assert not self._ac.get_ac_power_state()
        assert self._ac.ac_power_on()
        assert self._ac.get_ac_power_state()
        return True

    def cleanup(self, return_status):
        super().cleanup(return_status)
        self._ac.close()


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if AcCyclingExample.main() else Framework.TEST_RESULT_FAIL)
