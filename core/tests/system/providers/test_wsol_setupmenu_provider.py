# coding:utf-8
# !/usr/bin/env python

"""
Python Env: Py2.7 & Py3.8
"""
import time
from xml.etree import ElementTree as ET

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


class TestSuites(object):
    def setup_class(self):
        tree = ET.ElementTree()
        tree.parse(r'tests/system/data/wsol_soundwave_cfg.xml')
        root = tree.getroot()

        sut = ConfigurationHelper.find_sut(root, {'ip': '10.13.168.111'})[0]
        acpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='ac')
        bootmenucfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='bios_setupmenu')

        self.acpower = ProviderFactory.create(acpwrcfg, log)  # type:Soundwave2kAcProvider
        self.setupmenu = ProviderFactory.create(bootmenucfg, log)  # type: WsolBiosSetupmenuProvider

    def test_setupmenu_Change_Order(self):
        self.acpower.ac_power_off(timeout=10)
        time.sleep(30)
        self.acpower.ac_power_on(timeout=10)
        time.sleep(10)
        if self.setupmenu.wait_for_entry_menu(timeout=360):
            log.debug('******* Press F2  *******')
            time.sleep(0.1)
            f2_state = self.setupmenu.press(input_key=r'F2')
            if f2_state:
                if self.setupmenu.wait_for_bios_setup_menu(timeout=60) == r'SUCCESS':
                    self.setupmenu.select(item_name=r"Boot Maintenance Manager", item_type=None, use_regex=True,
                                          timeout=240)
                    self.setupmenu.enter_selected_item(ignore=True, timeout=10)
                    self.setupmenu.enter_selected_item(ignore=True, timeout=10)
                    self.setupmenu.select(item_name='Change Boot Order', item_type=None, use_regex=True, timeout=240)
                    self.setupmenu.enter_selected_item(ignore=True, timeout=10)
                    self.setupmenu.change_order(order_list=['Boot Device List'])
