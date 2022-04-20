# coding:utf-8
# !/usr/bin/env python

"""
Python Env: Py2.7 & Py3.8
"""
import time
from xml.etree import ElementTree as ET

import pytest

from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.provider_factory import ProviderFactory


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

    def test_find_by_attribute(self):
        tree = ET.ElementTree()
        tree.parse(r'tests/system/data/configuration_helper.xml')
        root = tree.getroot()

        sut = ConfigurationHelper.find_sut(root, dict(id='testsut'))[0]

        acpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='ac', attrib=dict(id='testprovidera'))
        acpower = ProviderFactory.create(acpwrcfg, log)
        assert acpower

    def test_find_by_noattribute(self):
        tree = ET.ElementTree()
        tree.parse(r'tests/system/data/configuration_helper.xml')
        root = tree.getroot()
        sut_list = ConfigurationHelper.find_sut(root)
        ac_list = list()
        for sut in sut_list:
            acpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='ac',
                                                               attrib=dict(id='testproviderb'))
            acpower = ProviderFactory.create(acpwrcfg, log)
            assert acpower
            ac_list.append(acpower)

    def test_find_by_attributes(self):
        tree = ET.ElementTree()
        tree.parse(r'tests/system/data/configuration_helper.xml')
        root = tree.getroot()
        sut = ConfigurationHelper.find_sut(root, dict(ip='10.13.168.111', id='testsut'))[0]
        acpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='ac',
                                                           attrib=dict(id='testprovidera'))
        acpower = ProviderFactory.create(acpwrcfg, log)
        assert acpower
