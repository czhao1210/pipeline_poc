import sys
import time
import os
from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.provider_factory import ProviderFactory
from xml.etree import ElementTree as ET
import unittest
from dtaf_core.providers.bios_provider import BiosProvider
from dtaf_core.lib.configuration import ConfigurationHelper

class XmlCliProviderExample(BaseTestCase):
    def __init__(self, test_log, arguments, cfg_opts):
        super(XmlCliProviderExample, self).__init__(test_log, arguments, cfg_opts)
        xmlcli_cfg = cfg_opts.find(BiosProvider.DEFAULT_CONFIG_PATH)
        self._bios = ProviderFactory.create(xmlcli_cfg, test_log)

    def test_read_bios_knobs(self):
        '''
        #scenario-1 #read using prompt attribute //if more repetative prompt so use name attribute
        ret=self._bios.read_bios_knobs("WHEA Support","NGN ECC Write Check")
        if(ret[0] == True):
            self._log.info(ret[1])
            self._log.info("System Testing Passed scenario-1 For Read Bios Knob Value")
        else:
            self._log.error("System Testing FAILED scenario-1 For Read Bios Knob Value")
        '''
        #scenario-2 #read using name attribute since it's unique reading it from xml file
        ret=self._bios.read_bios_knobs("PcieRootPortL1SubStates_1","WheaSupportEn","CoreVoltageOffPrefix_1","CoreMaxTurbo_3",hexa=True)
        if(ret[0] == True):
            self._log.info(ret[1])
            self._log.info("System Testing Passed scenario-2 For Read Bios Knob Value")
        else:
            self._log.error("System Testing FAILED scenario-2 For Read Bios Knob Value")
        
    def test_get_knob_options(self):
        ret=self._bios.get_knob_options("NGN ECC Write Check","WHEA Support")
        if(ret[0] == True):
            self._log.info("System Testing Passed For get_knob_options")
            self._log.info(ret[1])
        else:
            self._log.error("System Testing FAILED For get_knob_options")

    def test_get_bios_bootorder(self):
        ret=self._bios.get_bios_bootorder()
        if(ret[0] == True):
            self._log.info("System Testing Passed For Get Bios Boot Order")
            self._log.info(ret[1])
        else:
            self._log.error("Ssytem Testing FAILED For Get Bios Boot Order")

    def test_default_bios_settings(self):
        ret=self._bios.default_bios_settings()
        if(ret[0] == True):
            self._log.info("System Testing Passed For Default Bios Setting")
            self._log.info(ret[1])
        else:
            self._log.error("System Testing FAILED For Default Bios Setting")

    def test_set_bios_knobs(self):
        #using prompt attribute and config file
        '''
        ret=self._bios.set_bios_knobs("WHEA Support",0)
        if(ret[0] == True):
            self._log.info("System Testing Passed For Set Bios Knob")
            self._log.info(ret[1])
        else:
            self._log.error("System Testing FAILED For Set Bios Knob")
        '''
        #using name attribute
        ret=self._bios.set_bios_knobs("ScrambleEn","0x0",overlap=True)
        if(ret[0] == True):
            self._log.info("System Testing Passed For Set Bios Knob Method-2")
            self._log.info(ret[1])
        else:
            self._log.error("System Testing FAILED For Set Bios Knob Method-2")

    def test_set_bios_bootorder(self):
        '''
        #using config file method
        ret=self._bios.set_bios_bootorder('efi',0)
        if(ret[0] == True):
            self._log.info("System Testing Passed For set Bios Boot Order")
            self._log.info(ret[1])
        else:
            self._log.error("System Testing FAILED For set Bios Boot Order")
        '''
        #using direct parameter method to set, bootorder make sure you pass extact name of hard-disk or pendrive
        ret=self._bios.set_bios_bootorder('UEFI Internal Shell')
        if(ret[0] == True):
            self._log.info("System Testing Passed For set Bios Boot Order")
            self._log.info(ret[1])
        else:
            self._log.error("System Testing FAILED For set Bios Boot Order")
         
    def test_write_bios_knob_value(self):
        #scenarios-1 #if muliple prompt no options use name attribute
        ret=self._bios.write_bios_knob_value("leakyBktLo",22,hexa=True)
        if(ret[0] == True):
            self._log.info("System Testing Passed For Write Bios value")
            self._log.info(ret[1])
        else:
            self._log.error("System Testing FAILED For Write Bios value")
        
    def test_set_auto_knobpath_knoboptions(self):
        ret=self._bios.set_auto_knobpath_knoboptions(True,"HardwarePM Interrupt")
        if(ret == True):
            self._log.info("System Testing Passed For set_auto_knobpath_knoboptions")
            self._log.info(ret)
        else:
            self._log.error("System Testing FAILED For set_auto_knobpath_knoboptions")

    def test_execute(self):
        ret=self._bios.execute("ifconfig",60)
        if(ret == True):
            self._log.info("output came")
            self._log.info(ret)
        else:
            self._log.error("Output didn't come")

    def test_flashing_image_xmlcli(self):
        ret=self._bios.flash_ifwi_image(r"/opt/APP/image//","53.2.02.1244.bin")
        if(ret == True):
            self._log.info("flashing logic worked fine")
        else:
            self._log.error("flashing logic failed")

    def test_xmlcli_path_setting(self):
        ret = self._bios.path_setter()
        print(ret)

    def execute(self):
        # self.test_read_bios_knobs()
        # self.test_write_bios_knob_value()
        #self.test_get_knob_options()
        # self.test_get_bios_bootorder()
        self.test_default_bios_settings()
        # self.test_set_bios_knobs()
        # self.test_set_bios_bootorder()
        return True

if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if XmlCliProviderExample.main() else Framework.TEST_RESULT_FAIL)
