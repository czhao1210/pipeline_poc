import re
import time
from datetime import datetime

from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.exceptions import TimeoutException, InvalidParameterError
from dtaf_core.providers.console import ConsoleProvider


class BaseConsoleProvider(ConsoleProvider):
    def __init__(self, cfg_opts, log):
        """
        Create a new BmcProvider object.

        :param cfg_opts: xml.etree.ElementTree.Element of configuration options for execution environment
        :param log: Logger object to use for output messages
        """
        super(BaseConsoleProvider, self).__init__(cfg_opts, log)
        self._logger = log
        self.buffer_name = 'bmc_console_buffer'
        self.buffer_size = 4 * 1024 * 1024
        self.bmc_prompt = ':~#'
        if 'com' == self._config_model.driver_cfg.name:
            self.drv_opts = ConfigurationHelper.get_driver_config(provider=cfg_opts, driver_name='com')
        elif 'wsol' == self._config_model.driver_cfg.name:
            self.drv_opts = ConfigurationHelper.get_driver_config(provider=cfg_opts, driver_name='wsol')
        else:
            raise InvalidParameterError('Driver {com, wsol} lost')

        self.serial = DriverFactory.create(self.drv_opts, log)
        self.serial.register(self.buffer_name, self.buffer_size)

    def __enter__(self):
        return super(BaseConsoleProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(BaseConsoleProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def wait_for_login(self, timeout):
        # type: (int) -> None
        """
        Wait for login into bmc within specific timeout.
        """
        start = datetime.now()
        while (datetime.now() - start).seconds < timeout:
            res = self._read_until_time(int(self._config_model.login_time_delay))
            if not res:
                try:
                    self.execute('', 10, end_pattern='login:')
                    return True
                except:
                    try:
                        self.execute('uname -s', 10, end_pattern='Linux')
                        return True
                    except:
                        continue
        else:
            return False

    def _read_until_time(self, timeout):
        if timeout < 0:
            raise InvalidParameterError('Invalid timeout value: {}'.format(timeout))

        data = ''
        start = datetime.now()
        while (datetime.now() - start).seconds < timeout:
            c = self.serial.read_from(self.buffer_name)
            if not c:
                continue
            data += c
        return data

    def login(self):
        try:
            self.execute(self._config_model.user, timeout=10, end_pattern='Password')
            self.execute(self._config_model.password, timeout=10, end_pattern=':~#')
            print('login way one')
            return True
        except:
            self.execute(self._config_model.user, timeout=10, end_pattern='command not found')
            print('login way two')
            return True
        return False

    def exit(self):
        self.execute('exit', timeout=10, end_pattern='logout')

    def in_console(self):
        # type: () -> bool
        """


        :return: True if in console else False
        """
        try:
            self.execute('uname -s', timeout=10, end_pattern='Linux')
            return True
        except:
            return False

    def reboot(self):
        self.execute('shutdown', timeout=0)

    def execute(self, cmd, timeout=0, end_pattern=None):
        # type: (str, int) -> str
        """
        Execute cmd.

        :param cmd: command
        :param timeout: Maximum execution timeout, 0 means no need to wait for output data
        :param end_pattern: search pattern in output of command. if any match, API will return the data received.
        :return: Execution result
        """

        if timeout < 0:
            raise InvalidParameterError('Invalid timeout value: {}'.format(timeout))
        self._log.debug('Execute cmd: {}'.format(cmd))
        self._cleanup_buffer()
        for c in cmd:
            self.serial.write(c)
            time.sleep(0.1)
        self.serial.write('\r')
        if 0 == timeout:
            return ''
        elif end_pattern is None:
            return self._read_output(self.bmc_prompt, timeout)
        else:
            pat = re.compile(end_pattern)
            return self._read_output(pat, timeout)

    def _cleanup_buffer(self):
        """
        cleanup buffer
        :return:
        """
        self.serial.read_from(self.buffer_name)

    def _read_output(self, flag, timeout):
        """
        Read data until flag within timeout seconds.

        :param flag: Compiled python RE object
        :param timeout: Maximum waiting seconds
        :raise InvalidParameterError: If timeout is a negative value
        :raise TimeoutException: If not get flag within specific timeout
        :return: Data string till flag
        """
        if timeout < 0:
            raise InvalidParameterError('Invalid timeout value: {}'.format(timeout))

        data = ''
        start = datetime.now()
        while (datetime.now() - start).seconds < timeout:
            c = self.serial.read_from(self.buffer_name)
            if not c:
                continue
            data += c
            if flag.search(data):
                self._log.debug('Response data: ' + data)
                return data
        else:
            self._log.debug('Response timeout: ' + data)
            raise TimeoutException('Timeout to wait for {} within {}s'.format(flag.pattern, timeout))
