# coding:utf-8
# !/usr/bin/env python

"""
Python Env: Py2.7 & Py3.8
"""

import json

import pytest

from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.internal.soundwave2k_ac_provider import Soundwave2kAcProvider
from dtaf_core.providers.provider_factory import ProviderFactory
import time
from dtaf_core.lib.ssh_lib import SSHlib


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


@pytest.mark.soundwave1
class TestSuites(object):

    def setup_class(self):
        with open(r'tests/system/data/ac_json_configuration', 'rt') as f:
            root = json.loads(f.read())
        sut = ConfigurationHelper.find_sut(root, {'ip': '10.13.168.111'})[0]
        acpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='ac')
        self.acpower = ProviderFactory.create(acpwrcfg, log)  # type:Soundwave2kAcProvider
        self.acpower.ac_power_off(timeout=20)
        time.sleep(30)
        self.acpower.ac_power_on(timeout=20)
        time.sleep(400)

        self.ip = '10.239.173.79'
        self.port = 22
        self.username = 'root'
        self.password = 'password'

        self.sshlib_obj = SSHlib(ip=self.ip, port=self.port, username=self.username, password=self.password)

    def test_file(self):
        self.sshlib_obj.upload('tests/system/data/ac_json_configuration', '/root/ac_json_configuration')
        self.sshlib_obj.download('/root/ac_json_configuration', 'tests/system/data/ac_json_configuration_backup')

    def test_directory(self):
        self.sshlib_obj.upload('tests/system/data', '/root/data')
        self.sshlib_obj.download('/root/data', 'tests/system/data_backup')

    def test_close(self):
        self.sshlib_obj.close()
