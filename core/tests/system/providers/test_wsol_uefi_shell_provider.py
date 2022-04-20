#!/usr/bin/env python

"""
Python Env: Py2.7 & Py3.8
"""

import os
import time
from xml.etree import ElementTree as ET

from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.provider_factory import ProviderFactory
import pytest


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


def provider_create(provider):
    tree = ET.ElementTree()
    tree.parse(os.path.join(os.path.dirname(__file__), r'../data/{}'.format('wsol_soundwave_cfg.xml')))

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


# @pytest.mark.soundwave5
class TestSuites:
    def test_map(self):
        ac = provider_create('ac')
        bios = provider_create('bios_bootmenu')
        uefi = provider_create('uefi_shell')

        ac.ac_power_off(10)
        time.sleep(20)
        ac.ac_power_on(10)

        if bios.wait_for_entry_menu(420):
            for i in range(10):
                bios.press('F7')
                time.sleep(0.3)
            if bios.wait_for_bios_boot_menu(10):
                bios.select('UEFI Internal Shell', 'DIR_TYPE', 60, False)
                bios.enter_selected_item(10, True)
                uefi.execute('\n', 0)
                uefi.in_uefi()
                ac.ac_power_off(10)
        else:
            raise Exception('F7 not found !')
