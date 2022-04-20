#!/usr/bin/env python

"""
Python Env: Py2.7 & Py3.8
"""

import json

import pytest
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.provider_factory import ProviderFactory
from dtaf_core.providers.internal.soundwave2k_ac_provider import Soundwave2kAcProvider


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


@pytest.mark.soundwave5
class TestSuites(object):
    def setup_class(self):
        with open(r'tests/system/data/ac_json_configuration', 'rt') as f:
            root = json.loads(f.read())
        sut = ConfigurationHelper.find_sut(root, {'ip': '10.13.168.111'})[0]

        acpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='ac')

        self.acpower = ProviderFactory.create(acpwrcfg, log)  # type:Soundwave2kAcProvider

    def test_ac_power_on(self):
        if self.acpower.get_ac_power_state():
            log.info('AC POWER STATE 1 : {}'.format(self.acpower.get_ac_power_state()))

            self.acpower.ac_power_off(timeout=6)
            log.info('AC POWER STATE 2 : {}'.format(self.acpower.get_ac_power_state()))
            if self.acpower.get_ac_power_state():
                raise MyError('ac power shutdown failed !')
            self.acpower.ac_power_on(timeout=6)
            log.info('AC POWER STATE 3 : {}'.format(self.acpower.get_ac_power_state()))

            assert self.acpower.get_ac_power_state()

        elif not self.acpower.get_ac_power_state():
            log.info('AC POWER STATE 4 : {}'.format(self.acpower.get_ac_power_state()))

            self.acpower.ac_power_on(timeout=6)
            log.info('AC POWER STATE 5 : {}'.format(self.acpower.get_ac_power_state()))

            assert self.acpower.get_ac_power_state()

        elif self.acpower.get_ac_power_state() == 'Unknown':
            log.info('AC POWER STATE 6 : {}'.format(self.acpower.get_ac_power_state()))
            raise MyError('Unknown status')
        else:
            raise MyError('Unexpected results !')

    def test_ac_power_off(self):
        if self.acpower.get_ac_power_state():

            self.acpower.ac_power_off(timeout=6)
            log.info('AC POWER STATE 11 : {}'.format(self.acpower.get_ac_power_state()))

            assert self.acpower.get_ac_power_state() == False

        elif not self.acpower.get_ac_power_state():
            log.info('AC POWER STATE 22 : {}'.format(self.acpower.get_ac_power_state()))
            self.acpower.ac_power_on(timeout=6)
            log.info('AC POWER STATE 33 : {}'.format(self.acpower.get_ac_power_state()))
            if not self.acpower.get_ac_power_state():
                raise MyError('ac power open failed !')
            self.acpower.ac_power_off(timeout=6)
            assert not self.acpower.get_ac_power_state()

        elif not self.acpower.get_ac_power_state():
            log.info('AC POWER STATE 44 : {}'.format(self.acpower.get_ac_power_state()))
            raise MyError('Unknown status')
        else:
            raise MyError('Unexpected results !')
