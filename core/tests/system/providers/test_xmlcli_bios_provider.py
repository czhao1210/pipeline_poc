#!/usr/bin/env python
"""
Python Env: Py2.7 & Py3.8
"""
import sys
from xml.etree import ElementTree as ET

import pytest
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.provider_factory import ProviderFactory


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


@pytest.mark.mehlow
class TestSuites(object):
    def setup_class(self):
        tree = ET.ElementTree()
        if sys.platform == 'win32':
            tree.parse(r'C:\git\dtaf-core\tests\system\data\pi_sample_configuration.xml')
        else:
            tree.parse('/opt/Automation/system_configuration.xml')
        root = tree.getroot()
        sut_dict = dict(
            platform=dict(
                attrib=dict(type='commercial')
            ),
            silicon=dict()
        )
        # TODO: CHANGE THE IP WHILE DOING TESTING
        sut = ConfigurationHelper.filter_sut_config(root, '10.190.179.22', sut_filter=sut_dict)[0]
        xmlcli_cfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='bios')
        self._bios = ProviderFactory.create(xmlcli_cfg, log)

    def test_read_bios_knobs(self):
        # multiple knob read check
        ret = self._bios.read_bios_knobs("WHEA Support", "Load NGN DIMM Management Drivers")
        if (ret[0] == True):
            log.info("System Testing Passed For Read Bios Knob")
            log.info(ret[1])
        else:
            log.error("System Testing FAILED For Read Bios Knob")

        # scenario-2 #multiple reads based on prompt attribute
        ret = self._bios.read_bios_knobs("WHEA Support", "NGN ECC Write Check")
        if (ret[0] == True):
            log.info(ret[1])
            log.info("System Testing Passed scenario-2 For Read Bios Knob Value")
        else:
            log.error("System Testing FAILED scenario-2 For Read Bios Knob Value")

        # scenario-3 #read using name attribute since it's unique reading it from xml file
        ret = self._bios.read_bios_knobs("PcieRootPortL1SubStates_1", "WheaSupportEn", "CoreVoltageOffPrefix_1",
                                         "CoreMaxTurbo_3", hexa=True)
        if (ret[0] == True):
            log.info(ret[1])
            log.info("System Testing Passed scenario-3 For Read Bios Knob Value")
        else:
            log.error("System Testing FAILED scenario-3 For Read Bios Knob Value")

    def test_write_bios_knob_value(self):
        # multiple knob writing
        ret = self._bios.write_bios_knob_value("leakyBktLo", 22, "LeakyBktHiLeakyBktLo", 62000, hexa=True)
        if (ret[0] == True):
            log.info("System Testing Passed For Write Bios value")
            log.info(ret[1])
        else:
            log.error("System Testing FAILED For Write Bios value")

    def test_get_knob_options(self):
        ret = self._bios.get_knob_options("NGN ECC Write Check", "WHEA Support")
        if (ret[0] == True):
            log.info("System Testing Passed For get_knob_options")
            log.info(ret[1])
        else:
            log.error("System Testing FAILED For get_knob_options")

    def test_get_bios_bootorder(self):
        ret = self._bios.get_bios_bootorder()
        if (ret[0] == True):
            log.info("System Testing Passed For Get Bios Boot Order")
            log.info(ret[1])
        else:
            log.error("Ssytem Testing FAILED For Get Bios Boot Order")

    def test_default_bios_settings(self):
        ret = self._bios.default_bios_settings()
        if (ret[0] == True):
            log.info("System Testing Passed For Default Bios Setting")
            log.info(ret[1])
        else:
            log.error("System Testing FAILED For Default Bios Setting")

    def test_set_bios_knobs(self):
        # using prompt attribute and config file
        ret = self._bios.set_bios_knobs("WHEA Support", 0)
        if (ret[0] == True):
            log.info("System Testing Passed For Set Bios Knob")
            log.info(ret[1])
        else:
            log.error("System Testing FAILED For Set Bios Knob")

        # using name attribute
        ret = self._bios.set_bios_knobs("WheaSupportE", "0x1", "PcieRootPortL1SubStates_1", "0x1", overlap=True)
        if (ret[0] == True):
            log.info("System Testing Passed For Set Bios Knob Method-2")
            log.info(ret[1])
        else:
            log.error("System Testing FAILED For Set Bios Knob Method-2")

    def test_set_bios_bootorder(self):
        ret = self._bios.set_bios_bootorder('efi', 0)
        if (ret[0] == True):
            log.info("System Testing Passed For set Bios Boot Order")
            log.info(ret[1])
        else:
            log.error("System Testing FAILED For set Bios Boot Order")

    def test_set_auto_knobpath_knoboptions(self):
        ret = self._bios.set_auto_knobpath_knoboptions(True, "WHEA Support")
        if (ret == True):
            log.info("System Testing Passed For set_auto_knobpath_knoboptions")
            log.info(ret)
        else:
            log.error("System Testing FAILED For set_auto_knobpath_knoboptions")
