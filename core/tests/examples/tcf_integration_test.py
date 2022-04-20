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
import sys
import time

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.lib.exceptions import OsCommandTimeoutException
from dtaf_core.providers.dc_power import DcPowerControlProvider
from dtaf_core.providers.provider_factory import ProviderFactory
from dtaf_core.providers.sut_os_provider import SutOsProvider


class SutOsProviderExample(BaseTestCase):
    """Basic test case demonstrating the use of SutOsProvider"""

    def __init__(self, test_log, arguments, cfg_opts):
        super(SutOsProviderExample, self).__init__(test_log, arguments, cfg_opts)
        sut_os_cfg = cfg_opts.find(SutOsProvider.DEFAULT_CONFIG_PATH)
        self._os = ProviderFactory.create(sut_os_cfg, test_log)  # type: SutOsProvider
        dc_cfg = cfg_opts.find(DcPowerControlProvider.DEFAULT_CONFIG_PATH)
        self._dc = ProviderFactory.create(dc_cfg, test_log)  # type: DcPowerControlProvider

    def example_os_cmd(self):
        self._log.info("Executing a basic command...")
        result = self._os.execute("ls /usr", 5)
        self._log.info("Files/folders in /usr: {}".format(result.stdout.strip().split("\n")))
        if result.cmd_failed():
            raise RuntimeError("'ls /usr' failed!")

    def example_os_cmd_dir(self):
        test_dir = "/usr/bin"
        self._log.info("Default directory: {}".format(self._os.execute("pwd", 5).stdout.strip()))
        result = self._os.execute("pwd", 5.0, cwd=test_dir).stdout.strip()
        self._log.debug("Received pwd output: {}".format(result))
        if result != test_dir:
            raise RuntimeError("Failed to switch to {}, pwd output: {}".format(test_dir, result))

    def example_async(self):
        self._log.info("Executing a background task...")
        self._os.execute_async("sleep 25")
        result = self._os.execute("ps aux | grep sleep", 5.0).stdout.count("sleep 25") == 2
        if not result:
            raise RuntimeError("Failed to launch background process!")

    def example_reboot(self):
        self._log.debug("Rebooting SUT...")
        self._os.reboot(400.0)

    def example_shutdown(self):
        self._log.debug("Checking if system is reporting as up...")
        assert self._dc.get_dc_power_state()
        assert self._os.is_alive()

        self._log.debug("Turning off system...")
        self._dc.dc_power_off()
        time.sleep(15.0)

        self._log.debug("Checking if system is reporting as off...")
        assert not self._dc.get_dc_power_state()
        assert not self._os.is_alive()

        self._log.debug("Powering system back on...")
        self._dc.dc_power_on()
        self._os.wait_for_os(500)

    def example_timeout(self):
        self._log.debug("Expect command timeout...")
        try:
            self._os.execute("sleep 10", 1)
        except OsCommandTimeoutException:
            self._log.debug("Success! Got a timeout exception.")
        else:
            self._log.error("Fail - no timeout exception received.")
            raise RuntimeError("Fail - no timeout exception received.")

    def execute(self):
        self.example_os_cmd()
        self.example_os_cmd_dir()
        self.example_async()
        self.example_timeout()
        self.example_reboot()
        self.example_shutdown()
        return True


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if SutOsProviderExample.main() else Framework.TEST_RESULT_FAIL)
