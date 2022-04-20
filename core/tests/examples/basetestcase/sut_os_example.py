import os
import re
import sys
import time

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.sut_os_provider import SutOsProvider
from dtaf_core.providers.provider_factory import ProviderFactory


class SutOsExample(BaseTestCase):
    def __init__(self, test_log, arguments, cfg_opts):
        super().__init__(test_log, arguments, cfg_opts)
        suf_config = ConfigurationHelper.get_sut_config(
            cfg_opts)  # parse the sut configuration from the configuration file
        self._log = test_log  # save the logger object
        self._sut_os_cfg = ConfigurationHelper.get_provider_config(provider_name="sut_os",
                                                                   sut=suf_config)
        self._ac_cfg = ConfigurationHelper.get_provider_config(provider_name="ac",
                                                               sut=suf_config)

        self._log_cfg = ConfigurationHelper.get_provider_config(sut=suf_config, provider_name="log")

    def prepare(self):
        super().prepare()
        self._sut_os_provider = ProviderFactory.create(cfg_opts=self._sut_os_cfg, logger=self._log) # type: SutOsProvider
        self._ac_provider = ProviderFactory.create(cfg_opts=self._ac_cfg, logger=self._log)
        self._log_provider = ProviderFactory.create(cfg_opts=self._log_cfg, logger=self._log)

    def execute(self):
        import time
        from datetime import datetime
        time.sleep(30)
        assert self._ac_provider.ac_power_off()
        assert not self._ac_provider.get_ac_power_state()
        assert self._ac_provider.ac_power_on()
        assert self._ac_provider.get_ac_power_state()
        __start_os_boot = datetime.now()
        self._sut_os_provider.wait_for_os(1200)
        __start_os_cmd = datetime.now()
        res = self._sut_os_provider.execute('ip address', 10)
        result1 = self._sut_os_provider.execute('python --version', 10)
        result1 = result1.stdout, result1.stderr
        self._log.info(result1)
        result2 = self._sut_os_provider.execute('python3 --version', 10)
        result2 = result2.stdout, result2.stderr
        self._log.info(result2)
        res1 = re.search(r"[Pp]ython\s+\d+\.\d+\.\d+", result1[0]) or re.search(r"[Pp]ython\s+\d+\.\d+\.\d+", result2[0])
        assert res1, 'neither python nor python3 can be found'
        cmd_time = (datetime.now() - __start_os_cmd).seconds
        boot_time = (datetime.now() - __start_os_boot).seconds
        print(f"SUT takes {cmd_time} seconds to execute all these commands, {boot_time} seconds to boot into OS")
        return True

    def cleanup(self, return_status):
        super().cleanup(return_status)
        self._sut_os_provider.close()
        self._ac_provider.close()
        self._log_provider.close()


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if SutOsExample.main() else Framework.TEST_RESULT_FAIL)
