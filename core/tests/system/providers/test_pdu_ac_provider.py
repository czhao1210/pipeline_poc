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
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.provider_factory import ProviderFactory
from xml.etree import ElementTree as ET
import time
from dtaf_core.providers.internal.pdu_ac_provider import PduAcProvider
from dtaf_core.providers.internal.soundwave2k_dc_provider import Soundwave2kDcProvider


class Log:
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


LOG = Log()


@pytest.mark.soundwave3
class TestSuites(object):
    def setup_class(self):
        tree = ET.ElementTree()
        tree.parse(r'tests/system/data/pdu_sample_configuration.xml')
        root = tree.getroot()
        sut_dict = dict(
            platform=dict(
                attrib=dict(type='commercial')
            ),
            silicon=dict()
        )

        sut = ConfigurationHelper.filter_sut_config(root, '10.13.168.111', sut_filter=sut_dict)[0]
        pducfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='ac')
        dcpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='dc')

        self.pdu = ProviderFactory.create(pducfg, LOG)  # type:PduAcProvider
        self.dcpower = ProviderFactory.create(dcpwrcfg, LOG)  # type:Soundwave2kDcProvider

    def test_pdu_ac_off(self):
        self.dcpower.dc_power_off(timeout=10)
        time.sleep(10)
        assert self.pdu.ac_power_off(timeout=10) == True

    def test_pdu_ac_on(self):
        assert self.pdu.ac_power_on(timeout=10) == True

    def test_pdu_ac_state(self):
        self.pdu.ac_power_off(timeout=10)
        assert self.pdu.get_ac_power_state(timeout=10) == False
        self.pdu.ac_power_on(timeout=10)
        assert self.pdu.get_ac_power_state(timeout=10) == True
        time.sleep(360)
        self.dcpower.dc_power_off(timeout=10)
