import os
import re
import sys
import time

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.internal.ssh_sut_os_provider import SshSutOsProvider
from dtaf_core.providers.provider_factory import ProviderFactory


class SutOsCopyExample(BaseTestCase):
    def __init__(self, test_log, arguments, cfg_opts):
        super().__init__(test_log, arguments, cfg_opts)
        suf_config = ConfigurationHelper.get_sut_config(
            cfg_opts)  # parse the sut configuration from the configuration file
        self._log = test_log  # save the logger object
        self._sut_os_cfg = ConfigurationHelper.get_provider_config(provider_name="sut_os",
                                                                   sut=suf_config)
        self._ac_cfg = ConfigurationHelper.get_provider_config(provider_name="ac",
                                                               sut=suf_config)

    def prepare(self):
        super().prepare()
        self._sut_os_provider = ProviderFactory.create(cfg_opts=self._sut_os_cfg, logger=self._log)
        self._ac_provider = ProviderFactory.create(cfg_opts=self._ac_cfg, logger=self._log)

    def execute(self):
        base_path = os.path.dirname(__file__)
        file_name, extension = os.path.splitext(os.path.split(__file__)[-1])
        new_file_name = f'{file_name}_copy{extension}'
        destination_path = f'/root/{new_file_name}'
        source_path = os.path.join(base_path, f'{file_name}{extension}')
        assert self._ac_provider.ac_power_off()
        assert not self._ac_provider.get_ac_power_state()
        assert self._ac_provider.ac_power_on()
        assert self._ac_provider.get_ac_power_state()
        self._sut_os_provider.wait_for_os(600)
        res = self._sut_os_provider.execute('ip address', 10)
        assert res.stdout.find(self._sut_os_provider._ip) != -1 or res.stdout.find(
            self._sut_os_provider._dhcp_pool_ip) != -1
        self._sut_os_provider.copy_local_file_to_sut(source_path, destination_path)
        assert self._sut_os_provider.check_if_path_exists(destination_path)
        source_path = os.path.join(base_path, new_file_name)
        source_path, destination_path = destination_path, source_path
        self._sut_os_provider.copy_file_from_sut_to_local(source_path, destination_path)
        self._sut_os_provider.execute(f'yes | rm {source_path}', 10)
        assert os.remove(destination_path) is None
        return True

    def cleanup(self, return_status):
        super().cleanup(return_status)
        self._sut_os_provider.close()
        self._ac_provider.close()


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if SutOsCopyExample.main() else Framework.TEST_RESULT_FAIL)
