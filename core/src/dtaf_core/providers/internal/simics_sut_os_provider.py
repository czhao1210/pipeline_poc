import socket

import fabric
import six
from paramiko.ssh_exception import NoValidConnectionsError, SSHException

from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.drivers.internal.simics_driver import SimicsDriver
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.exceptions import OsCommandException, OsCommandTimeoutException
from dtaf_core.lib.os_lib import OsCommandResult
from dtaf_core.providers.internal.ssh_sut_os_provider import SshSutOsProvider


class SimicsSutOsProvider(SshSutOsProvider):
    def __init__(self, cfg_opts, log):
        super(SimicsSutOsProvider, self).__init__(cfg_opts, log)
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"simics")
        self.__driver = DriverFactory.create(cfg_opts=driver_cfg, logger=self._log)  # type: SimicsDriver
        self.__driver.register(r"simics_sut_os")

    def __enter__(self):
        return super(SimicsSutOsProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(SimicsSutOsProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def _load_config(self):
        self._ip = self._config_model.driver_cfg.host
        self._user = self._config_model.driver_cfg.network_user
        self._retry_cnt = self._config_model.driver_cfg.retry_cnt
        self._port = 22
        self._password = self._config_model.driver_cfg.network_password
        self._dhcp_pool_ip = self._config_model.driver_cfg.dhcp_pool_ip
        self._jump_host = None
        self._jump_user = None
        self._jump_auth = None
        self._server_path = None
        self._enable = None

    def update_port(self, value):
        self._port = value

    def wait_for_os(self, timeout):
        try:
            self.update_port(self._config_model.driver_cfg.os_port)
        except TypeError as ex:
            self.update_port(self._config_model.driver_cfg.extra_attr.get('localhost:-1')['os_port'])
        super().wait_for_os(timeout)
