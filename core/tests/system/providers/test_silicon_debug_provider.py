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
import platform
import os

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.lib.silicon import CPUID
from dtaf_core.providers.provider_factory import ProviderFactory
from dtaf_core.providers.silicon_debug_provider import SiliconDebugProvider
from dtaf_core.lib.dtaf_constants import OperatingSystems


class TestSiliconDebugProvider(BaseTestCase):
    """Basic test case demonstrating the use of SutOsProvider"""

    def __init__(self, test_log, arguments, cfg_opts):
        super(TestSiliconDebugProvider, self).__init__(test_log, arguments, cfg_opts)
        si_dbg_cfg = cfg_opts.find(SiliconDebugProvider.DEFAULT_CONFIG_PATH)
        self._sdp = ProviderFactory.create(si_dbg_cfg, test_log)  # type: SiliconDebugProvider

    def test_start_log_and_stop_log(self):
        self._log.info("Executing start_log and stop_log...")
        exec_os = platform.system()
        if OperatingSystems.WINDOWS in exec_os:
            log_file_name = r"c:\temp\log_sdp_halt.log"
        elif OperatingSystems.LINUX in exec_os:
            log_file_name = r"/tmp/log_sdp_halt.log"
        else:
            self._log.info("The xdp provider is not supported on os '{}'..".format(exec_os))

        self._sdp.start_log(log_file_name)
        # halt and go commands to write debug commands to log file name
        self._sdp.halt()
        self._sdp.go()
        self._sdp.stop_log()

        # assert log file is created and size is >0
        assert os.path.isfile(log_file_name) == True
        assert os.path.getsize(log_file_name) > 0

    def test_cpuid(self):
        self._log.info("Executing CPUID[0] with and without squash...")
        self._sdp.halt()
        result_no_squash = self._sdp.cpuid(CPUID.EAX, 0)
        result_squash = self._sdp.cpuid(CPUID.EAX, 0, squash=True)
        self._log.info("CPUID no-squash result: {}".format(map(hex, result_no_squash)))
        self._log.info("CPUID squash result: {}".format(hex(result_squash)))
        assert type(result_no_squash) == list
        assert type(result_squash) == int
        self._sdp.go()

    def test_msr(self):
        self._log.info("Reading MSR 0x13a with and without squash...")
        self._sdp.halt()
        result_no_squash = self._sdp.msr_read(0x13a)
        result_squash = self._sdp.msr_read(0x13a, squash=True)
        self._log.info("MSR no-squash result: {}".format(map(hex, result_no_squash)))
        self._log.info("MSR squash result: {}".format(hex(result_squash)))
        self._sdp.go()

        self._log.info("Writing MSR 0x6...")
        self._sdp.halt()
        self._sdp.msr_write(0x6, 0x41)
        self._sdp.go()
        time.sleep(0.1)
        self._sdp.halt()
        read_back = self._sdp.msr_read(0x6, squash=True)
        self._log.debug("MSR post-write readback result: {}".format(hex(read_back)))
        self._sdp.go()
        assert read_back == 0x41

    def test_mem(self):
        self._log.info("Reading memory address 0x1000")
        self._sdp.halt()
        self._log.info("Result: {}".format(hex(self._sdp.mem_read("0x1000p", 8))))
        self._log.info("Writing 0xdeadbeef to address 0x1000")
        self._sdp.mem_write("0x1000p", 8, 0xdeadbeef)
        self._sdp.go()
        time.sleep(0.1)
        self._sdp.halt()
        read_back = self._sdp.mem_read("0x1000p", 8)
        self._log.debug("Read back: {}".format(hex(read_back)))
        self._sdp.go()
        assert read_back == 0xdeadbeef

    def execute(self):
        self.test_start_log_and_stop_log()
        self.test_cpuid()
        self.test_msr()
        self.test_mem()
        self._sdp.halt()  # Tests that system is automatically resumed after leaving the test context
        return True


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if TestSiliconDebugProvider.main() else Framework.TEST_RESULT_FAIL)
