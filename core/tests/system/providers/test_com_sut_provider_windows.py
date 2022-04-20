#!/usr/bin/env python
#################################################################################
# INTEL CONFIDENTIAL
# Copyright Intel Corporation All Rights Reserved.
#
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material may contain trade secrets and proprietary
# and confidential information of Intel Corporation and its suppliers and
# licensors, and is protected by worldwide copyright and trade secret laws and
# treaty provisions. No part of the Material may be used, copied, reproduced,
# modified, published, uploaded, posted, transmitted, distributed, or disclosed
# in any way without Intel's prior express written permission.
#
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
#################################################################################
import pytest
from time import sleep
from dtaf_core.lib.os_lib import OsCommandResult
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.provider_factory import ProviderFactory
from xml.etree import ElementTree as ET
import time
from dtaf_core.providers.internal.soundwave2k_ac_provider import Soundwave2kAcProvider
from dtaf_core.providers.internal.soundwave2k_dc_provider import Soundwave2kDcProvider
from dtaf_core.providers.internal.com_sut_os_provider import ComSutOsProvider


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


@pytest.mark.soundwave3
class TestSuites(object):
    def setup_class(self):
        tree = ET.ElementTree()
        tree.parse(r'tests/system/data/com_sut_configuration.xml')
        root = tree.getroot()

        sut = ConfigurationHelper.find_sut(root, {'ip': '10.239.181.138'})[0]
        acpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='ac')
        dcpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='dc')
        comsutoscfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='sut_os')

        self.acpower = ProviderFactory.create(acpwrcfg, log)  # type:Soundwave2kAcProvider
        self.dcpower = ProviderFactory.create(dcpwrcfg, log)  # type:Soundwave2kDcProvider
        self.com_sutos = ProviderFactory.create(comsutoscfg, log)  # type: ComSutOsProvider

    def test_shutdown(self):
        self.dcpower.dc_power_off(timeout=60)
        time.sleep(20)
        self.acpower.ac_power_off(timeout=10)
        time.sleep(10)
        self.acpower.ac_power_on(timeout=10)
        time.sleep(20)
        self.com_sutos.wait_for_os(timeout=600)
        time.sleep(5)
        self.com_sutos.shutdown(timeout=300)
        time.sleep(10)
        assert self.com_sutos.is_alive() != True
        time.sleep(10)
        self.dcpower.dc_power_off(timeout=10)
        time.sleep(20)

    def test_reboot(self):
        self.dcpower.dc_power_off(timeout=60)
        time.sleep(20)
        self.dcpower.dc_power_on(timeout=60)
        self.com_sutos.wait_for_os(timeout=600)
        time.sleep(5)
        self.com_sutos.reboot(timeout=500)
        time.sleep(10)
        self.dcpower.dc_power_off(timeout=10)
        time.sleep(20)

    def test_breakpoint_start(self):
        self.dcpower.dc_power_off(timeout=60)
        time.sleep(20)
        self.dcpower.dc_power_on(timeout=60)
        self.com_sutos.wait_for_os(timeout=600)
        time.sleep(5)
        assert self.com_sutos.is_alive()
        ret = self.com_sutos.execute(cmd="dir", timeout=15)  # type: OsCommandResult
        content = ret.stdout
        assert content != ''
        assert ret.return_code == 0
        time.sleep(120)

    def test_breakpoint_end(self):
        assert self.com_sutos.is_alive()
        ret = self.com_sutos.execute(cmd="dir", timeout=15)  # type: OsCommandResult
        content = ret.stdout
        assert content != ''
        assert ret.return_code == 0
        time.sleep(10)
        self.dcpower.dc_power_off(timeout=10)
        time.sleep(20)
