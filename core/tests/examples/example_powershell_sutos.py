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
from dtaf_core.providers.sut_os_provider import SutOsProvider
from dtaf_core.providers.provider_factory import ProviderFactory


class PowershellSutOSSystemTest(BaseTestCase):
    """
    Basic test case demonstrating the use of FlashProvider.

    Add the IFWI file you want to use to the working directory as IFWI.bin.
    This example test assumes 32MB flash and
    that the SUT is already powered-on and booted to the OS.
    This is designed to be triggered manually,
    and as such, is not marked as a system test for py test to pick up.
    """

    def __init__(self, test_log, arguments, cfg_opts):
        super(PowershellSutOSSystemTest, self).__init__(test_log, arguments, cfg_opts)

        sut_cfg = ConfigurationHelper.get_sut_config(cfg_opts)
        sutos_cfg = sut_cfg.find("providers/sut_os") #ConfigurationHelper.get_provider_config(sut=sut_cfg, provider_name=r"sutos")
        self._sutos = ProviderFactory.create(sutos_cfg, test_log)  # type: SutOsProvider

    def function_test(self):
        """
        This is the function to verify ac functionality of rsc2
        :return: None
        """
        assert self._sutos.is_alive()
        ret = self._sutos.execute("pwd", timeout=10)
        assert ret.return_code == 0
        lines = ret.stdout.readlines()
        assert len(lines) > 0
        if self._sutos.check_if_path_exists("readme.txt"):
            self._sutos.execute("del readme.txt", timeout=None)
        assert not self._sutos.check_if_path_exists("readme.txt")
        self._sutos.execute_async("echo hello >> readme.txt")
        import time
        time.sleep(5)
        assert self._sutos.check_if_path_exists("readme.txt")
        self._sutos.execute("del readme.txt", timeout=None)
        assert not self._sutos.check_if_path_exists("readme.txt")
        return True

    def execute(self):
        """
        The entry of Test Case.
        :return:
        """
        assert self.function_test()
        return True


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if PowershellSutOSSystemTest.main() else Framework.TEST_RESULT_FAIL)
