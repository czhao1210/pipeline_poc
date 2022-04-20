# coding:utf-8
# !/usr/bin/env python

"""
Python Env: Py2.7 & Py3.8
"""
import pytest
import time
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.provider_factory import ProviderFactory
from xml.etree import ElementTree as ET
from dtaf_core.providers.internal.soundwave2k_ac_provider import Soundwave2kAcProvider
from dtaf_core.providers.internal.wsol_bios_bootmenu_provider import WsolBiosBootmenuProvider


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


class TestSuites(object):
    def setup_class(self):
        tree = ET.ElementTree()
        tree.parse(r'tests/system/data/wsol_soundwave_cfg.xml')
        root = tree.getroot()

        sut = ConfigurationHelper.find_sut(root, {'ip': '10.13.168.111'})[0]
        acpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='ac')
        bootmenucfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='bios_bootmenu')

        self.acpower = ProviderFactory.create(acpwrcfg, log) # type:Soundwave2kAcProvider
        self.bootmenu = ProviderFactory.create(bootmenucfg, log)  # type: WsolBiosBootmenuProvider

    def test_bootmenu_press_down(self):
        self.acpower.ac_power_off(timeout=10)
        time.sleep(20)
        self.acpower.ac_power_on(timeout=10)
        if self.bootmenu.wait_for_entry_menu(timeout=300):
            f7_state = self.bootmenu.press(input_key=r'F7')
            self.bootmenu.wait_for_bios_boot_menu(timeout=10)
            if f7_state:
                assert self.bootmenu.press_key(input_key='DOWN') == True
            else:
                log.error('F7 not found !')
                raise Exception('F7 not found !')
        else:
            raise Exception('F7 not found !')
