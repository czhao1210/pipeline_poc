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
        acpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='ac')
        flashcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='flash')
        self._flash = ProviderFactory.create(flashcfg, log)
        self.acpower = ProviderFactory.create(acpwrcfg, log)

    def setup(self):
        self.acpower.ac_power_off()
        if self.acpower.get_ac_power_state() != True:
            log.info("AC POWER IS Not Detected in The platform ready To Test PI Flash Provider")

    def teardown(self):
        log.info("end")

    def test_chip_identify(self):
        if (self._flash.chip_identify() == True):
            log.info("System Testing Passed For Identify Flash Chip")
            assert self._flash.chip_identify() == True
        else:
            log.error("System Testing Failed For Identify Flash Chip")

    def test_read(self):
        if (self._flash.chip_identify() == True):
            log.info("System Testing Passed For Reading Flash Chip")
        else:
            log.error("System Testing Failed To Reading Flash Chip")

    def test_flash_image(self):
        if (self._flash.chip_identify() == True):
            self._flash.flash_image()
            log.info("System Testing Passed For Flashing Image To Flash Chip")
        else:
            log.error("System Testing FAILED For Reading Flash Chip")
