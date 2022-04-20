import json
import sys
import time
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


@pytest.mark.soundwave2
class TestSuites(object):
    def setup_class(self):
        tree = ET.ElementTree()
        if sys.platform == 'win32':
            tree.parse(r'tests\system\data\redfish_sample_configuration.xml')
        else:
            tree.parse('/opt/Automation/ipmi_system_configuration.xml')
        root = tree.getroot()
        sut_dict = dict(
            platform=dict(
                attrib=dict(type='commercial')
            ),
            silicon=dict()
        )
        sut = ConfigurationHelper.filter_sut_config(root, '10.190.179.22', sut_filter=sut_dict)[0]
        dcpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='dc')
        self.dcpower = ProviderFactory.create(dcpwrcfg, log)

        with open(r'tests/system/data/ac_json_configuration', 'rt') as f:
            root = json.loads(f.read())
        sut = ConfigurationHelper.find_sut(root, {'ip': '10.13.168.111'})[0]
        acpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='ac')
        self.acpower = ProviderFactory.create(acpwrcfg, log)

    def test_dc_power_on(self):
        self.acpower.ac_power_off(10)
        time.sleep(30)
        self.acpower.ac_power_on(10)
        time.sleep(300)
        if self.dcpower.get_dc_power_state() == True:
            time.sleep(10)
            log.info("DC POWER IS Detected in The platform")
            self.dcpower.dc_power_off()
            time.sleep(10)
            log.info('DC POWER STATE 2 : {}'.format(self.dcpower.get_dc_power_state()))
            time.sleep(10)
            self.dcpower.dc_power_on()
            time.sleep(10)
            log.info('DC POWER STATE 3 : {}'.format(self.dcpower.get_dc_power_state()))
        elif self.dcpower.get_dc_power_state() != True:
            time.sleep(10)
            log.info("DC POWER IS NOT Detected")
            if self.dcpower.dc_power_on() == True:
                time.sleep(10)
                log.info('DC POWER STATE 5 : {}'.format(self.dcpower.get_dc_power_state()))
                time.sleep(10)
                assert self.dcpower.get_dc_power_state() == True
            else:
                raise MyError('DC power on failed for verification!')
        else:
            raise MyError('Unexpected results !')

    def test_dc_power_reset(self):
        time.sleep(10)
        if self.dcpower.get_dc_power_state() == True:
            time.sleep(10)
            log.info('DC POWER STATE 11 : {}'.format(self.dcpower.get_dc_power_state()))
            time.sleep(10)
            self.dcpower.dc_power_reset()
            time.sleep(10)
            log.info('DC POWER STATE 22 : {}'.format(self.dcpower.get_dc_power_state()))
            time.sleep(10)
            assert self.dcpower.get_dc_power_state() == True
        elif self.dcpower.get_dc_power_state() != True:
            time.sleep(10)
            log.info('DC POWER STATE 33 : {}'.format(self.dcpower.get_dc_power_state()))
            time.sleep(10)
            self.dcpower.dc_power_on()
            time.sleep(10)
            log.info('DC POWER STATE 44 : {}'.format(self.dcpower.get_dc_power_state()))
            time.sleep(10)
            if self.dcpower.get_dc_power_state() == True:
                time.sleep(10)
                assert self.dcpower.dc_power_reset() == True
            else:
                raise MyError('DC power open failed !')
        else:
            raise MyError('Unexpected results !')
