#!/usr/bin/env python

"""
Python Env: Py2.7 & Py3.8
"""

import os
import sys
import time
import pytest


cwd = os.path.dirname(__file__)
sys.path.append(cwd)
dtaf_dir = os.path.join(cwd, os.pardir, os.pardir, os.pardir, 'src')
if dtaf_dir not in sys.path:
    sys.path.append(dtaf_dir)


from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.provider_factory import ProviderFactory

from xml.etree import ElementTree as ET


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


class TestUefiShell(object):
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

    def _uefi_check(self, com_cfg, sol_cfg):
        bios = self._provider_create('bios_bootmenu', com_cfg)
        bios.wait_for_entry_menu(600)
        bios.press('F7')
        time.sleep(10)
        bios.select('UEFI Internal Shell', 'DIR_TYPE', 60, False)
        bios.enter_selected_item(10, True)
        time.sleep(3)
        uefi = self._provider_create('uefi_shell', sol_cfg)
        time.sleep(10)
        uefi.execute('\n', 3)
        time.sleep(1)
        assert uefi.in_uefi() is True
        time.sleep(1)
        output = uefi.execute('map -r', 10)
        assert len(output) > 0
        time.sleep(1)
        uefi.exit_uefi()

        bios.select('UEFI Internal Shell', 'DIR_TYPE', 60, False)
        bios.enter_selected_item(10, True)
        uefi.execute('\n', 3)
        time.sleep(1)
        assert uefi.in_uefi() is True
        time.sleep(1)
        uefi.shutdown()

    @pytest.mark.soundwave
    @pytest.mark.com
    @pytest.mark.sol
    def test_uefi_shell_with_sol_driver(self):
        self.sol_cfg = 'sol_soundwave_cfg.xml'
        self.com_cfg = 'com_soundwave_cfg.xml'
        self.ac = self._provider_create('ac', self.com_cfg)
        self._sut_init(self.ac)
        self._uefi_check(self.com_cfg, self.sol_cfg)


if __name__ == '__main__':
    ts_us = TestUefiShell()
    ts_us.test_uefi_shell_with_sol_driver()
    sys.exit(0)
