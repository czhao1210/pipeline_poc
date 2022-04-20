#!/usr/bin/env python
"""
Python Env: Py2.7 & Py3.8
"""
import sys
import pytest
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.provider_factory import ProviderFactory
from xml.etree import ElementTree as ET
import time


class MyError(Exception):
    pass


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
    def setup_class(self):
        tree = ET.ElementTree()
        if sys.platform == 'win32':
            tree.parse(r'tests\system\data\xmlcli_bios_configuration.xml')
        else:
            tree.parse('/opt/Automation/xmlcli_bios_configuration.xml')
        root = tree.getroot()

        sut = ConfigurationHelper.find_sut(root, {'ip': '10.190.179.22'})[0]
        xmlcli_cfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='bios')
        self._bios = ProviderFactory.create(xmlcli_cfg, log)

        acpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='ac')
        dcpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='dc')
        self.acpower = ProviderFactory.create(acpwrcfg, log)
        self.dcpower = ProviderFactory.create(dcpwrcfg, log)

        self.acpower.ac_power_off(10)
        time.sleep(10)
        self.acpower.ac_power_on(10)
        time.sleep(20)
        self.dcpower.dc_power_off(60)
        time.sleep(20)
        self.dcpower.dc_power_on(60)
        time.sleep(400)

    def teardown_class(self):
        self.acpower.ac_power_off(10)

    def test_read_bios_knobs(self):
        ret = self._bios.read_bios_knobs("WHEA Support")
        if (ret[0] == True):
            log.info("System Testing Passed For Read Bios Knob")
            log.info(ret[1])
        else:
            raise Exception("System Testing FAILED For Read Bios Knob")

        ret = self._bios.read_bios_knobs("WHEA Support", "NGN ECC Write Check")
        if (ret[0] == True):
            log.info(ret[1])
            log.info("System Testing Passed scenario-2 For Read Bios Knob Value")
        else:
            raise Exception("System Testing FAILED scenario-2 For Read Bios Knob Value")

        ret = self._bios.read_bios_knobs("PcieRootPortL1SubStates_1", "WheaSupportEn", hexa=True)
        if (ret[0] == True):
            log.info(ret[1])
            log.info("System Testing Passed scenario-3 For Read Bios Knob Value")
        else:
            raise Exception("System Testing FAILED scenario-3 For Read Bios Knob Value")

    def test_write_bios_knob_value(self):
        ret = self._bios.write_bios_knob_value("ShellEntryTime", 6, hexa=True)
        if (ret[0] == True):
            log.info("System Testing Passed For Write Bios value")
            log.info(ret[1])
        else:
            raise Exception("System Testing FAILED For Write Bios value")

    def test_get_knob_options(self):
        ret = self._bios.get_knob_options("WHEA Support")
        if (ret[0] == True):
            log.info("System Testing Passed For get_knob_options")
            log.info(ret[1])
        else:
            raise Exception("System Testing FAILED For get_knob_options")

    def test_get_bios_bootorder(self):
        ret = self._bios.get_bios_bootorder()
        if (ret[0] == True):
            log.info("System Testing Passed For Get Bios Boot Order")
            log.info(ret[1])
        else:
            raise Exception("Ssytem Testing FAILED For Get Bios Boot Order")

    def test_default_bios_settings(self):
        ret = self._bios.default_bios_settings()
        if (ret[0] == True):
            log.info("System Testing Passed For Default Bios Setting")
            log.info(ret[1])
        else:
            raise Exception("System Testing FAILED For Default Bios Setting")

    def test_set_bios_knobs(self):
        ret = self._bios.set_bios_knobs("WHEA Support", 0)
        if (ret[0] == True):
            log.info("System Testing Passed For Set Bios Knob")
            log.info(ret[1])
        else:
            raise Exception("System Testing FAILED For Set Bios Knob")

        ret = self._bios.set_bios_knobs("PcieRootPortL1SubStates_1", "0x1", overlap=True)
        if (ret[0] == True):
            log.info("System Testing Passed For Set Bios Knob Method-2")
            log.info(ret[1])
        else:
            raise Exception("System Testing FAILED For Set Bios Knob Method-2")

    def test_set_bios_bootorder(self):
        ret = self._bios.set_bios_bootorder('efi', 0)
        if (ret[0] == True):
            log.info("System Testing Passed For set Bios Boot Order")
            log.info(ret[1])
        else:
            raise Exception("System Testing FAILED For set Bios Boot Order")

    def test_set_auto_knobpath_knoboptions(self):
        ret = self._bios.set_auto_knobpath_knoboptions(True, "WHEA Support")
        if (ret == True):
            log.info("System Testing Passed For set_auto_knobpath_knoboptions")
            log.info(ret)
        else:
            raise Exception("System Testing FAILED For set_auto_knobpath_knoboptions")
