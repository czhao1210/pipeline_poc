#!/usr/bin/env python

"""
Python Env: Py2.7 & Py3.8
"""

import os
import sys
import time
import pytest

cwd = os.path.dirname(__file__)
sys.path.append(cwd)
dtaf_dir = os.path.join(cwd, os.pardir, os.pardir, os.pardir, 'src')
if dtaf_dir not in sys.path:
    sys.path.append(dtaf_dir)


from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.provider_factory import ProviderFactory

from xml.etree import ElementTree as ET


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
    def _provider_create(self, provider, xml_cfg):
        tree = ET.ElementTree()
        tree.parse(os.path.join(os.path.dirname(__file__), r'../data/{}'.format(xml_cfg)))

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

    def _sut_init(self, ac):
        ac.ac_power_off(10)
        time.sleep(20)
        ac.ac_power_on(10)

    def _log(self, console):
        if console.runwith_framework == 'caf' and os.environ['CAF_CASE_LOG_PATH']:
            log_file = os.path.join(os.environ['CAF_CASE_LOG_PATH'],
                                    os.path.splitext(os.path.basename(sys.argv[0]))[0]
                                    + '_console.log')
        elif console.logpath_local:
            log_file = os.path.join(self.console.logpath_local,
                                    os.path.splitext(os.path.basename(sys.argv[0]))[0]
                                    + '_console.log')
        else:
            log_file = os.path.join(os.path.dirname(sys.argv[0]).replace('/', os.sep),
                                    'local_logs',
                                    os.path.splitext(os.path.basename(sys.argv[0]))[0]
                                    + '_console.log')
        return open(log_file).read()

    def _inject_check(self, console, inject):
        assert inject in self._log(console)
        assert len(inject) <= len(self._log(console))

    def test_console_log_with_wsol_driver(self):
        self.inject = 'CONSOLE LOG WITH WSOL PORT'
        self.xml_cfg = 'wsol_soundwave_cfg.xml'
        self.console = self._provider_create('console_log', self.xml_cfg)
        self.ac = self._provider_create('ac', self.xml_cfg)
        self.console.inject_line(self.inject)
        self._sut_init(self.ac)
        time.sleep(5)
        self._inject_check(self.console, self.inject)
