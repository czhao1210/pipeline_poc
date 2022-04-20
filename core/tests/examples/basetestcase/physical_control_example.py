import sys
import time

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.ac_power import AcPowerControlProvider
from dtaf_core.providers.dc_power import DcPowerControlProvider
from dtaf_core.providers.physical_control import PhysicalControlProvider
from dtaf_core.providers.provider_factory import ProviderFactory


class PhysicalControlExample(BaseTestCase):
    """
    Command Reference:
    Run in IPU iDRAC infrastructure:
    python3 physical_control_example.py --cfg_file tests/system/data/system/data/physical_control_example_idrac.xml
    """

    def __init__(self, test_log, arguments, cfg_opts):
        super().__init__(test_log, arguments, cfg_opts)
        self._log = test_log
        suf_config = ConfigurationHelper.get_sut_config(cfg_opts)  # parse the sut configuration from the configuration file
        self._ac_cfg = ConfigurationHelper.get_provider_config(provider_name="ac", sut=suf_config)  # parse AC Provider Configuration
        self._dc_cfg = ConfigurationHelper.get_provider_config(provider_name="dc", sut=suf_config)  # parse DC Provider Configuration
        self._phy_cfg = ConfigurationHelper.get_provider_config(provider_name="physical_control", sut=suf_config)  # parse DC Provider Configuration

    def prepare(self):
        super().prepare()
        self._ac = ProviderFactory.create(cfg_opts=self._ac_cfg, logger=self._log)  # type: AcPowerControlProvider
        self._dc = ProviderFactory.create(cfg_opts=self._dc_cfg, logger=self._log)  # type: DcPowerControlProvider
        self._phy = ProviderFactory.create(cfg_opts=self._phy_cfg, logger=self._log)  # type: PhysicalControlProvider

    def execute(self):
        if not self._ac.get_ac_power_state():
            self._ac.ac_power_on()
        print(self._dc.get_dc_power_state())
        assert self._dc.dc_power_off()
        time.sleep(30)
        assert not self._dc.get_dc_power_state()
        assert self._dc.dc_power_on()
        post_codes = dict()
        for x in range(0, 100):
            ret, code = self._phy.read_postcode()
            if ret:
                print(code)
                if code not in post_codes.keys():
                    post_codes[code] = 0
                else:
                    post_codes[code] += 1
            time.sleep(1)
        assert self._dc.get_dc_power_state()
        for k, v in post_codes.items():
            print(f"code={k},{v}")
        assert len(post_codes.keys()) > 2
        return True

    def cleanup(self, return_status):
        super().cleanup(return_status)
        self._ac.close()
        self._dc.close()


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if PhysicalControlExample.main() else Framework.TEST_RESULT_FAIL)

