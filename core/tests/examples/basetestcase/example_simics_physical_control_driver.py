import sys
from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.provider_factory import ProviderFactory
from dtaf_core.providers.physical_control import PhysicalControlProvider
from dtaf_core.lib.configuration import ConfigurationHelper

class SimicsPhysicalControlProviderExample(BaseTestCase):
    """
    Command Reference:
    python3 example_simics_physical_control_driver.py --cfg_file tests/system/data/example_simics_physical_control.xml
    """
    def __init__(self, test_log, arguments, cfg_opts):
        super().__init__(test_log, arguments, cfg_opts)
        suf_config = ConfigurationHelper.get_sut_config(
            cfg_opts)  # parse the sut configuration from the configuration file
        self._log = test_log  # save the logger object
        self.simics_physical_control_cfg = ConfigurationHelper.get_provider_config(provider_name="physical_control", sut=suf_config)

    def prepare(self):
        super().prepare()
        self.simics_physical_control_provider = ProviderFactory.create(cfg_opts=self.simics_physical_control_cfg, logger=self._log)  # type: PhysicalControlProvider

    def execute(self):
        s3_pin_output = self.simics_physical_control_provider.read_s3_pin(timeout=10)  # Read S3 pin
        assert s3_pin_output
        print("*************************output of s3_pin***************************")
        print(s3_pin_output)
        s4_pin_output = self.simics_physical_control_provider.read_s4_pin(timeout=10)  # Read S3 pin
        assert s4_pin_output
        print("*************************output of s4_pin***************************")
        print(s4_pin_output)
        return True

    def cleanup(self, return_status):
        super().cleanup(return_status)
        self.simics_physical_control_provider.close()


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if SimicsPhysicalControlProviderExample.main() else Framework.TEST_RESULT_FAIL)