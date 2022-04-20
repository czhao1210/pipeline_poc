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
This is an example of Log Provider.
Command to run:
python <python script> --cfg_file <configuration xml file>
e.g.
python log_example.py --cfg_file tests/system/data/log_example.xml
"""
import sys
from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.dc_power import DcPowerControlProvider
from dtaf_core.providers.provider_factory import ProviderFactory
from dtaf_core.providers.log import LogProvider


class TestLogExample(BaseTestCase):
    def prepare(self):
        super().prepare()

    def __init__(self, test_log, arguments, cfg_opts):
        super().__init__(test_log, arguments, cfg_opts)
        sut_cfg = ConfigurationHelper.get_sut_config(root=cfg_opts)
        self._test_log = test_log
        self._log_cfg = ConfigurationHelper.get_provider_config(sut=sut_cfg, provider_name="log")
        self._dc_cfg = ConfigurationHelper.get_provider_config(sut=sut_cfg, provider_name="dc")

    def execute(self):
        for i in range(0, 2):
            with ProviderFactory.create(cfg_opts=self._log_cfg, logger=self._test_log) as l: # type: LogProvider
                with ProviderFactory.create(cfg_opts=self._dc_cfg, logger=self._test_log) as d: # type: DcPowerControlProvider
                    # import os
                    # if os.path.exists("console{}.log".format(i)):
                    #     os.remove("console{}.log".format(i))
                    # l.redirect("console{}.log".format(i))
                    assert d.dc_power_reset()
                    import time
                    time.sleep(180)
                    pass
        return True

    def cleanup(self, return_status):
        super().cleanup(return_status)


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if TestLogExample.main() else Framework.TEST_RESULT_FAIL)