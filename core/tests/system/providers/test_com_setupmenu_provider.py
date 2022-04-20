# coding:utf-8
# !/usr/bin/env python

"""
Python Env: Py2.7 & Py3.8
"""
import time
from xml.etree import ElementTree as ET

import pytest
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.internal.com_bios_setupmenu_provider import ComBiosSetupmenuProvider
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
        tree.parse(r'tests/system/data/setupmenu_configuration.xml')
        root = tree.getroot()

        sut = ConfigurationHelper.find_sut(root, {'ip': '10.13.168.111'})[0]
        acpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='ac')
        self.setupmenucfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='bios_setupmenu')

        self.acpower = ProviderFactory.create(acpwrcfg, log)  # type:Soundwave2kAcProvider
        self.setupmenu = ProviderFactory.create(self.setupmenucfg, log)  # type:ComBiosSetupmenuProvider

    def teardown_method(self):
        self.acpower.ac_power_off(timeout=10)
        time.sleep(30)

    def test_setupmenu_Boot_Timeout(self):
        self.acpower.ac_power_off(timeout=10)
        time.sleep(30)
        self.acpower.ac_power_on(timeout=10)
        time.sleep(10)

        kw = [r"Boot Maintenance Manager", r"Set Time Out Value", r"Auto Boot Time-out",
              r"Commit Changes and Exit"]

        if self.setupmenu.wait_for_entry_menu(360):
            time.sleep(0.1)
            f2_state = self.setupmenu.press(input_key=r'F2')

            if f2_state:
                if self.setupmenu.wait_for_bios_setup_menu(timeout=60) == r'SUCCESS':
                    log.debug('******* Enter setup menu   select {}*******'.format(kw[0]))
                    self.setupmenu.select(item_name=kw[0], item_type="DIR_TYPE", use_regex=True, timeout=240)
                    log.debug('Select finshing')
                    self.setupmenu.enter_selected_item(ignore=False, timeout=10)
                    self.setupmenu.select(item_name=kw[1], item_type="DIR_TYPE", use_regex=True, timeout=240)
                    self.setupmenu.enter_selected_item(ignore=False, timeout=10)
                    self.setupmenu.select(item_name=kw[2], item_type="DIR_TYPE", use_regex=True, timeout=240)
                    data = self.setupmenu.get_selected_item().result_value[-1]
                    if not data:
                        return
                    log.debug('Data is : {} s.'.format(data))
                    log.debug('Data type is : {} s.'.format(type(data)))
                    timeout = int('{}'.format(list(data)[1]))
                    log.debug('Default Timeout is : {} s.'.format(timeout))
                    self.setupmenu.enter_selected_item(ignore=False, timeout=10)
                    self.setupmenu.input_text("{}".format(timeout))
                    log.debug('Modify Timeout is : {} s.'.format(timeout))
                    self.setupmenu.select(item_name=kw[3], item_type="DIR_TYPE", use_regex=True, timeout=240)
                    self.setupmenu.enter_selected_item(ignore=False, timeout=10)
                    self.acpower.ac_power_off(timeout=60)
                    time.sleep(10)
                    self.acpower.ac_power_on(timeout=60)
                    if self.setupmenu.wait_for_entry_menu(timeout=360):
                        time.sleep(0.1)
                        f2_state = self.setupmenu.press(input_key=r'F2')
                        if f2_state:
                            if self.setupmenu.wait_for_bios_setup_menu(timeout=60) == r'SUCCESS':
                                log.debug('******* Enter setup menu   select {}*******'.format(kw[0]))
                                self.setupmenu.select(item_name=kw[0], item_type=None, use_regex=True, timeout=240)
                                log.debug('Select finshing')
                                if self.setupmenu.enter_selected_item(ignore=False, timeout=10) == r'SUCCESS':
                                    self.setupmenu.select(item_name=kw[1], item_type="DIR_TYPE", use_regex=True,
                                                          timeout=240)
                                    self.setupmenu.enter_selected_item(ignore=False, timeout=10)
                                    self.setupmenu.select(item_name=kw[2], item_type="DIR_TYPE", use_regex=True,
                                                          timeout=240)
                                    data_new = self.setupmenu.get_selected_item().result_value[-1]
                                    timeout_new = int('{}'.format(list(data_new)[1]))
                                    assert int(timeout) == int(timeout_new)
                else:
                    raise Exception('wait_for_bios_setup_menu failed !')
            else:
                raise Exception('F2 not found !')
        else:
            raise Exception('F2 not found !')

    def test_setupmenu_Boot_Maintenance_Manager(self):
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
                    select = r"Boot Maintenance Manager"
                    log.debug('******* Enter setup menu   select {}*******'.format(select))
                    self.setupmenu.select(item_name=select, item_type=None, use_regex=True, timeout=240)
                    log.debug('Press key')
                    log.debug('Select finshing')
                    self.setupmenu.enter_selected_item(ignore=False, timeout=10)
                else:
                    raise Exception('wait_for_bios_setup_menu failed !')
            else:
                log.error('F2 not found !')
                raise Exception('F2 not found !')
        else:
            raise Exception('F2 not found !')

    def test_setupmenu_get_selected_item(self):
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
                    select = r"BOOT Manager Menu"
                    log.debug('******* Enter setup menu   select {}*******'.format(select))
                    self.setupmenu.select(item_name=select, item_type=None, use_regex=True, timeout=240)
                    log.debug('Select finshing')
                    assert self.setupmenu.get_selected_item().return_code == r'SUCCESS'
                else:
                    raise ('wait_for_bios_setup_menu failed !')
            else:
                log.error('F2 not found !')
                raise Exception('F2 not found !')
        else:
            raise Exception('F2 not found !')

    def test_setupmenu_reboot(self):
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
                    assert self.setupmenu.get_page_information()
                    assert self.setupmenu.scan_current_page_items()
                    self.setupmenu.reboot(timeout=240)
                else:
                    raise Exception('wait_for_bios_setup_menu failed !')
            else:
                log.error('F2 not found !')
                raise Exception('F2 not found !')
        else:
            raise Exception('F2 not found !')

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
                    self.setupmenu.enter_selected_item(ignore=False, timeout=10)
                    self.setupmenu.enter_selected_item(ignore=False, timeout=10)
                    self.setupmenu.select(item_name='Change Boot Order', item_type=None, use_regex=True, timeout=240)
                    self.setupmenu.enter_selected_item(ignore=False, timeout=10)
                    self.setupmenu.change_order(order_list=['Boot Device List'])
