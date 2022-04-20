#!/usr/bin/env python

"""
Python Env: Py2.7 & Py3.8
"""

import pytest

from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.provider_factory import ProviderFactory

from xml.etree import ElementTree as ET
from dtaf_core.providers.internal.sf100_flash_provider import Sf100FlashProvider
import time


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


@pytest.mark.soundwave
@pytest.mark.bios
class TestSuites(object):
    def setup_class(self):
        tree = ET.ElementTree()
        tree.parse(r'tests\\system\\data\\flash_sf100_configuration.xml')
        root = tree.getroot()
        obj_configuration = root.find("suts").find("sut").find("providers").find("flash")
        self.pch_name = obj_configuration.find("driver").find("sf100").find("pch").attrib["name"]
        self.pch_chip = obj_configuration.find("driver").find("sf100").find("pch").attrib["chip"]
        self.obj = Sf100FlashProvider(obj_configuration, log)

        # ac configuration
        tree = ET.ElementTree()
        tree.parse(r'tests/system/data/configuration_sample.xml')
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

        self.acpower = ProviderFactory.create(acpwrcfg, log)

    def test_flash_image(self):
        if self.acpower.get_ac_power_state():
            self.acpower.ac_power_off(10)
        time.sleep(10)
        self.obj.flash_image(device_name=self.pch_name,
                             image_path=r"C:\Users\sys_shrasp\Desktop\bios_image\WLYDCRB.86B.BR.64.2019.31.3.04.0439_0012.D09_P80020_LBG_SPS.bin",
                             timeout="600",
                             chip=self.pch_chip
                             )
