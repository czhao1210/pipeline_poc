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
import logging
import unittest
import xml.etree.ElementTree
from argparse import Namespace

import six
from dtaf_core.lib.dtaf_constants import OperatingSystems
from dtaf_core.lib.flash import FlashDevices
from dtaf_core.providers.internal.em100_flash_provider import Em100FlashProvider

if six.PY2:
    import mock
else:
    from unittest import mock


class TestEm100FlashProvider(unittest.TestCase):
    """Unit tests for Em100FlashEmulatorProvider"""

    mock_xml = xml.etree.ElementTree.fromstring("<mock />")

    mock_config_one_pch = Namespace(
        chip_config={
            FlashDevices.PCH: ("chip_type", ["1"])
        }, cli_path="mock_dir\\")

    def setUp(self):
        super(TestEm100FlashProvider, self).setUp()
        self.mock_platform = mock.patch("platform.system", return_value=OperatingSystems.WINDOWS)
        self.mock_platform.start()

    def tearDown(self):
        self.mock_platform.stop()

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_pch))
    def test_stop_is_blocked(self, mock_pcf):
        fp = Em100FlashProvider(self.mock_xml, logging.getLogger())
        self.assertIsNotNone(fp)
        self.assertEqual(1, mock_pcf.call_count)
        with self.assertRaises(NotImplementedError):
            fp.stop(FlashDevices.PCH)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_pch))
    def test_start_is_blocked(self, mock_pcf):
        fp = Em100FlashProvider(self.mock_xml, logging.getLogger())
        self.assertIsNotNone(fp)
        self.assertEqual(1, mock_pcf.call_count)
        with self.assertRaises(NotImplementedError):
            fp.start(FlashDevices.PCH)


if __name__ == "__main__":
    unittest.main()
