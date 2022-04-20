# coding:utf-8
# !/usr/bin/env python

"""
Python Env: Py2.7 & Py3.8
"""
import time
from xml.etree import ElementTree as ET

import pytest

from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.internal.com_bios_bootmenu_provider import ComBiosBootmenuProvider
from dtaf_core.providers.internal.soundwave2k_ac_provider import Soundwave2kAcProvider
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


@pytest.mark.soundwave4
class TestSuites(object):
    def setup_class(self):
        tree = ET.ElementTree()
        tree.parse(r'tests/system/data/bootmenu_configuration.xml')
        root = tree.getroot()

        sut = ConfigurationHelper.find_sut(root, {'ip': '10.13.168.111'})[0]
        acpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='ac')
        self.bootmenucfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='bios_bootmenu')

        self.acpower = ProviderFactory.create(acpwrcfg, log)  # type:Soundwave2kAcProvider
        self.bootmenu = ProviderFactory.create(self.bootmenucfg, log)  # type: ComBiosBootmenuProvider

    def teardown_method(self):
        self.acpower.ac_power_off(timeout=10)
        time.sleep(20)

    def test_bootmenu_random_selection(self):
        self.acpower.ac_power_off(timeout=10)
        time.sleep(20)
        self.acpower.ac_power_on(timeout=10)
        if self.bootmenu.wait_for_entry_menu(timeout=420):
            f7_state = self.bootmenu.press_key(input_key=r'F7')
            if self.bootmenu.wait_for_bios_boot_menu(timeout=10):
                if f7_state:
                    select = r'UEFI Internal Shell'
                    self.bootmenu.select(item_name=select, item_type="DIR_TYPE", timeout=90, use_regex=False)
                    assert self.bootmenu.enter_selected_item(timeout=60, ignore_output=True) == True
                else:
                    log.error('F7 not found !')
                    raise Exception('F7 not found !')
        else:
            raise Exception('F7 not found !')

    def test_bootmenu_press_esc(self):
        self.acpower.ac_power_off(timeout=10)
        time.sleep(20)
        self.acpower.ac_power_on(timeout=10)
        if self.bootmenu.wait_for_entry_menu(timeout=420):
            f7_state = self.bootmenu.press(input_key=r'F7')
            if self.bootmenu.wait_for_bios_boot_menu(timeout=10):
                if f7_state:
                    assert self.bootmenu.get_page_information()
                    assert self.bootmenu.press_key(input_key='ESC') == True
                else:
                    log.error('F7 not found !')
                    raise Exception('F7 not found !')
        else:
            raise Exception('F7 not found !')

    def test_bootmenu_press_key(self):
        self.acpower.ac_power_off(timeout=10)
        time.sleep(20)
        self.acpower.ac_power_on(timeout=10)
        if self.bootmenu.wait_for_entry_menu(timeout=420):
            f7_state = self.bootmenu.press_key(input_key=r'F7')
            if self.bootmenu.wait_for_bios_boot_menu(timeout=10):
                if f7_state:
                    time.sleep(10)
                    ret1 = self.bootmenu.get_selected_item()
                    self.bootmenu.press_key(input_key='DOWN', not_ignore=True, timeout=15)
                    ret2 = self.bootmenu.get_selected_item()
                    self.bootmenu.press_key(input_key='DOWN')
                    ret3 = self.bootmenu.get_selected_item()
                    assert ret1 != ret2
                    assert ret2 != ret3
                else:
                    log.error('F7 not found !')
                    raise Exception('F7 not found !')
        else:
            raise Exception('F7 not found !')
