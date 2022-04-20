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
from time import sleep
from xml.etree import ElementTree as ET

import pytest

from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.internal.socket_sut_os_provider import SocketSutOsProvider
from dtaf_core.providers.provider_factory import ProviderFactory


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


@pytest.mark.com
@pytest.mark.check
@pytest.mark.soundwave
class TesSutOsSystem(object):
    def setup_class(self):
        tree = ET.ElementTree()
        tree.parse(r'tests/system/data/socket_sut_configuration.xml')
        root = tree.getroot()
        sut_dict = dict(
            platform=dict(
                attrib=dict(type='commercial')
            ),
            silicon=dict()
        )

        # TODO: CHANGE THE IP WHEN DO TESTING
        sut = ConfigurationHelper.filter_sut_config(root, '10.13.168.111', sut_filter=sut_dict)[0]
        acpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='ac')
        comsutoscfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='sut_os')
        ET.dump(comsutoscfg)
        self.acpower = ProviderFactory.create(acpwrcfg, log)
        self.socket_sutos = ProviderFactory.create(comsutoscfg, log)  # type: SocketSutOsProvider

    def setup_method(self):
        self.acpower.ac_power_off(60)
        self.acpower.ac_power_on(60)

    def test_shutdown(self):
        self.socket_sutos.wait_for_os(500)
        self.socket_sutos.shutdown(500)
        sleep(10)
        assert self.socket_sutos.is_alive() != True

    def test_reboot(self):
        self.socket_sutos.wait_for_os(500)
        self.socket_sutos.reboot(500)

    def test_execute(self):
        self.socket_sutos.wait_for_os(500)
        ret = self.socket_sutos.execute("uname -s", 10)
        assert ret.return_code == 0
