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
"""
This is an example of RSC2 implemented AC Power Control Provider
"""

import sys
from xml.etree import ElementTree as eTree

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.provider_factory import ProviderFactory


class DcPowerSystemTest(BaseTestCase):
    """
    Basic test case demonstrating the use of FlashProvider.

    Add the IFWI file you want to use to the working directory as IFWI.bin.
    This example test assumes 32MB flash and
    that the SUT is already powered-on and booted to the OS.
    This is designed to be triggered manually,
    and as such, is not marked as a system test for py test to pick up.
    """

    def __init__(self, test_log, arguments, cfg_opts):
        super(DcPowerSystemTest, self).__init__(test_log, arguments, cfg_opts)

        tree = eTree.ElementTree()
        if sys.platform == 'win32':
            tree.parse(r'tests\system\data\rsc2_configuration.xml')
        else:
            tree.parse('/opt/Automation/rsc2_configuration.xml')
        root = tree.getroot()
        sut = ConfigurationHelper.get_sut_config(root)
        dc_power_cfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name=r"dc")
        self._dc = ProviderFactory.create(dc_power_cfg, test_log)  # type: DcPowerControlProvider

    def verify_rsc2_dc(self):
        """
        This is the function to verify ac functionality of rsc2
        :return: None
        """
        assert self._dc.dc_power_off(30)
        print(self._dc.get_dc_power_state())
        assert self._dc.dc_power_on(30)
        print(self._dc.get_dc_power_state())
        return True

    def execute(self):
        """
        The entry of Test Case.
        :return:
        """
        self.verify_rsc2_dc()
        return False


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if DcPowerSystemTest.main() else Framework.TEST_RESULT_FAIL)
