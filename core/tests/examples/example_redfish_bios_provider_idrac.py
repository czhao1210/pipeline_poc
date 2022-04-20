# coding:utf-8
# !/usr/bin/env python

"""
Python Env: Py2.7 & Py3.8
"""
from xml.etree import ElementTree as ET

import pytest

from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.internal.redfish_bios_provider import RedfishBiosProvider
from dtaf_core.providers.internal.redfish_flash_provider import RedfishFlashProvider
from dtaf_core.providers.provider_factory import ProviderFactory
from dtaf_core.providers.internal.redfish_physical_control_provider import RedfishPhysicalControlProvider


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


@pytest.mark.pi1
class TestSuites(object):
    def setup_class(self):
        tree = ET.ElementTree()
        tree.parse(r'tests/system/data/idrac_system_configuration.xml')
        root = tree.getroot()

        sut = ConfigurationHelper.find_sut(root, {'ip': '10.190.179.183'})[0]
        self.bioscfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='bios')
        self.flashcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='flash')
        self.physical_controlcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='physical_control')

        self.bios = ProviderFactory.create(self.bioscfg, log)  # type: RedfishBiosProvider
        self.flash = ProviderFactory.create(self.flashcfg, log)  # type: RedfishFlashProvider
        self.physical_control = ProviderFactory.create(self.physical_controlcfg,
                                                       log)  # type: RedfishPhysicalControlProvider

    def test_get(self):
        res1 = self.bios.get_bios_category_bootorder()
        print(res1)
        # assert res1 == ['Boot0002', 'Boot0000', 'Boot0001'] or res1 == ['Boot0002', 'Boot0000']
        res2 = self.flash.current_bios_version_check()
        assert res2 == (True, '1.1.3')
        res3 = self.flash.current_bmc_version_check()
        assert res3 == (True, '4.40.20.00')
        res4 = self.flash.current_cpld_version_check()
        assert res4 == (True, '0.4.4')
        res5 = self.physical_control.read_postcode()
        assert res5 == (True, 126)
