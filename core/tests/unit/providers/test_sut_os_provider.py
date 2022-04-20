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
import xml
import mock
import logging
import unittest
from argparse import Namespace
from dtaf_core.lib.exceptions import UnsupportedOsException, OsStateTransitionException
from dtaf_core.lib.os_lib import OsCommandResult, Linux, Windows
from dtaf_core.providers.internal.ssh_sut_os_provider import SutOsProvider


class TestSutOsProvider(unittest.TestCase):
    """Unit tests for SutOsProvider interface"""

    @classmethod
    def setUpClass(cls):
        # Must allow instantiation of abstract base class, otherwise ABCMeta will block it
        SutOsProvider.__abstractmethods__ = set()

    # Mock Provider configurations
    mock_xml = xml.etree.ElementTree.fromstring("<mock />")
    mock_config_linux = Namespace(os_type="Linux", os_subtype="RHEL", os_version="7.6", os_kernel="3.10",
                                  shutdown_delay=5.0,verify='false')
    mock_config_windows = Namespace(os_type="Windows", os_subtype="Server", os_version="2019", os_kernel="18077",
                                    shutdown_delay=5.0,verify='false')
    mock_config_unsupported_os = Namespace(os_type="macOS", os_subtype="X", os_version="10.15", os_kernel="19.0.0",
                                           shutdown_delay=5.0,verify='false')

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_unsupported_os)
    def test_unsupported_os_fail(self, mock_pcf):
        """Test an unsupported OS configuration"""
        with self.assertRaises(UnsupportedOsException):
            SutOsProvider(self.mock_xml, logging.getLogger())

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    @mock.patch.object(SutOsProvider, 'execute', return_value=OsCommandResult(0, "rebooted", ""))
    @mock.patch.object(SutOsProvider, 'is_alive', side_effect=[False])
    @mock.patch.object(SutOsProvider, 'wait_for_os')
    def test_reboot_linux_pass(self, mock_wait, mock_is_alive, mock_execute, mock_pcf):
        """Test that function executes the correct reboot command for Linux"""
        os = SutOsProvider(self.mock_xml, logging.getLogger())
        os.os_shutdown_delay = 0.01
        os.reboot(1.0)
        self.assertEqual(1, mock_execute.call_count)
        self.assertEqual(1, mock_wait.call_count)
        self.assertEqual(1, mock_is_alive.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(mock.call(Linux.Commands.RESTART, os.os_shutdown_delay), mock_execute.call_args_list[0])

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_windows)
    @mock.patch.object(SutOsProvider, 'execute', return_value=OsCommandResult(0, "rebooted", ""))
    @mock.patch.object(SutOsProvider, 'is_alive', side_effect=[False])
    @mock.patch.object(SutOsProvider, 'wait_for_os')
    def test_reboot_windows_pass(self, mock_wait, mock_is_alive, mock_execute, mock_pcf):
        """Test that function executes the correct reboot command for Windows"""
        os = SutOsProvider(self.mock_xml, logging.getLogger())
        os.os_shutdown_delay = 0.01
        os.reboot(1.0)
        self.assertEqual(1, mock_execute.call_count)
        self.assertEqual(1, mock_wait.call_count)
        self.assertEqual(1, mock_is_alive.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(mock.call(Windows.Commands.RESTART, os.os_shutdown_delay), mock_execute.call_args_list[0])

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    @mock.patch.object(SutOsProvider, 'execute', return_value=OsCommandResult(0, "", ""))
    @mock.patch.object(SutOsProvider, 'is_alive', side_effect=[False])
    @mock.patch.object(SutOsProvider, 'wait_for_os')
    def test_reboot_pass_no_stdout(self, mock_wait, mock_is_alive, mock_execute, mock_pcf):
        """Test reboot when reboot command passes but gives no output"""
        os = SutOsProvider(self.mock_xml, logging.getLogger())
        os.os_shutdown_delay = 0.01
        os.reboot(1.0)
        self.assertEqual(1, mock_execute.call_count)
        self.assertEqual(1, mock_wait.call_count)
        self.assertEqual(1, mock_is_alive.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    @mock.patch.object(SutOsProvider, 'execute', return_value=OsCommandResult(1, "", ""))
    @mock.patch.object(SutOsProvider, 'is_alive', side_effect=[True])
    @mock.patch.object(SutOsProvider, 'wait_for_os')
    def test_reboot_cmd_fail(self, mock_wait, mock_is_alive, mock_execute, mock_pcf):
        """Test reboot function to ensure a command failure is detected, even if it fails silently"""
        os = SutOsProvider(self.mock_xml, logging.getLogger())
        os.os_shutdown_delay = 0.01
        with self.assertRaises(OsStateTransitionException):
            os.reboot(1.0)
        self.assertEqual(1, mock_execute.call_count)
        self.assertEqual(0, mock_wait.call_count)
        self.assertEqual(1, mock_is_alive.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    @mock.patch.object(SutOsProvider, 'execute', return_value=OsCommandResult(1, "", "hello"))
    @mock.patch.object(SutOsProvider, 'is_alive', side_effect=[True])
    @mock.patch.object(SutOsProvider, 'wait_for_os')
    def test_reboot_cmd_stderr(self, mock_wait, mock_is_alive, mock_execute, mock_pcf):
        """Test reboot function to ensure a command failure is detected"""
        os = SutOsProvider(self.mock_xml, logging.getLogger())
        os.os_shutdown_delay = 0.01
        with self.assertRaises(OsStateTransitionException):
            os.reboot(1.0)
        self.assertEqual(1, mock_execute.call_count)
        self.assertEqual(0, mock_wait.call_count)
        self.assertEqual(1, mock_is_alive.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    @mock.patch.object(SutOsProvider, 'execute', return_value=OsCommandResult(0, "", "hello"))
    @mock.patch.object(SutOsProvider, 'is_alive', side_effect=[True])
    @mock.patch.object(SutOsProvider, 'wait_for_os')
    def test_reboot_cmd_stderr_only(self, mock_wait, mock_is_alive, mock_execute, mock_pcf):
        """
        Test reboot function to ensure a command failure is detected even if the return code is passing, but
        stderr is populated. This is to provide for the fact that some OSes have to execute reboot in the background,
        meaning that the return code will always be 0, so only stderr can indicate an error.
        """
        os = SutOsProvider(self.mock_xml, logging.getLogger())
        os.os_shutdown_delay = 0.01
        with self.assertRaises(OsStateTransitionException):
            os.reboot(1.0)
        self.assertEqual(1, mock_execute.call_count)
        self.assertEqual(0, mock_wait.call_count)
        self.assertEqual(1, mock_is_alive.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    @mock.patch.object(SutOsProvider, 'execute', return_value=OsCommandResult(0, "rebooted", ""))
    @mock.patch.object(SutOsProvider, 'is_alive', side_effect=[True])
    def test_reboot_machine_stuck_on(self, mock_is_alive, mock_execute, mock_pcf):
        """Test reboot function to ensure if SUT is stuck on, it is reported as a failure."""
        os = SutOsProvider(self.mock_xml, logging.getLogger())
        os.os_shutdown_delay = 0.01
        with self.assertRaises(OsStateTransitionException):
            os.reboot(1.0)
        self.assertEqual(1, mock_execute.call_count)
        self.assertEqual(1, mock_is_alive.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    @mock.patch.object(SutOsProvider, 'execute', return_value=OsCommandResult(0, "shutdown", ""))
    @mock.patch.object(SutOsProvider, 'is_alive', side_effect=[False])
    def test_shutdown_linux_pass(self, mock_is_alive, mock_execute, mock_pcf):
        """Test shutdown when provider should select a Linux command"""
        os = SutOsProvider(self.mock_xml, logging.getLogger())
        os.os_shutdown_delay = 1.0
        os.shutdown(1.0)
        self.assertEqual(1, mock_execute.call_count)
        self.assertEqual(1, mock_is_alive.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(mock.call(Linux.Commands.SHUTDOWN, os.os_shutdown_delay), mock_execute.call_args_list[0])

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_windows)
    @mock.patch.object(SutOsProvider, 'execute', return_value=OsCommandResult(0, "shutdown", ""))
    @mock.patch.object(SutOsProvider, 'is_alive', side_effect=[False])
    def test_shutdown_windows_pass(self, mock_is_alive, mock_execute, mock_pcf):
        """Test shutdown when provider should select a Windows command"""
        os = SutOsProvider(self.mock_xml, logging.getLogger())
        os.os_shutdown_delay = 1.0
        os.shutdown(1.0)
        self.assertEqual(1, mock_execute.call_count)
        self.assertEqual(1, mock_is_alive.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(mock.call(Windows.Commands.SHUTDOWN, os.os_shutdown_delay), mock_execute.call_args_list[0])

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_windows)
    @mock.patch.object(SutOsProvider, 'execute', return_value=OsCommandResult(0, "", ""))
    @mock.patch.object(SutOsProvider, 'is_alive', side_effect=[False])
    def test_shutdown_pass_no_stdout(self, mock_is_alive, mock_execute, mock_pcf):
        """Test that shutdown passes when the command passes and the SUT shuts off as expected"""
        os = SutOsProvider(self.mock_xml, logging.getLogger())
        os.os_shutdown_delay = 0.01
        os.shutdown(1.0)
        self.assertEqual(1, mock_execute.call_count)
        self.assertEqual(1, mock_is_alive.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    @mock.patch.object(SutOsProvider, 'execute', return_value=OsCommandResult(1, "", ""))
    @mock.patch.object(SutOsProvider, 'is_alive', side_effect=[False])
    def test_shutdown_cmd_fail(self, mock_is_alive, mock_execute, mock_pcf):
        """Test that function detects failed shutdown commands, even if it fails silently"""
        os = SutOsProvider(self.mock_xml, logging.getLogger())
        os.os_shutdown_delay = 0.01
        with self.assertRaises(OsStateTransitionException):
            os.shutdown(1.0)
        self.assertEqual(1, mock_execute.call_count)
        self.assertEqual(0, mock_is_alive.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    @mock.patch.object(SutOsProvider, 'execute', return_value=OsCommandResult(1, "", "hello"))
    @mock.patch.object(SutOsProvider, 'is_alive', side_effect=[False])
    def test_shutdown_cmd_stderr(self, mock_is_alive, mock_execute, mock_pcf):
        """Test that function detects failed shutdown commands."""
        os = SutOsProvider(self.mock_xml, logging.getLogger())
        os.os_shutdown_delay = 0.01
        with self.assertRaises(OsStateTransitionException):
            os.shutdown(1.0)
        self.assertEqual(1, mock_execute.call_count)
        self.assertEqual(0, mock_is_alive.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    @mock.patch.object(SutOsProvider, 'execute', return_value=OsCommandResult(0, "", "hello"))
    @mock.patch.object(SutOsProvider, 'is_alive', side_effect=[False])
    def test_shutdown_cmd_stderr_only(self, mock_is_alive, mock_execute, mock_pcf):
        """Test that function detects failed shutdown commands even if only stderr is populated"""
        os = SutOsProvider(self.mock_xml, logging.getLogger())
        os.os_shutdown_delay = 0.01
        with self.assertRaises(OsStateTransitionException):
            os.shutdown(1.0)
        self.assertEqual(1, mock_execute.call_count)
        self.assertEqual(0, mock_is_alive.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    @mock.patch.object(SutOsProvider, 'execute', return_value=OsCommandResult(0, "rebooted", ""))
    @mock.patch.object(SutOsProvider, 'is_alive', side_effect=[False])
    def test_shutdown_machine_stuck_on(self, mock_is_alive, mock_execute, mock_pcf):
        """Test that function detects when SUT is stuck on after issuing the shutdown command"""
        os = SutOsProvider(self.mock_xml, logging.getLogger())
        os.os_shutdown_delay = 0.01
        os.shutdown(1.0)
        self.assertEqual(1, mock_execute.call_count)
        self.assertEqual(1, mock_is_alive.call_count)
        self.assertEqual(1, mock_pcf.call_count)


if __name__ == "__main__":
    unittest.main()
