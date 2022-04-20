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
if six.PY2:
    import mock
if six.PY3:
    from unittest import mock

import os
import logging
import unittest
import dtaf_core.lib.log_utils
from argparse import Namespace
from dtaf_core.lib.base_test_case import BaseTestCase


class TestBaseTestCase(unittest.TestCase):
    """Unit tests for BaseTestCase"""

    def setUp(self):
        current_path, _ = os.path.split(__file__)
        self.filename = os.path.join(current_path, 'log.txt')

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    # Logging setup
    logger = logging.getLogger('unittestLogger')
    logger.level = logging.DEBUG
    logging.basicConfig(filename='log.txt')
    test_result_pass = "INFO:unittestLogger:<Test Result: Test Passed>"
    test_result_fail = "ERROR:unittestLogger:<Test Result: Test Failed>"

    @mock.patch.object(BaseTestCase, 'execute', return_value=True)
    @mock.patch.object(BaseTestCase, 'parse_arguments', return_value=Namespace(console_debug=True))
    @mock.patch.object(BaseTestCase, 'parse_config_file', return_value={})
    @mock.patch.object(dtaf_core.lib.log_utils, 'create_logger', return_value=logger)
    def test_btc_pass(self, mock_execute, mock_parse, mock_config, mock_logger):
        # TODO: When Python2 is dropped, the log.txt file can be removed and the below code can be used instead.
        # with self.assertLogs(self.logger, level=logging.INFO) as cm:
        #     self.assertTrue(BaseTestCase.main())
        # self.assertIn(self.test_result_pass, cm.output)

        BaseTestCase.main()
        with open('log.txt', 'r') as f:
            data = [i.strip() for i in f.readlines()]
        self.assertIn(self.test_result_pass, data)

    @mock.patch.object(BaseTestCase, 'execute', return_value=False)
    @mock.patch.object(BaseTestCase, 'parse_arguments', return_value=Namespace(console_debug=True))
    @mock.patch.object(BaseTestCase, 'parse_config_file', return_value={})
    @mock.patch.object(dtaf_core.lib.log_utils, 'create_logger', return_value=logger)
    def test_btc_fail(self, mock_execute, mock_parse, mock_config, mock_logger):
        # TODO: When Python2 is dropped, the log.txt file can be removed and the below code can be used instead.
        # with self.assertLogs(self.logger, level=logging.ERROR) as cm:
        #     self.assertFalse(BaseTestCase.main())
        # self.assertIn(self.test_result_fail, cm.output)

        BaseTestCase.main()
        with open('log.txt', 'r') as f:
            data = [i.strip() for i in f.readlines()]
        self.assertIn(self.test_result_fail, data)

    @mock.patch.object(BaseTestCase, 'prepare', side_effect=RuntimeError)
    @mock.patch.object(BaseTestCase, 'parse_arguments', return_value=Namespace(console_debug=True))
    @mock.patch.object(BaseTestCase, 'parse_config_file', return_value={})
    @mock.patch.object(dtaf_core.lib.log_utils, 'create_logger', return_value=logger)
    def test_btc_prepare_fail(self, mock_prepare, mock_parse, mock_config, mock_logger):
        # TODO: When Python2 is dropped, the log.txt file can be removed and the below code can be used instead.
        # with self.assertLogs(self.logger, level=logging.ERROR) as cm:
        #     self.assertRaises(RuntimeError, BaseTestCase.main)
        # self.assertIn(self.test_result_fail, cm.output)

        self.assertRaises(RuntimeError, BaseTestCase.main)
        with open('log.txt', 'r') as f:
            data = [i.strip() for i in f.readlines()]
        self.assertIn(self.test_result_fail, data)

    @mock.patch.object(BaseTestCase, 'execute', side_effect=RuntimeError)
    @mock.patch.object(BaseTestCase, 'parse_arguments', return_value=Namespace(console_debug=True))
    @mock.patch.object(BaseTestCase, 'parse_config_file', return_value={})
    @mock.patch.object(dtaf_core.lib.log_utils, 'create_logger', return_value=logger)
    def test_btc_execute_exception(self, mock_execute, mock_parse, mock_config, mock_logger):
        # TODO: When Python2 is dropped, the log.txt file can be removed and the below code can be used instead.
        # with self.assertLogs(self.logger, level=logging.ERROR) as cm:
        #     self.assertRaises(RuntimeError, BaseTestCase.main)
        # self.assertIn(self.test_result_fail, cm.output)

        self.assertRaises(RuntimeError, BaseTestCase.main)
        with open('log.txt', 'r') as f:
            data = [i.strip() for i in f.readlines()]
        self.assertIn(self.test_result_fail, data)

    @mock.patch.object(BaseTestCase, 'execute', side_effect=BaseException)
    @mock.patch.object(BaseTestCase, 'parse_arguments', return_value=Namespace(console_debug=True))
    @mock.patch.object(BaseTestCase, 'parse_config_file', return_value={})
    @mock.patch.object(dtaf_core.lib.log_utils, 'create_logger', return_value=logger)
    def test_btc_execute_base_exception(self, mock_execute, mock_parse, mock_config, mock_logger):
        # TODO: When Python2 is dropped, the log.txt file can be removed and the below code can be used instead.
        # with self.assertLogs(self.logger, level=logging.ERROR) as cm:
        #     self.assertRaises(BaseException, BaseTestCase.main)
        # self.assertIn(self.test_result_fail, cm.output)

        self.assertRaises(BaseException, BaseTestCase.main)
        with open('log.txt', 'r') as f:
            data = [i.strip() for i in f.readlines()]
        self.assertIn(self.test_result_fail, data)
