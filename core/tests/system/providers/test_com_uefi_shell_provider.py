#!/usr/bin/env python

"""
Python Env: Py2.7 & Py3.8
"""

import os
import sys
import time
from xml.etree import ElementTree as ET

import pytest
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.bios_menu import BiosBootMenuProvider
from dtaf_core.providers.provider_factory import ProviderFactory

cwd = os.path.dirname(__file__)
sys.path.append(cwd)
dtaf_dir = os.path.join(cwd, os.pardir, os.pardir, os.pardir, 'src')
if dtaf_dir not in sys.path:
    sys.path.append(dtaf_dir)


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
    def _provider_create(self, provider, xml_cfg):
        tree = ET.ElementTree()
        tree.parse(os.path.join(os.path.dirname(__file__), r'../data/{}'.format(xml_cfg)))

        root = tree.getroot()
        sut_dict = dict(
            platform=dict(
                attrib=dict(type='commercial')
            ),
            silicon=dict()
        )

        sut = ConfigurationHelper.filter_sut_config(root, '10.13.168.111', sut_filter=sut_dict)[0]
        provider_cfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name=provider)
        ET.dump(provider_cfg)

        return ProviderFactory.create(provider_cfg, log)

    def _sut_init(self, ac):
        if ac.get_ac_power_state():
            ac.ac_power_off(600)
            time.sleep(5)
            ac.ac_power_on(600)
        else:
            ac.ac_power_on(600)

    def _uefi_check(self, bios, uefi):
        bios.wait_for_entry_menu(600)
        bios.press('F7')
        time.sleep(0.3)
        bios.press('F7')
        time.sleep(0.3)
        bios.press('F7')
        time.sleep(0.3)
        bios.press('F7')
        time.sleep(0.3)
        bios.press('F7')
        time.sleep(0.3)
        bios.press('F7')
        time.sleep(0.3)
        bios.wait_for_bios_boot_menu(10)
        time.sleep(5)
        bios.select('UEFI Internal Shell', 'DIR_TYPE', 60, False)
        bios.enter_selected_item(10, True)
        uefi.execute('\n', 0)
        time.sleep(1)
        uefi.in_uefi()
        time.sleep(1)
        output = uefi.execute('map -r', 10)
        time.sleep(1)
        uefi.shutdown()

    @pytest.mark.check
    @pytest.mark.soundwave1
    @pytest.mark.com
    def test_uefi_shell_with_com_driver(self):
        self.xml_cfg = 'com_soundwave_cfg.xml'
        self.ac = self._provider_create('ac', self.xml_cfg)
        self.bios = self._provider_create('bios_bootmenu', self.xml_cfg)  # type: BiosBootMenuProvider
        self.uefi = self._provider_create('uefi_shell', self.xml_cfg)
        time.sleep(10)
        self._sut_init(self.ac)
        time.sleep(10)
        self.ac.ac_power_off(10)


if __name__ == '__main__':
    ts_us = TestUefiShell()
    ts_us.test_uefi_shell_with_com_driver()
    sys.exit(0)
