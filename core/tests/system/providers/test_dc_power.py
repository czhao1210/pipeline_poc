#!/usr/bin/env python

"""
Python Env: Py2.7 & Py3.8
"""

import time
import pytest

from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.provider_factory import ProviderFactory
from xml.etree import ElementTree as ET
from dtaf_core.providers.internal.soundwave2k_ac_provider import Soundwave2kAcProvider
from dtaf_core.providers.internal.soundwave2k_dc_provider import Soundwave2kDcProvider


class MyError(Exception):
    pass


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
        tree = ET.ElementTree()
        tree.parse(r'tests/system/data/dc_power_configuration.xml')
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
        dcpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='dc')

        self.acpower = ProviderFactory.create(acpwrcfg, log)  # type:Soundwave2kAcProvider
        self.dcpower = ProviderFactory.create(dcpwrcfg, log)  # type:Soundwave2kDcProvider

    def setup_method(self):
        self.acpower.ac_power_off(timeout=10)
        self.acpower.ac_power_on(timeout=10)

    def teardown_method(self):
        time.sleep(10)
        self.acpower.ac_power_off(timeout=60)

    def test_dc_power_on(self):
        self.dcpower.dc_power_on(timeout=60)
        log.info('DC POWER STATE 1 : {}'.format(self.dcpower.get_dc_power_state()))
        assert self.dcpower.get_dc_power_state() == 'S0'

    def test_dc_power_off(self):
        self.dcpower.dc_power_off(timeout=60)
        log.info('DC POWER STATE 22 : {}'.format(self.dcpower.get_dc_power_state()))
        assert self.dcpower.get_dc_power_state() == 'S0'
