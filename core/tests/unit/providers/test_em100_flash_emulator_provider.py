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
import subprocess
import unittest
import xml.etree.ElementTree
from argparse import Namespace
from os import urandom

import six
from dtaf_core.lib.dtaf_constants import OperatingSystems
from dtaf_core.lib.exceptions import FlashEmulatorException, FlashProgrammerException
from dtaf_core.lib.flash import FlashDevices
from dtaf_core.providers.internal.em100_flash_emulator_provider import Em100FlashEmulatorProvider

if six.PY2:
    import mock
else:
    from unittest import mock

# Horrible hack to bypass the multi-chip per device disable check for unit testing
# TODO: Remove once multi-chip is tested on real HW
Em100FlashEmulatorProvider._disable_multi_chip = lambda x, y: None


class TestEm100FlashEmulatorProvider(unittest.TestCase):
    """Unit tests for Em100FlashEmulatorProvider"""

    mock_xml = xml.etree.ElementTree.fromstring("<mock />")

    mock_config_one_pch = Namespace(
        chip_config={
            FlashDevices.PCH: ("chip_type", ["1"])
        }, cli_path="mock_dir\\")
    mock_config_multi_pch = Namespace(
        chip_config={
            FlashDevices.PCH: ("chip_type", ["1", "2", "3"])
        }, cli_path="mock_dir\\")
    mock_config_one_bmc = Namespace(
        chip_config={
            FlashDevices.BMC: ("chip_type", ["2"])
        }, cli_path="mock_dir\\")
    mock_config_multi_bmc = Namespace(
        chip_config={
            FlashDevices.BMC: ("chip_type", ["1", "2"])
        }, cli_path="mock_dir\\")
    mock_config_single_both = Namespace(
        chip_config={
            FlashDevices.PCH: ("chip_type", ["1"]),
            FlashDevices.BMC: ("chip_type", ["4"])
        }, cli_path="mock_dir\\"
    )
    mock_config_multi_both = Namespace(
        chip_config={
            FlashDevices.PCH: ("chip_type", ["1", "2", "3", "4"]),
            FlashDevices.BMC: ("chip_type", ["5", "6", "7", "8"])
        }, cli_path="mock_dir\\"
    )

    def setUp(self):
        super(TestEm100FlashEmulatorProvider, self).setUp()
        self.mock_platform = mock.patch("platform.system", return_value=OperatingSystems.WINDOWS)
        self.mock_platform.start()

    def tearDown(self):
        self.mock_platform.stop()

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_pch))
    def test_construction_one_pch(self, mock_pcf):
        test_obj = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())
        self.assertIsNotNone(test_obj)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_pch))
    def test_construction_multi_pch(self, mock_pcf):
        test_obj = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())
        self.assertIsNotNone(test_obj)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_bmc))
    def test_construction_one_bmc(self, mock_pcf):
        test_obj = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())
        self.assertIsNotNone(test_obj)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_bmc))
    def test_construction_multi_bmc(self, mock_pcf):
        test_obj = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())
        self.assertIsNotNone(test_obj)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_single_both))
    def test_construction_one_both(self, mock_pcf):
        test_obj = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())
        self.assertIsNotNone(test_obj)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_both))
    def test_construction_multi_both(self, mock_pcf):
        test_obj = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())
        self.assertIsNotNone(test_obj)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_pch))
    def test_pch_no_bmc(self, mock_pcf):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        with mock.patch('subprocess.check_output') as mock_func:
            with self.assertRaises(KeyError):
                fp.start(FlashDevices.BMC)
            self.assertEqual(0, mock_func.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_bmc))
    def test_bmc_no_pch(self, mock_pcf):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        with mock.patch('subprocess.check_output') as mock_func:
            with self.assertRaises(KeyError):
                fp.start(FlashDevices.PCH)
            self.assertEqual(0, mock_func.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_bmc))
    def test_multi_start(self, mock_pcf):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        with mock.patch('subprocess.check_output') as mock_func:
            fp.start(FlashDevices.BMC)
            self.assertEqual(2, mock_func.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_bmc))
    def test_multi_start_fail(self, mock_pcf):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        with mock.patch('subprocess.check_output',
                        side_effect=[True, subprocess.CalledProcessError(1, "mock")]) as mock_func:
            with self.assertRaises(FlashEmulatorException):
                fp.start(FlashDevices.BMC)
            self.assertEqual(2, mock_func.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_bmc))
    def test_multi_stop(self, mock_pcf):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        with mock.patch('subprocess.check_output') as mock_func:
            fp.stop(FlashDevices.BMC)
            self.assertEqual(2, mock_func.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_bmc))
    def test_multi_stop_fail(self, mock_pcf):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        with mock.patch('subprocess.check_output',
                        side_effect=[True, subprocess.CalledProcessError(1, "mock")]) as mock_func:
            with self.assertRaises(FlashEmulatorException):
                fp.stop(FlashDevices.BMC)
            self.assertEqual(2, mock_func.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_pch))
    def test_single_flash_image(self, mock_pcf):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        with mock.patch('subprocess.check_output') as mock_func:
            fp.flash_image("ifwi.bin", FlashDevices.PCH)
            self.assertEqual(1, mock_func.call_count)

            # Check that the --download command was sent to smucmd, without conflicting commands.
            command = Em100FlashEmulatorProvider.DP_FLASH
            conflicting_commands = [Em100FlashEmulatorProvider.DP_ADDRESS, Em100FlashEmulatorProvider.DP_LENGTH,
                                    Em100FlashEmulatorProvider.DP_READ]
            function_call = mock_func.call_args_list[0][0][0]
            self.assertIn(command, function_call)
            self.assertEqual(1, function_call.count(Em100FlashEmulatorProvider.DP_STOP))
            self.assertEqual(1, function_call.count(Em100FlashEmulatorProvider.DP_START))
            self.assertLess(function_call.index(Em100FlashEmulatorProvider.DP_STOP),
                            function_call.index(Em100FlashEmulatorProvider.DP_START))
            for conflicting_command in conflicting_commands:
                self.assertNotIn(conflicting_command, function_call)

        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_bmc))
    def test_single_flash_image_fail(self, mock_pcf):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        with mock.patch('subprocess.check_output', side_effect=subprocess.CalledProcessError(1, "mock")) as mock_func:
            with self.assertRaises(FlashProgrammerException):
                fp.flash_image("ifwi.bin", FlashDevices.BMC)
            self.assertEqual(2, mock_func.call_count)  # Includes emulator resume
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_pch))
    def test_multi_flash_image(self, mock_pcf):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        with mock.patch('subprocess.check_output') as mock_func:
            fp.flash_image("ifwi.bin", FlashDevices.PCH)
            self.assertEqual(3, mock_func.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_pch))
    def test_multi_flash_image_fail(self, mock_pcf):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        with mock.patch('subprocess.check_output',
                        side_effect=[True, True, subprocess.CalledProcessError(1, "mock"), True]) as mock_func:
            with self.assertRaises(FlashProgrammerException):
                fp.flash_image("ifwi.bin", FlashDevices.PCH)
            self.assertEqual(4, mock_func.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch("dtaf_core.providers.internal.em100_flash_emulator_provider.open", create=True)
    @mock.patch('os.stat', return_value=Namespace(st_size=3))
    @mock.patch('os.remove')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_bmc))
    def test_single_read(self, mock_pcf, mock_remove, mock_stat, mock_open, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address = 0x10
        test_length = 3
        test_data = bytes([0x0d, 0xec, 0xaf])

        mock_open.return_value = mock.MagicMock()
        mock_open.return_value.__enter__.return_value.read.return_value = test_data
        test_read = fp.read(test_address, test_length, FlashDevices.BMC)
        self.assertEqual(1, mock_check_output.call_count)
        self.assertEqual(bytearray(test_data), test_read)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(1, mock_remove.call_count)
        self.assertEqual(1, mock_stat.call_count)

        # Check that the --read command was sent to smucmd with --addr and --length flags, without conflicting commands.
        commands = [Em100FlashEmulatorProvider.DP_READ, Em100FlashEmulatorProvider.DP_ADDRESS,
                    Em100FlashEmulatorProvider.DP_LENGTH]
        conflicting_commands = [Em100FlashEmulatorProvider.DP_FLASH]
        function_call = mock_check_output.call_args_list[0][0][0]
        self.assertEqual(1, function_call.count(Em100FlashEmulatorProvider.DP_STOP))
        self.assertEqual(1, function_call.count(Em100FlashEmulatorProvider.DP_START))
        self.assertLess(function_call.index(Em100FlashEmulatorProvider.DP_STOP),
                        function_call.index(Em100FlashEmulatorProvider.DP_START))
        for command in commands:
            self.assertIn(command, function_call)
        for conflicting_command in conflicting_commands:
            self.assertNotIn(conflicting_command, function_call)

    @mock.patch("dtaf_core.providers.internal.em100_flash_emulator_provider.open", create=True)
    @mock.patch('subprocess.check_output')
    @mock.patch('os.stat', return_value=Namespace(st_size=16, st_mtime=0))
    @mock.patch('os.remove')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_pch))
    def test_single_read_fail_length(self, mock_pcf, mock_remove, mock_stat, mock_check_output, mock_open):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address = 0x10
        test_length = 3
        test_data = bytes([0x0d, 0xec, 0xaf])

        mock_open.return_value = mock.MagicMock()
        mock_open.return_value.__enter__.return_value.read.return_value = test_data
        with self.assertRaises(FlashProgrammerException):
            fp.read(test_address, test_length, FlashDevices.PCH)
        self.assertEqual(1, mock_check_output.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(1, mock_remove.call_count)

    @mock.patch('subprocess.check_output', side_effect=subprocess.CalledProcessError(5, "mock"))
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_pch))
    def test_single_read_cli_fail(self, mock_pcf, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address = 0x10
        test_length = 3

        with self.assertRaises(FlashProgrammerException):
            fp.read(test_address, test_length, FlashDevices.PCH)
        self.assertEqual(2, mock_check_output.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch("dtaf_core.providers.internal.em100_flash_emulator_provider.open", create=True)
    @mock.patch('os.stat', return_value=Namespace(st_size=20))
    @mock.patch('os.remove')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_bmc))
    def test_single_read_log_warning(self, mock_pcf, mock_remove, mock_stat, mock_open, mock_check_output):
        if six.PY2:
            self.skipTest("assertLogs isn't supported on Python 2.")
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address = 0x10
        test_length = 20
        test_data = bytearray(urandom(test_length))

        mock_open.return_value = mock.MagicMock()
        mock_open.return_value.__enter__.return_value.read.return_value = test_data
        with self.assertLogs(level='WARNING') as log_check:
            test_read = fp.read(test_address, test_length, FlashDevices.BMC)
            self.assertLess(len(log_check.output[0]), 150)  # 150 characters as a reasonable limit
        self.assertEqual(1, mock_check_output.call_count)
        self.assertEqual(test_data, test_read)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(1, mock_remove.call_count)
        self.assertEqual(1, mock_stat.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch("dtaf_core.providers.internal.em100_flash_emulator_provider.open", create=True)
    @mock.patch('os.stat', return_value=Namespace(st_size=20))
    @mock.patch('os.remove')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_bmc))
    def test_single_read_log_truncation(self, mock_pcf, mock_remove, mock_stat, mock_open, mock_check_output):
        if six.PY2:
            self.skipTest("assertLogs isn't supported on Python 2.")
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address = 0x10
        test_length = 20
        test_data = bytearray(urandom(test_length))

        mock_open.return_value = mock.MagicMock()
        mock_open.return_value.__enter__.return_value.read.return_value = test_data
        with self.assertLogs(level='DEBUG') as log_check:
            test_read = fp.read(test_address, test_length, FlashDevices.BMC)
            self.assertLess(len(log_check.output[1]), 80)  # 80 characters as a reasonable limit
        self.assertEqual(1, mock_check_output.call_count)
        self.assertEqual(test_data, test_read)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(1, mock_remove.call_count)
        self.assertEqual(1, mock_stat.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch("dtaf_core.providers.internal.em100_flash_emulator_provider.open", create=True)
    @mock.patch('os.stat', return_value=Namespace(st_size=15))
    @mock.patch('os.remove')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_bmc))
    def test_single_read_log_no_truncation(self, mock_pcf, mock_remove, mock_stat, mock_open, mock_check_output):
        if six.PY2:
            self.skipTest("assertLogs isn't supported on Python 2.")
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address = 0x10
        test_length = 15
        test_data = bytearray(urandom(test_length))

        mock_open.return_value = mock.MagicMock()
        mock_open.return_value.__enter__.return_value.read.return_value = test_data
        with self.assertLogs(level='DEBUG') as log_check:
            test_read = fp.read(test_address, test_length, FlashDevices.BMC)
            self.assertLess(len(log_check.output[0]), 80)  # 80 characters as a reasonable limit
        self.assertEqual(1, mock_check_output.call_count)
        self.assertEqual(test_data, test_read)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(1, mock_remove.call_count)
        self.assertEqual(1, mock_stat.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch("dtaf_core.providers.internal.em100_flash_emulator_provider.open", create=True)
    @mock.patch('os.stat', return_value=Namespace(st_size=3))
    @mock.patch('os.remove')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_pch))
    def test_multi_read(self, mock_pcf, mock_remove, mock_stat, mock_open, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address = 0x10
        test_length = 3
        test_data = bytes([0x0d, 0xec, 0xaf])

        mock_open.return_value = mock.MagicMock()
        mock_open.return_value.__enter__.return_value.read.return_value = test_data
        test_read = fp.read(test_address, test_length, FlashDevices.PCH)
        self.assertEqual(3, mock_check_output.call_count)
        self.assertEqual(bytearray(test_data), test_read)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(3, mock_remove.call_count)
        self.assertEqual(3, mock_stat.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch("dtaf_core.providers.internal.em100_flash_emulator_provider.open", create=True)
    @mock.patch('os.stat', return_value=Namespace(st_size=3))
    @mock.patch('os.remove')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_pch))
    def test_multi_read_fail(self, mock_pcf, mock_remove, mock_stat, mock_open, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address = 0x10
        test_length = 3
        test_data = bytes([0x0d, 0xec, 0xaf])
        test_data_wrong = bytes([0xde, 0xad, 0x00])

        mock_open.return_value = mock.MagicMock()
        mock_open.return_value.__enter__.return_value.read.side_effect = [test_data, test_data, test_data_wrong]
        if six.PY2:
            with self.assertRaisesRegexp(FlashProgrammerException, ".+consistent.+"):
                fp.read(test_address, test_length, FlashDevices.PCH)
        else:
            with self.assertRaisesRegex(FlashProgrammerException, ".+consistent.+"):
                fp.read(test_address, test_length, FlashDevices.PCH)
        self.assertEqual(3, mock_check_output.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(3, mock_remove.call_count)
        self.assertEqual(3, mock_stat.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch("dtaf_core.providers.internal.em100_flash_emulator_provider.open", create=True)
    @mock.patch('os.stat', return_value=Namespace(st_size=3))
    @mock.patch('os.remove')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_pch))
    def test_multi_read_fail_mid(self, mock_pcf, mock_remove, mock_stat, mock_open, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address = 0x10
        test_length = 3
        test_data = bytes([0x0d, 0xec, 0xaf])
        test_data_wrong = bytes([0xde, 0xad, 0x00])

        mock_open.return_value = mock.MagicMock()
        mock_open.return_value.__enter__.return_value.read.side_effect = [test_data, test_data_wrong, test_data]
        if six.PY2:
            with self.assertRaisesRegexp(FlashProgrammerException, ".+consistent.+"):
                fp.read(test_address, test_length, FlashDevices.PCH)
        else:
            with self.assertRaisesRegex(FlashProgrammerException, ".+consistent.+"):
                fp.read(test_address, test_length, FlashDevices.PCH)
        self.assertEqual(3, mock_check_output.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(3, mock_remove.call_count)
        self.assertEqual(3, mock_stat.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch("dtaf_core.providers.internal.em100_flash_emulator_provider.open", create=True)
    @mock.patch('os.stat', return_value=Namespace(st_size=3))
    @mock.patch('os.remove')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_pch))
    def test_multi_read_fail_start(self, mock_pcf, mock_remove, mock_stat, mock_open, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address = 0x10
        test_length = 3
        test_data = bytes([0x0d, 0xec, 0xaf])
        test_data_wrong = bytes([0xde, 0xad, 0x00])

        mock_open.return_value = mock.MagicMock()
        mock_open.return_value.__enter__.return_value.read.side_effect = [test_data_wrong, test_data, test_data]
        if six.PY2:
            with self.assertRaisesRegexp(FlashProgrammerException, ".+consistent.+"):
                fp.read(test_address, test_length, FlashDevices.PCH)
        else:
            with self.assertRaisesRegex(FlashProgrammerException, ".+consistent.+"):
                fp.read(test_address, test_length, FlashDevices.PCH)
        self.assertEqual(3, mock_check_output.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(3, mock_remove.call_count)
        self.assertEqual(3, mock_stat.call_count)

    @mock.patch('subprocess.check_output', side_effect=[None, None, subprocess.CalledProcessError(1, "mock"), None])
    @mock.patch("dtaf_core.providers.internal.em100_flash_emulator_provider.open", create=True)
    @mock.patch('os.stat', return_value=Namespace(st_size=3))
    @mock.patch('os.remove')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_pch))
    def test_multi_read_fail_exception(self, mock_pcf, mock_remove, mock_stat, mock_open, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address = 0x10
        test_length = 3
        test_data = bytes([0x0d, 0xec, 0xaf])
        test_data_wrong = bytes([0xde, 0xad, 0x00])

        mock_open.return_value = mock.MagicMock()
        mock_open.return_value.__enter__.return_value.read.side_effect = [test_data_wrong, test_data, test_data]
        with self.assertRaises(FlashProgrammerException):
            fp.read(test_address, test_length, FlashDevices.PCH)
        self.assertEqual(4, mock_check_output.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_remove.call_count)
        self.assertEqual(2, mock_stat.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch("dtaf_core.providers.internal.em100_flash_emulator_provider.open", create=True)
    @mock.patch('os.stat', return_value=Namespace(st_size=10000))
    @mock.patch('os.remove')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_bmc))
    def test_single_write(self, mock_pcf, mock_remove, mock_stat, mock_open, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address = 0x1000
        test_data = bytearray(urandom(1000))
        mock_mmap = mock.MagicMock()
        with mock.patch("mmap.mmap", return_value=mock_mmap):
            fp.write(test_address, test_data, FlashDevices.BMC)
            mock_mmap.__setitem__.assert_called_with(slice(test_address, test_address + len(test_data), None),
                                                     test_data)
            mock_mmap.flush.assert_called()
            mock_mmap.close.assert_called()

        self.assertEqual(2, mock_check_output.call_count)
        # Check that image was flashed to the same device that it was read from
        self.assertEqual(mock_check_output.call_args_list[0][0][0][2], mock_check_output.call_args_list[1][0][0][2])
        self.assertEqual(1, mock_pcf.call_count)

        # Check that the --read command was sent to smucmd without the --addr and --length or conflicting commands.
        command = Em100FlashEmulatorProvider.DP_READ
        conflicting_commands = [Em100FlashEmulatorProvider.DP_FLASH, Em100FlashEmulatorProvider.DP_ADDRESS,
                                Em100FlashEmulatorProvider.DP_LENGTH]
        function_call = mock_check_output.call_args_list[0][0][0]
        self.assertEqual(1, function_call.count(Em100FlashEmulatorProvider.DP_STOP))
        self.assertEqual(1, function_call.count(Em100FlashEmulatorProvider.DP_START))
        self.assertLess(function_call.index(Em100FlashEmulatorProvider.DP_STOP),
                        function_call.index(Em100FlashEmulatorProvider.DP_START))
        self.assertIn(command, function_call)
        for conflicting_command in conflicting_commands:
            self.assertNotIn(conflicting_command, function_call)

        # Check that the --download command was sent to smucmd with --verify flag, without conflicting commands.
        commands = [Em100FlashEmulatorProvider.DP_FLASH, Em100FlashEmulatorProvider.DP_VERIFY]
        conflicting_commands = [Em100FlashEmulatorProvider.DP_READ, Em100FlashEmulatorProvider.DP_LENGTH,
                                Em100FlashEmulatorProvider.DP_ADDRESS]
        function_call = mock_check_output.call_args_list[1][0][0]
        self.assertEqual(1, function_call.count(Em100FlashEmulatorProvider.DP_STOP))
        self.assertEqual(1, function_call.count(Em100FlashEmulatorProvider.DP_START))
        self.assertLess(function_call.index(Em100FlashEmulatorProvider.DP_STOP),
                        function_call.index(Em100FlashEmulatorProvider.DP_START))
        for command in commands:
            self.assertIn(command, function_call)
        for conflicting_command in conflicting_commands:
            self.assertNotIn(conflicting_command, function_call)

    @mock.patch('subprocess.check_output')
    @mock.patch("dtaf_core.providers.internal.em100_flash_emulator_provider.open", create=True)
    @mock.patch('os.stat', return_value=Namespace(st_size=10000, st_mtime=0))
    @mock.patch('os.remove')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_bmc))
    def test_single_write_mmap_fail(self, mock_pcf, mock_remove, mock_stat, mock_open, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address = 0x1000
        test_data = bytearray(urandom(1000))
        with mock.patch("mmap.mmap", side_effect=IOError):
            with self.assertRaises(IOError):
                fp.write(test_address, test_data, FlashDevices.BMC)

        self.assertEqual(1, mock_check_output.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('subprocess.check_output', side_effect=[None, subprocess.CalledProcessError(-1, "mock"), None])
    @mock.patch("dtaf_core.providers.internal.em100_flash_emulator_provider.open", create=True)
    @mock.patch('os.stat', return_value=Namespace(st_size=10000, st_mtime=0))
    @mock.patch('os.remove')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_bmc))
    def test_single_write_cli_fail(self, mock_pcf, mock_remove, mock_stat, mock_open, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address = 0x1000
        test_data = bytearray(urandom(1000))
        mock_mmap = mock.MagicMock()
        with mock.patch("mmap.mmap", return_value=mock_mmap):
            with self.assertRaises(FlashProgrammerException):
                fp.write(test_address, test_data, FlashDevices.BMC)
            mock_mmap.__setitem__.assert_called_with(slice(test_address, test_address + len(test_data), None),
                                                     test_data)
            mock_mmap.flush.assert_called()
            mock_mmap.close.assert_called()

        self.assertEqual(3, mock_check_output.call_count)
        # Check that image was flashed to the same device that it was read from
        self.assertEqual(mock_check_output.call_args_list[0][0][0][2], mock_check_output.call_args_list[1][0][0][2])
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch("dtaf_core.providers.internal.em100_flash_emulator_provider.open", create=True)
    @mock.patch('os.stat', return_value=Namespace(st_size=10000))
    @mock.patch('os.remove')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_bmc))
    def test_multi_write(self, mock_pcf, mock_remove, mock_stat, mock_open, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address = 0x1000
        test_data = bytearray(urandom(1000))
        mock_mmap = mock.MagicMock()
        with mock.patch("mmap.mmap", return_value=mock_mmap):
            fp.write(test_address, test_data, FlashDevices.BMC)
            mock_mmap.__setitem__.assert_called_with(slice(test_address, test_address + len(test_data), None),
                                                     test_data)
            mock_mmap.flush.assert_called()
            mock_mmap.close.assert_called()

        self.assertEqual(4, mock_check_output.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('subprocess.check_output',
                side_effect=[None, None, None, subprocess.CalledProcessError(-1, "mock"), None])
    @mock.patch("dtaf_core.providers.internal.em100_flash_emulator_provider.open", create=True)
    @mock.patch('os.stat', return_value=Namespace(st_size=10000, st_mtime=0))
    @mock.patch('os.remove')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_pch))
    def test_multi_write_fail(self, mock_pcf, mock_remove, mock_stat, mock_open, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address = 0x1000
        test_data = bytearray(urandom(1000))
        mock_mmap = mock.MagicMock()
        with mock.patch("mmap.mmap", return_value=mock_mmap):
            with self.assertRaises(FlashProgrammerException):
                fp.write(test_address, test_data, FlashDevices.PCH)
            mock_mmap.__setitem__.assert_called_with(slice(test_address, test_address + len(test_data), None),
                                                     test_data)
            mock_mmap.flush.assert_called()
            mock_mmap.close.assert_called()

        self.assertEqual(5, mock_check_output.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch("dtaf_core.providers.internal.em100_flash_emulator_provider.open", create=True)
    @mock.patch('os.stat', side_effect=[Namespace(st_size=10), Namespace(st_size=50)])
    @mock.patch('os.remove')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_single_both))
    def test_pch_and_bmc_read(self, mock_pcf, mock_remove, mock_stat, mock_open, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address_pch = 0x10
        test_length_pch = 10
        test_data_pch = bytearray(urandom(test_length_pch))

        test_address_bmc = 0x100F0CA1
        test_length_bmc = 50
        test_data_bmc = bytearray(urandom(test_length_bmc))

        mock_open.return_value = mock.MagicMock()
        mock_open.return_value.__enter__.return_value.read.side_effect = [test_data_pch, test_data_bmc]
        test_read_pch = fp.read(test_address_pch, test_length_pch, FlashDevices.PCH)
        test_read_bmc = fp.read(test_address_bmc, test_length_bmc, FlashDevices.BMC)
        self.assertEqual(2, mock_check_output.call_count)
        self.assertEqual(test_data_pch, test_read_pch)
        self.assertEqual(test_data_bmc, test_read_bmc)
        self.assertEqual(2, mock_remove.call_count)
        self.assertEqual(2, mock_stat.call_count)

        # Check that PCH call was directed to the PCH and BMC call was directed to the BMC.
        pch_device_used = mock_check_output.call_args_list[0][0][0][2]
        bmc_device_used = mock_check_output.call_args_list[1][0][0][2]
        self.assertNotEqual(pch_device_used, bmc_device_used)
        self.assertEqual(fp.device_mapping[FlashDevices.PCH][1][0], str(pch_device_used))
        self.assertEqual(fp.device_mapping[FlashDevices.BMC][1][0], str(bmc_device_used))
        self.assertEqual(len(fp.device_mapping[FlashDevices.PCH][1]), 1)
        self.assertEqual(len(fp.device_mapping[FlashDevices.BMC][1]), 1)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch("dtaf_core.providers.internal.em100_flash_emulator_provider.open", create=True)
    @mock.patch('os.stat', side_effect=[Namespace(st_size=100000), Namespace(st_size=200000)])
    @mock.patch('os.remove')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_single_both))
    def test_pch_and_bmc_write(self, mock_pcf, mock_remove, mock_stat, mock_open, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address_pch = 0x4000
        test_length_pch = 100
        test_data_pch = bytearray(urandom(test_length_pch))

        test_address_bmc = 0x5000
        test_length_bmc = 500
        test_data_bmc = bytearray(urandom(test_length_bmc))

        mock_mmap_pch = mock.MagicMock()
        mock_mmap_bmc = mock.MagicMock()
        with mock.patch("mmap.mmap", side_effect=[mock_mmap_bmc, mock_mmap_pch]):
            fp.write(test_address_bmc, test_data_bmc, FlashDevices.BMC)
            fp.write(test_address_pch, test_data_pch, FlashDevices.PCH)

        mock_mmap_bmc.__setitem__.assert_called_with(slice(test_address_bmc, test_address_bmc + test_length_bmc, None),
                                                     test_data_bmc)
        mock_mmap_bmc.flush.assert_called()
        mock_mmap_bmc.close.assert_called()
        mock_mmap_pch.__setitem__.assert_called_with(slice(test_address_pch, test_address_pch + test_length_pch, None),
                                                     test_data_pch)
        mock_mmap_pch.flush.assert_called()
        mock_mmap_pch.close.assert_called()

        self.assertEqual(4, mock_check_output.call_count)
        self.assertEqual(2, mock_remove.call_count)
        self.assertEqual(2, mock_stat.call_count)

        # Check that PCH calls were directed to the PCH and BMC calls were directed to the BMC.
        pch_device_used = mock_check_output.call_args_list[2][0][0][2]
        bmc_device_used = mock_check_output.call_args_list[0][0][0][2]
        self.assertEqual(pch_device_used, mock_check_output.call_args_list[3][0][0][2])
        self.assertEqual(bmc_device_used, mock_check_output.call_args_list[1][0][0][2])
        self.assertNotEqual(pch_device_used, bmc_device_used)
        self.assertEqual(fp.device_mapping[FlashDevices.PCH][1][0], str(pch_device_used))
        self.assertEqual(fp.device_mapping[FlashDevices.BMC][1][0], str(bmc_device_used))
        self.assertEqual(len(fp.device_mapping[FlashDevices.PCH][1]), 1)
        self.assertEqual(len(fp.device_mapping[FlashDevices.BMC][1]), 1)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_single_both))
    def test_pch_and_bmc_flash(self, mock_pcf, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider

        fp.flash_image("ifwi.bin", FlashDevices.PCH)
        fp.flash_image("ifwi.bin", FlashDevices.BMC)

        self.assertEqual(2, mock_check_output.call_count)
        self.assertEqual(1, mock_pcf.call_count)

        # Check that PCH calls were directed to the PCH and BMC calls were directed to the BMC.
        pch_device_used = mock_check_output.call_args_list[0][0][0][2]
        bmc_device_used = mock_check_output.call_args_list[1][0][0][2]
        self.assertNotEqual(pch_device_used, bmc_device_used)
        self.assertEqual(fp.device_mapping[FlashDevices.PCH][1][0], str(pch_device_used))
        self.assertEqual(fp.device_mapping[FlashDevices.BMC][1][0], str(bmc_device_used))
        self.assertEqual(len(fp.device_mapping[FlashDevices.PCH][1]), 1)
        self.assertEqual(len(fp.device_mapping[FlashDevices.BMC][1]), 1)

    @mock.patch('subprocess.check_output')
    @mock.patch("dtaf_core.providers.internal.em100_flash_emulator_provider.open", create=True)
    @mock.patch('os.stat', side_effect=[Namespace(st_size=500, st_mtime=0) for _ in range(0, 4)] +
                                       [Namespace(st_size=350, st_mtime=0) for _ in range(0, 4)])
    @mock.patch('os.remove')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_both))
    def test_multi_pch_and_multi_bmc_read(self, mock_pcf, mock_remove, mock_stat, mock_open, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address_pch = 0x10
        test_length_pch = 500
        test_data_pch = bytearray(urandom(test_length_pch))

        test_address_bmc = 0x100F0CA1
        test_length_bmc = 350
        test_data_bmc = bytearray(urandom(test_length_bmc))

        mock_open.return_value = mock.MagicMock()
        mock_open.return_value.__enter__.return_value.read.side_effect = [test_data_pch for _ in range(0, 4)] + \
                                                                         [test_data_bmc for _ in range(0, 4)]
        test_read_pch = fp.read(test_address_pch, test_length_pch, FlashDevices.PCH)
        test_read_bmc = fp.read(test_address_bmc, test_length_bmc, FlashDevices.BMC)
        self.assertEqual(8, mock_check_output.call_count)
        self.assertEqual(test_data_pch, test_read_pch)
        self.assertEqual(test_data_bmc, test_read_bmc)
        self.assertEqual(8, mock_remove.call_count)
        self.assertEqual(8, mock_stat.call_count)

        # Check that PCH calls were directed to the PCH and BMC calls were directed to the BMC.
        for i in range(0, 4):
            self.assertIn(mock_check_output.call_args_list[i][0][0][2], fp.device_mapping[FlashDevices.PCH][1])
            self.assertNotIn(mock_check_output.call_args_list[i][0][0][2], fp.device_mapping[FlashDevices.BMC][1])
            self.assertIn(mock_check_output.call_args_list[4 + i][0][0][2], fp.device_mapping[FlashDevices.BMC][1])
            self.assertNotIn(mock_check_output.call_args_list[4 + i][0][0][2], fp.device_mapping[FlashDevices.PCH][1])
        self.assertEqual(len(fp.device_mapping[FlashDevices.PCH][1]), 4)
        self.assertEqual(len(fp.device_mapping[FlashDevices.BMC][1]), 4)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch("dtaf_core.providers.internal.em100_flash_emulator_provider.open", create=True)
    @mock.patch('os.stat', side_effect=[Namespace(st_size=100000, st_mtime=0) for _ in range(0, 4)] +
                                       [Namespace(st_size=200000, st_mtime=0) for _ in range(0, 4)])
    @mock.patch('os.remove')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_both))
    def test_multi_pch_and_multi_bmc_write(self, mock_pcf, mock_remove, mock_stat, mock_open, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address_pch = 0x4000
        test_length_pch = 100
        test_data_pch = bytearray(urandom(test_length_pch))

        test_address_bmc = 0x5000
        test_length_bmc = 500
        test_data_bmc = bytearray(urandom(test_length_bmc))

        mock_mmap_pch = mock.MagicMock()
        mock_mmap_bmc = mock.MagicMock()
        with mock.patch("mmap.mmap", side_effect=[mock_mmap_bmc for _ in range(0, 4)] +
                                                 [mock_mmap_pch for _ in range(0, 4)]):
            fp.write(test_address_bmc, test_data_bmc, FlashDevices.BMC)
            fp.write(test_address_pch, test_data_pch, FlashDevices.PCH)

        mock_mmap_bmc.__setitem__.assert_called_with(slice(test_address_bmc, test_address_bmc + test_length_bmc, None),
                                                     test_data_bmc)
        self.assertEqual(4, mock_mmap_bmc.flush.call_count)
        self.assertEqual(4, mock_mmap_bmc.close.call_count)
        mock_mmap_pch.__setitem__.assert_called_with(slice(test_address_pch, test_address_pch + test_length_pch, None),
                                                     test_data_pch)
        self.assertEqual(4, mock_mmap_pch.flush.call_count)
        self.assertEqual(4, mock_mmap_pch.close.call_count)

        self.assertEqual(16, mock_check_output.call_count)
        self.assertEqual(8, mock_remove.call_count)
        self.assertEqual(8, mock_stat.call_count)

        # Check that PCH calls were directed to the PCH and BMC calls were directed to the BMC.
        for i in range(0, 4):
            self.assertIn(mock_check_output.call_args_list[2 * i][0][0][2], fp.device_mapping[FlashDevices.BMC][1])
            self.assertNotIn(mock_check_output.call_args_list[2 * i][0][0][2], fp.device_mapping[FlashDevices.PCH][1])
            self.assertEqual(mock_check_output.call_args_list[2 * i][0][0][2],
                             mock_check_output.call_args_list[2 * i + 1][0][0][2])
            self.assertIn(mock_check_output.call_args_list[8 + 2 * i][0][0][2],
                          fp.device_mapping[FlashDevices.PCH][1])
            self.assertNotIn(mock_check_output.call_args_list[8 + 2 * i][0][0][2],
                             fp.device_mapping[FlashDevices.BMC][1])
            self.assertEqual(mock_check_output.call_args_list[2 * i + 8][0][0][2],
                             mock_check_output.call_args_list[2 * i + 8 + 1][0][0][2])
        self.assertEqual(len(fp.device_mapping[FlashDevices.PCH][1]), 4)
        self.assertEqual(len(fp.device_mapping[FlashDevices.BMC][1]), 4)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_both))
    def test_multi_pch_and_multi_bmc_flash(self, mock_pcf, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider

        fp.flash_image("ifwi.bin", FlashDevices.BMC)
        fp.flash_image("ifwi.bin", FlashDevices.PCH)

        self.assertEqual(8, mock_check_output.call_count)

        # Check that PCH calls were directed to the PCH and BMC calls were directed to the BMC.
        for i in range(0, 4):
            self.assertIn(mock_check_output.call_args_list[i][0][0][2], fp.device_mapping[FlashDevices.BMC][1])
            self.assertNotIn(mock_check_output.call_args_list[i][0][0][2], fp.device_mapping[FlashDevices.PCH][1])
            self.assertIn(mock_check_output.call_args_list[4 + i][0][0][2], fp.device_mapping[FlashDevices.PCH][1])
            self.assertNotIn(mock_check_output.call_args_list[4 + i][0][0][2], fp.device_mapping[FlashDevices.BMC][1])
        self.assertEqual(len(fp.device_mapping[FlashDevices.PCH][1]), 4)
        self.assertEqual(len(fp.device_mapping[FlashDevices.BMC][1]), 4)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch('os.stat', return_value=Namespace(st_size=0x2000, st_mtime=0))
    @mock.patch('os.remove')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_pch))
    def test_write_past_end(self, mock_pcf, mock_remove, mock_stat, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address_pch = 0x2010
        test_length_pch = 100
        test_data_pch = bytearray(urandom(test_length_pch))

        with self.assertRaises(ValueError):
            fp.write(test_address_pch, test_data_pch, FlashDevices.PCH)

        self.assertEqual(1, mock_check_output.call_count)
        self.assertEqual(1, mock_remove.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch('os.stat', return_value=Namespace(st_size=0x2000, st_mtime=0))
    @mock.patch('os.remove')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_pch))
    def test_write_overflow_past_end(self, mock_pcf, mock_remove, mock_stat, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address_pch = 0x1FF0
        test_length_pch = 100
        test_data_pch = bytearray(urandom(test_length_pch))

        with self.assertRaises(ValueError):
            fp.write(test_address_pch, test_data_pch, FlashDevices.PCH)

        self.assertEqual(1, mock_check_output.call_count)
        self.assertEqual(1, mock_remove.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_pch))
    def test_write_invalid_address(self, mock_pcf, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address_pch = -0x1980
        test_length_pch = 100
        test_data_pch = bytearray(urandom(test_length_pch))

        with self.assertRaises(ValueError):
            fp.write(test_address_pch, test_data_pch, FlashDevices.PCH)

        self.assertEqual(0, mock_check_output.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_pch))
    def test_write_invalid_value(self, mock_pcf, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        test_address_pch = 0x1980
        test_data_pch = "0xdecaf"

        with self.assertRaises(ValueError):
            # noinspection PyTypeChecker
            fp.write(test_address_pch, test_data_pch, FlashDevices.PCH)

        self.assertEqual(0, mock_check_output.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_one_pch))
    def test_read_invalid_address(self, mock_pcf, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        with self.assertRaises(ValueError):
            fp.read(-1, 20, FlashDevices.PCH)
        self.assertEqual(0, mock_check_output.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_both))
    def test_invalid_length(self, mock_pcf, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        with self.assertRaises(ValueError):
            fp.read(0x1000, -20, FlashDevices.PCH)
        self.assertEqual(0, mock_check_output.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_single_both))
    def test_start_single(self, mock_pcf, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        fp.start(FlashDevices.PCH)
        fp.start(FlashDevices.BMC)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_check_output.call_count)

        # Check that the --start command was sent to smucmd, without conflicting commands.
        command = Em100FlashEmulatorProvider.DP_START
        conflicting_commands = [Em100FlashEmulatorProvider.DP_STOP, Em100FlashEmulatorProvider.DP_FLASH,
                                Em100FlashEmulatorProvider.DP_ADDRESS, Em100FlashEmulatorProvider.DP_LENGTH,
                                Em100FlashEmulatorProvider.DP_READ]
        self.assertIn(command, mock_check_output.call_args_list[0][0][0])
        self.assertIn(command, mock_check_output.call_args_list[1][0][0])
        for conflicting_command in conflicting_commands:
            self.assertNotIn(conflicting_command, mock_check_output.call_args_list[0][0][0])
            self.assertNotIn(conflicting_command, mock_check_output.call_args_list[1][0][0])

        # Check that PCH calls were directed to the PCH and BMC calls were directed to the BMC.
        pch_device_used = mock_check_output.call_args_list[0][0][0][2]
        bmc_device_used = mock_check_output.call_args_list[1][0][0][2]
        self.assertNotEqual(pch_device_used, bmc_device_used)
        self.assertEqual(fp.device_mapping[FlashDevices.PCH][1][0], str(pch_device_used))
        self.assertEqual(fp.device_mapping[FlashDevices.BMC][1][0], str(bmc_device_used))
        self.assertEqual(len(fp.device_mapping[FlashDevices.PCH][1]), 1)
        self.assertEqual(len(fp.device_mapping[FlashDevices.BMC][1]), 1)

    @mock.patch('subprocess.check_output', side_effect=subprocess.CalledProcessError(6, "mock"))
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_single_both))
    def test_start_single_fail(self, mock_pcf, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        with self.assertRaises(FlashEmulatorException):
            fp.start(FlashDevices.PCH)
        with self.assertRaises(FlashEmulatorException):
            fp.start(FlashDevices.BMC)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_check_output.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_both))
    def test_start_multi(self, mock_pcf, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        fp.start(FlashDevices.PCH)
        fp.start(FlashDevices.BMC)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(8, mock_check_output.call_count)

        # Check that PCH calls were directed to the PCH and BMC calls were directed to the BMC.
        for i in range(0, 4):
            self.assertIn(mock_check_output.call_args_list[i][0][0][2], fp.device_mapping[FlashDevices.PCH][1])
            self.assertNotIn(mock_check_output.call_args_list[i][0][0][2], fp.device_mapping[FlashDevices.BMC][1])
            self.assertIn(mock_check_output.call_args_list[4 + i][0][0][2], fp.device_mapping[FlashDevices.BMC][1])
            self.assertNotIn(mock_check_output.call_args_list[4 + i][0][0][2], fp.device_mapping[FlashDevices.PCH][1])
        self.assertEqual(len(fp.device_mapping[FlashDevices.PCH][1]), 4)
        self.assertEqual(len(fp.device_mapping[FlashDevices.BMC][1]), 4)

    @mock.patch('subprocess.check_output', side_effect=[None, None, subprocess.CalledProcessError(5, "None"),
                                                        None, None, None, subprocess.CalledProcessError(4, "None")])
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_both))
    def test_start_multi_fail(self, mock_pcf, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        with self.assertRaises(FlashEmulatorException):
            fp.start(FlashDevices.PCH)
        self.assertEqual(3, mock_check_output.call_count)

        with self.assertRaises(FlashEmulatorException):
            fp.start(FlashDevices.BMC)
        self.assertEqual(7, mock_check_output.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_single_both))
    def test_stop_single(self, mock_pcf, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        fp.stop(FlashDevices.PCH)
        fp.stop(FlashDevices.BMC)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_check_output.call_count)

        # Check that the --start command was sent to smucmd, without conflicting commands.
        command = Em100FlashEmulatorProvider.DP_STOP
        conflicting_commands = [Em100FlashEmulatorProvider.DP_START, Em100FlashEmulatorProvider.DP_FLASH,
                                Em100FlashEmulatorProvider.DP_ADDRESS, Em100FlashEmulatorProvider.DP_LENGTH,
                                Em100FlashEmulatorProvider.DP_READ]
        self.assertIn(command, mock_check_output.call_args_list[0][0][0])
        self.assertIn(command, mock_check_output.call_args_list[1][0][0])
        for conflicting_command in conflicting_commands:
            self.assertNotIn(conflicting_command, mock_check_output.call_args_list[0][0][0])
            self.assertNotIn(conflicting_command, mock_check_output.call_args_list[1][0][0])

        # Check that PCH calls were directed to the PCH and BMC calls were directed to the BMC.
        pch_device_used = mock_check_output.call_args_list[0][0][0][2]
        bmc_device_used = mock_check_output.call_args_list[1][0][0][2]
        self.assertNotEqual(pch_device_used, bmc_device_used)
        self.assertEqual(fp.device_mapping[FlashDevices.PCH][1][0], str(pch_device_used))
        self.assertEqual(fp.device_mapping[FlashDevices.BMC][1][0], str(bmc_device_used))
        self.assertEqual(len(fp.device_mapping[FlashDevices.PCH][1]), 1)
        self.assertEqual(len(fp.device_mapping[FlashDevices.BMC][1]), 1)

    @mock.patch('subprocess.check_output', side_effect=subprocess.CalledProcessError(6, "mock"))
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_single_both))
    def test_stop_single_fail(self, mock_pcf, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        with self.assertRaises(FlashEmulatorException):
            fp.stop(FlashDevices.PCH)
        with self.assertRaises(FlashEmulatorException):
            fp.stop(FlashDevices.BMC)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_check_output.call_count)

    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_both))
    def test_stop_multi(self, mock_pcf, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        fp.stop(FlashDevices.PCH)
        fp.stop(FlashDevices.BMC)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(8, mock_check_output.call_count)

        # Check that PCH calls were directed to the PCH and BMC calls were directed to the BMC.
        for i in range(0, 4):
            self.assertIn(mock_check_output.call_args_list[i][0][0][2], fp.device_mapping[FlashDevices.PCH][1])
            self.assertNotIn(mock_check_output.call_args_list[i][0][0][2], fp.device_mapping[FlashDevices.BMC][1])
            self.assertIn(mock_check_output.call_args_list[4 + i][0][0][2], fp.device_mapping[FlashDevices.BMC][1])
            self.assertNotIn(mock_check_output.call_args_list[4 + i][0][0][2], fp.device_mapping[FlashDevices.PCH][1])
        self.assertEqual(len(fp.device_mapping[FlashDevices.PCH][1]), 4)
        self.assertEqual(len(fp.device_mapping[FlashDevices.BMC][1]), 4)

    @mock.patch('subprocess.check_output', side_effect=[None, None, subprocess.CalledProcessError(5, "None"),
                                                        None, None, None, subprocess.CalledProcessError(4, "None")])
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=Namespace(driver_cfg=mock_config_multi_both))
    def test_stop_multi_fail(self, mock_pcf, mock_check_output):
        fp = Em100FlashEmulatorProvider(self.mock_xml, logging.getLogger())  # type: Em100FlashEmulatorProvider
        with self.assertRaises(FlashEmulatorException):
            fp.stop(FlashDevices.PCH)
        self.assertEqual(3, mock_check_output.call_count)

        with self.assertRaises(FlashEmulatorException):
            fp.stop(FlashDevices.BMC)
        self.assertEqual(7, mock_check_output.call_count)
        self.assertEqual(1, mock_pcf.call_count)


if __name__ == "__main__":
    unittest.main()
