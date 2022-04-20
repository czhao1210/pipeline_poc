# coding:utf-8
# !/usr/bin/env python

"""
Python Env: Py2.7 & Py3.8
"""
import pytest
import time
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.provider_factory import ProviderFactory
from dtaf_core.providers.console_log import ConsoleLogProvider
from xml.etree import ElementTree as ET


class _Log(object):
    @classmethod
    def debug(cls, msg):
        print(msg)

    @classmethod
    def info(cls, msg):
        print(msg)

    @classmethod
    def warning(cls, msg):
        print(msg)

    @classmethod
    def error(cls, msg):
        print(msg)

    @classmethod
    def critical(cls, msg):
        print(msg)

    warn = warning
    fatal = critical


log = _Log()


@pytest.mark.soundwave2
class TestSuites(object):
    def setup_class(self):
        tree = ET.ElementTree()
        tree.parse(r'tests/system/data/console_configuration.xml')
        root = tree.getroot()
        sut_dict = dict(
            platform=dict(
                attrib=dict(type='commercial')
            ),
            silicon=dict()
        )

        # TODO: CHANGE THE IP WHEN DO TESTING
        sut = ConfigurationHelper.filter_sut_config(root, '10.13.168.111', sut_filter=sut_dict)[0]

        acpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='ac')
        consolecfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='console')

        self.acpower = ProviderFactory.create(acpwrcfg, log)
        self.console = ProviderFactory.create(consolecfg, log)  # type: ConsoleLogProvider

    def teardown_method(self):
        self.acpower.ac_power_off(10)
        time.sleep(20)

    def test_reboot(self):
        self.acpower.ac_power_off(10)
        time.sleep(20)
        self.acpower.ac_power_on(10)
        if self.console.wait_for_login(365):
            self.console.login()
            assert self.console.in_console()
            res = self.console.execute('uname -s', timeout=10, end_pattern='Linux')
            assert 'Linux' in res
            self.console.reboot()
            if self.console.wait_for_login(365):
                self.console.login()
                assert self.console.in_console()
                self.console.exit()
                assert not self.console.in_console()
            else:
                raise Exception("TIME OUT")
        else:
            raise Exception("TIME OUT")
