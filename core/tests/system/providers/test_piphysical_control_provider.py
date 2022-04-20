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


@pytest.mark.pi2
class TestSuites(object):
    def setup_class(self):
        tree = ET.ElementTree()
        if sys.platform == 'win32':
            tree.parse(r'tests\system\data\pi_sample_configuration.xml')
        else:
            tree.parse('/opt/Automation/system_configuration.xml')
        root = tree.getroot()
        sut_dict = dict(
            platform=dict(
                attrib=dict(type='commercial')
            ),
            silicon=dict()
        )
        # TODO: CHANGE THE IP WHEN DO TESTING
        sut = ConfigurationHelper.filter_sut_config(root, '10.190.179.22', sut_filter=sut_dict)[0]
        phycfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='physical_control')
        self.physical = ProviderFactory.create(phycfg, log)
        acpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='ac')
        dcpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='dc')
        self.dcpower = ProviderFactory.create(dcpwrcfg, log)
        self.acpower = ProviderFactory.create(acpwrcfg, log)

    def setup(self):
        self.acpower.ac_power_on()
        if self.dcpower.get_dc_power_state() != True:
            self.dcpower.dc_power_on()
            log.info("DC POWER IS Detected in The platform ready To Test Physical Control")

    def teardown(self):
        log.info("end")

    def test_connect_usb_to_sut(self):
        if self.physical.connect_usb_to_sut() == True:
            log.info("USB switched To Platform")
            assert self.physical.connect_usb_to_sut() == True

    def test_connect_usb_to_host(self):
        if self.physical.connect_usb_to_host() == True:
            log.info("USB switched To HOST")
            assert self.physical.connect_usb_to_host() == True

    def test_disconnect_usb(self):
        if self.physical.disconnect_usb() == True:
            log.info("USB switched Disconnected")
            assert self.physical.disconnect_usb() == True

    def test_read_postcode(self):
        ret = self.physical.read_postcode()
        assert self.physical.read_postcode() != None
        log.info("System Testing Passed For Reading Platform Post Code ==>" + str(ret) + "<==")

    def test_set_clear_cmos(self):
        if self.physical.set_clear_cmos() == True:
            log.info("System Testing Passed For set_clear_cmos Functionality")
            assert self.physical.set_clear_cmos() == True

    def test_program_jumper_set(self):
        if self.physical.program_jumper(state="set", gpio_pin_number=32, timeout=4) == True:
            log.info("System Testing Passed For Set Jumper")
            assert self.physical.program_jumper(state="set", gpio_pin_number=32, timeout=4) == True
        else:
            log.error("System Testing FAILED For Set Jumper")

    def test_program_jumper_unset(self):
        if self.physical.program_jumper(state="unset", gpio_pin_number=32, timeout=4) == True:
            log.info("System Testing Passed For UnSet Jumper")
            assert self.physical.program_jumper(state="unset", gpio_pin_number=32, timeout=4) == True
        else:
            log.error("System Testing FAILED For UnSet Jumper")
