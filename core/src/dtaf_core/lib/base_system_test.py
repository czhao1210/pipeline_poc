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
import six
import logging
import platform
import unittest

from xml.etree import ElementTree
from dtaf_core.lib.dtaf_constants import Framework

if six.PY2:  # Python library contextlib2 contains a back-port of the Python 3 ExitStack class for Python 2.
    from contextlib2 import ExitStack
else:  # Python 3 has ExitStack built in to the standard contextlib module.
    from contextlib import ExitStack


class BaseSystemTest(unittest.TestCase):
    """Base class for live system tests. To use, override CLASS_UNDER_TEST with the driver or provider to test."""

    CLASS_UNDER_TEST = None

    @classmethod
    def setUpClass(cls):
        super(BaseSystemTest, cls).setUpClass()

        # Get config file
        exec_os = platform.system()
        try:
            cfg_file = Framework.CFG_FILE_PATH[exec_os]
        except KeyError:
            print("Error - execution OS " + str(exec_os) + " not supported!")
            raise RuntimeError("Error - execution OS " + str(exec_os) + " not supported!")
        else:
            cfg_opts = ElementTree.parse(cfg_file).getroot()
            cls.class_config = cfg_opts.find(cls.CLASS_UNDER_TEST.DEFAULT_CONFIG_PATH)

    def setUp(self):
        with ExitStack() as stack:
            log = logging.getLogger()  # TODO: Change to LogProvider
            self.obj = stack.enter_context(self.CLASS_UNDER_TEST(self.class_config, log))
            self.addCleanup(stack.pop_all().close)


if __name__ == "__main__":
    unittest.main()
