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
from dtaf_core.providers.internal.simics_ac_provider import SimicsAcProvider
from dtaf_core.providers.internal.simics_dc_provider import SimicsDcProvider
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



class TestSuites(object):
    def test_ac_on(self):
        tree = ET.ElementTree()
        tree.parse(r'tests/system/data/simics_ac_configuration.xml')
        root = tree.getroot()

        sut = ConfigurationHelper.find_sut(root, {'ip': '10.239.181.138'})[0]
        acpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='ac')
        dcpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='dc')

        acpower = ProviderFactory.create(acpwrcfg, log)  # type:SimicsAcProvider
        dcpower = ProviderFactory.create(dcpwrcfg, log)  # type:SimicsDcProvider

        assert acpower.get_ac_power_state() == False
        acpower.ac_power_on()
        assert acpower.get_ac_power_state()
        ret = False
        retries = 0
        while retries < 6 and  not ret:
            ret = dcpower.get_dc_power_state()
            time.sleep(10)
            retries += 1
        assert ret
        dcpower.dc_power_off()
        assert not dcpower.get_dc_power_state()
        dcpower.dc_power_on()
        assert dcpower.get_dc_power_state()
        acpower.ac_power_off()
        assert not acpower.get_ac_power_state()
        print("PASSED")
TestSuites().test_ac_on()
