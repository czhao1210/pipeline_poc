import sys
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


@pytest.mark.pi
class TestSuites(object):
    def setup_class(self):
        tree = ET.ElementTree()
        if sys.platform == 'win32':
            tree.parse(r'C:\git\dtaf-core\tests\system\data\redfish_sample_configuration.xml')
        else:
            tree.parse('/opt/Automation/redfish_system_configuration.xml')
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
        self.acpower.ac_power_on()
        if self.acpower.get_ac_power_state() != True:
            log.error("AC POWER IS Not Detected in The platform BMC Flashing will not Happen")

    def test_flash_image(self):
        if (self._flash.flash_image(
                r"/home/pi/Downloads/WhitleyOBMC-wht-0.59-0-gbb4e18-83ecb75/WhitleyOBMC-wht-0.59-0-gbb4e18-83ecb75-oob.bin") == True):
            log.info("System Testing Passed For Flashing Image To Flash Chip")
            return True
        else:
            log.error("System Testing FAILED For Flashing BMC Chip")
            raise

    def teardown(self):
        log.info("end")
