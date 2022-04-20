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

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.lib.exceptions import OsCommandTimeoutException
from dtaf_core.providers.provider_factory import ProviderFactory
from dtaf_core.providers.sut_os_provider import SutOsProvider


class TcfNoSutInteractionExample(BaseTestCase):
    """Basic test case demonstrating the use of SutOsProvider"""

    def __init__(self, test_log, arguments, cfg_opts):
        super(TcfNoSutInteractionExample, self).__init__(test_log, arguments, cfg_opts)
        self._log.info("Hello from DTAF __init__! I can make a provider (I won't use it, though, promise!)")
        sut_os_cfg = cfg_opts.find(SutOsProvider.DEFAULT_CONFIG_PATH)
        self._os = ProviderFactory.create(sut_os_cfg, test_log)  # type: SutOsProvider
    
    def execute(self):
        self._log.info("I'm in execute now. Just going to report True.")
        return True


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if TcfNoSutInteractionExample.main() else Framework.TEST_RESULT_FAIL)
