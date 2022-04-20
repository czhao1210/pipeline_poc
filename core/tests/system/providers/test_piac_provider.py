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


@pytest.mark.pi1
class TestSuites(object):
    def setup_class(self):
        tree = ET.ElementTree()
        if sys.platform == 'win32':
            tree.parse(r'tests/system/data/piac_provider_configuration.xml')
        else:
            tree.parse('/opt/Automation/system_configuration.xml')
        root = tree.getroot()
        sut_dict = dict(
            platform=dict(
                attrib=dict(type='commercial')
            ),
            silicon=dict()
        )
        sut = ConfigurationHelper.filter_sut_config(root, '10.190.179.22', sut_filter=sut_dict)[0]
        acpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='ac')
        dcpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='dc')
        self.acpower = ProviderFactory.create(acpwrcfg, log)
        self.dcpower = ProviderFactory.create(dcpwrcfg, log)

    def setup(self):
        self.acpower.ac_power_on()

    def teardown(self):
        log.info('end')

    def test_ac_power_on(self):
        if self.acpower.get_ac_power_state() == True:
            log.info("AC POWER IS Detected in The platform")
            self.acpower.ac_power_off()
            log.info('AC POWER STATE 2 : {}'.format(self.acpower.get_ac_power_state()))
            self.acpower.ac_power_on()
            log.info('AC POWER STATE 3 : {}'.format(self.acpower.get_ac_power_state()))
        elif self.acpower.get_ac_power_state() != True:
            log.info("AC POWER IS NOT Detected")
            self.acpower.ac_power_on()
            log.info('AC POWER STATE 5 : {}'.format(self.acpower.get_ac_power_state()))
        else:
            raise MyError('Unexpected results !')

    def test_ac_power_off(self):
        if self.acpower.get_ac_power_state() == True:
            log.info('AC POWER STATE 11 : {}'.format(self.acpower.get_ac_power_state()))
            self.acpower.ac_power_off()
            log.info('AC POWER STATE 22 : {}'.format(self.acpower.get_ac_power_state()))
            assert self.acpower.get_ac_power_state() == None
        elif self.acpower.get_ac_power_state() != True:
            log.info('AC POWER STATE 44 : {}'.format(self.acpower.get_ac_power_state()))
            self.acpower.ac_power_on()
            log.info('AC POWER STATE 55 : {}'.format(self.acpower.get_ac_power_state()))
            log.info('AC POWER STATE 66 : {}'.format(self.acpower.get_ac_power_state()))
            self.acpower.ac_power_off()
            log.info('AC POWER STATE 77 : {}'.format(self.acpower.get_ac_power_state()))
        else:
            raise MyError('Unexpected results !')
