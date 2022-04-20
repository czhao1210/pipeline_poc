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
import socket
import logging
import six
import unittest

if six.PY2:
    import mock
if six.PY3 or six.PY34:
    from unittest import mock
from argparse import Namespace
from invoke import CommandTimedOut
from paramiko import SSHException
from paramiko.ssh_exception import NoValidConnectionsError
from dtaf_core.providers.internal.ssh_sut_os_provider import SshSutOsProvider


class TestSshSutOsProvider(unittest.TestCase):
    """Unit tests for SshSutOsProvider"""

    # Mock Driver configurations
    mock_xml = xml.etree.ElementTree.fromstring("<mock />")
    mock_ssh_driver_config = Namespace(ip="0.0.0.0", user="mock", password="mock", retry_cnt=1,
                                       jump_host=None, jump_user=None, server_path=None, enable=False, jump_auth=None,
                                       port=22)

    # Mock Provider configurations
    mock_config_linux = Namespace(os_type="Linux", os_subtype="RHEL", os_version="7.6", os_kernel="3.10",
                                  shutdown_delay=5.0, verify='false', driver_cfg=mock_ssh_driver_config)
    mock_config_windows = Namespace(os_type="Windows", os_subtype="Server", os_version="2019", os_kernel="18077",
                                    shutdown_delay=5.0, verify='false', driver_cfg=mock_ssh_driver_config)
    mock_config_esxi = Namespace(os_type="ESXi", os_subtype="6.7", os_version="U3", os_kernel="unknown",
                                 shutdown_delay=5.0, verify='false', driver_cfg=mock_ssh_driver_config)
    mock_config_unsupported_os = Namespace(os_type="macOS", os_subtype="X", os_version="10.15", os_kernel="19.0.0",
                                           shutdown_delay=5.0, verify='false', driver_cfg=mock_ssh_driver_config)

    @staticmethod
    def create_mock_connection(expected):
        mock_target = mock.MagicMock()
        mock_target.run.return_value = expected
        mock_target.cd = mock.MagicMock()

        cn = mock.MagicMock()
        cn.__enter__ = mock.MagicMock(return_value=mock_target)
        return cn

    @staticmethod
    def create_mock_connection_se(side_effect):
        mock_target = mock.MagicMock()
        mock_target.run = mock.MagicMock(side_effect=side_effect)
        mock_target.cd = mock.MagicMock()

        cn = mock.MagicMock()
        cn.__enter__ = mock.MagicMock(return_value=mock_target)
        return cn

    @staticmethod
    def create_mock_execute():
        excute_obj = mock.Mock()
        excute_obj.cmd_failed.return_value = False
        return excute_obj

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    def test_execute_command_pass(self, mock_pcf):
        """Test a passing SSH command"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        expected = Namespace(exited=0, stdout="mock", stderr="")
        mock_connection = self.create_mock_connection(expected)
        with mock.patch('fabric.Connection', return_value=mock_connection):
            result = os.execute("ls", 1.0)

        self.assertTrue(result.cmd_passed())
        self.assertEqual(expected.exited, result.return_code)
        self.assertEqual(expected.stdout, result.stdout)
        self.assertEqual(expected.stderr, result.stderr)
        self.assertEqual(1, mock_connection.__enter__().run.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    def test_execute_command_fail(self, mock_pcf):
        """Test a failing SSH command"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        expected = Namespace(exited=1, stdout="mock", stderr="")
        mock_connection = self.create_mock_connection(expected)
        with mock.patch('fabric.Connection', return_value=mock_connection):
            result = os.execute("ls", 1.0)

        self.assertTrue(result.cmd_failed())
        self.assertEqual(expected.exited, result.return_code)
        self.assertEqual(expected.stdout, result.stdout)
        self.assertEqual(expected.stderr, result.stderr)
        self.assertEqual(1, mock_connection.__enter__().run.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    def test_execute_timeout(self, mock_pcf):
        """Test a timed-out SSH command"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        mock_connection = self.create_mock_connection_se(CommandTimedOut(None, None))
        with mock.patch('fabric.Connection', return_value=mock_connection):
            with self.assertRaises(ValueError):
                os.execute("ls", None)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    def test_execute_command_timeout(self, mock_pcf):
        """Test a timed-out SSH command"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        mock_connection = self.create_mock_connection_se(CommandTimedOut(None, None))
        with mock.patch('fabric.Connection', return_value=mock_connection):
            with self.assertRaises(Exception):
                os.execute("ls", 1.0)

        self.assertEqual(1, mock_connection.__enter__().run.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    def test_execute_command_communication_fail(self, mock_pcf):
        """Test a command that doesn't execute at all due to an SSH issue"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        mock_connection = self.create_mock_connection_se(SSHException)
        with mock.patch('fabric.Connection', return_value=mock_connection):
            with self.assertRaises(Exception):
                os.execute("ls", 1.0)

        self.assertEqual(1, mock_connection.__enter__().run.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    def test_execute_command_unknown_fail(self, mock_pcf):
        """Test a command that doesn't execute at all due to an unknown issue"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        exceptions = [OSError, RuntimeError, ArithmeticError, ValueError, KeyError]
        for exception in exceptions:
            mock_connection = self.create_mock_connection_se(exception)
            with mock.patch('fabric.Connection', return_value=mock_connection):
                with self.assertRaises(Exception):
                    os.execute("ls", 1.0)
            self.assertEqual(1, mock_connection.__enter__().run.call_count)

        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    def test_execute_async_command_pass(self, mock_pcf):
        """Test a passing async command"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        expected = Namespace(exited=0, stdout="mock", stderr="")
        mock_connection = self.create_mock_connection(expected)
        with mock.patch('fabric.Connection', return_value=mock_connection):
            os.execute_async("ls")

        self.assertEqual(1, mock_connection.__enter__().run.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    def test_execute_async_command_fail(self, mock_pcf):
        """Test a failing async command"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        expected = Namespace(exited=1, stdout="mock", stderr="")
        mock_connection = self.create_mock_connection(expected)
        with mock.patch('fabric.Connection', return_value=mock_connection):
            with self.assertRaises(Exception):
                os.execute_async("ls")

        self.assertEqual(1, mock_connection.__enter__().run.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_windows)
    def test_execute_async_command_windows(self, mock_pcf):
        """Test an async command with Windows, unsupported right now"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        expected = Namespace(exited=1, stdout="mock", stderr="")
        mock_connection = self.create_mock_connection(expected)
        with mock.patch('fabric.Connection', return_value=mock_connection):
            os.execute = mock.Mock(return_value=self.create_mock_execute())
            os.execute_async("dir")

        self.assertEqual(0, mock_connection.__enter__().run.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_windows)
    def test_is_alive_still_booting(self, mock_pcf):
        """Test that is_alive reports False when the SUT is still booting"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        mock_connection = self.create_mock_connection(None)
        mock_connection.__enter__().open = mock.MagicMock(side_effect=NoValidConnectionsError({'0.0.0.0': 22}))
        with mock.patch('fabric.Connection', return_value=mock_connection):
            self.assertFalse(os.is_alive())

        self.assertEqual(1, mock_connection.__enter__().open.call_count)
        self.assertEqual(0, mock_connection.__enter__().close.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_windows)
    def test_is_alive_ssh_fail(self, mock_pcf):
        """Test that is_alive reports False if there is an SSH error"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        mock_connection = self.create_mock_connection(None)
        mock_connection.__enter__().open = mock.MagicMock(side_effect=SSHException())
        with mock.patch('fabric.Connection', return_value=mock_connection):
            self.assertFalse(os.is_alive())

        self.assertEqual(1, mock_connection.__enter__().open.call_count)
        self.assertEqual(0, mock_connection.__enter__().close.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_windows)
    def test_is_alive_socket_error(self, mock_pcf):
        """Test that is_alive reports False when there is a communication error"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        mock_connection = self.create_mock_connection(None)
        mock_connection.__enter__().open = mock.MagicMock(side_effect=socket.error)
        with mock.patch('fabric.Connection', return_value=mock_connection):
            self.assertFalse(os.is_alive())

        self.assertEqual(1, mock_connection.__enter__().open.call_count)
        self.assertEqual(0, mock_connection.__enter__().close.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_windows)
    def test_is_alive_generic_error(self, mock_pcf):
        """Test that is_alive re-raises exceptions if an unknown error occurs"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        mock_connection = self.create_mock_connection(None)
        mock_connection.__enter__().close = mock.MagicMock(side_effect=RuntimeError)
        with mock.patch('fabric.Connection', return_value=mock_connection):
            with self.assertRaises(RuntimeError):
                os.is_alive()

        self.assertEqual(1, mock_connection.__enter__().open.call_count)
        self.assertEqual(1, mock_connection.__enter__().close.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_windows)
    def test_is_alive_pass(self, mock_pcf):
        """Test that is_alive reports True when connection can be opened/closed successfully (no exceptions thrown)"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        mock_connection = self.create_mock_connection(mock.Mock())
        with mock.patch('fabric.Connection', return_value=mock_connection):
            self.assertTrue(os.is_alive())

        self.assertEqual(1, mock_connection.__enter__().open.call_count)
        self.assertEqual(1, mock_connection.__enter__().close.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_windows)
    @mock.patch.object(SshSutOsProvider, 'is_alive', side_effect=[False] * 10 + [True])
    def test_wait_for_os_pass(self, mock_is_alive, mock_pcf):
        """Test that waiting for the OS works"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        os.OS_POLL_INTERVAL = 0.1
        with mock.patch('fabric.Connection', return_value=self.create_mock_connection(None)):
            os.wait_for_os(10.0)

        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(11, mock_is_alive.call_count)  # Should get through all 11 is_alive values

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_windows)
    @mock.patch.object(SshSutOsProvider, 'is_alive', return_value=True)
    def test_wait_for_os_pass_immediate(self, mock_is_alive, mock_pcf):
        """Test that waiting for the OS works even when OS is already alive"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        os.OS_POLL_INTERVAL = 0.1
        with mock.patch('fabric.Connection', return_value=self.create_mock_connection(None)):
            os.wait_for_os(2.0)

        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(1, mock_is_alive.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_windows)
    @mock.patch.object(SshSutOsProvider, 'is_alive', side_effect=[False] * 10 + [True])
    def test_wait_for_os_fail(self, mock_is_alive, mock_pcf):
        """Test that wait_for_os raises an exception if the wait times out"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        os.OS_POLL_INTERVAL = 0.1
        with mock.patch('fabric.Connection', return_value=self.create_mock_connection(None)):
            with self.assertRaises(Exception):
                os.wait_for_os(0.6)

        self.assertEqual(1, mock_pcf.call_count)
        self.assertLess(mock_is_alive.call_count, 11)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_windows)
    @mock.patch.object(SshSutOsProvider, 'is_alive', side_effect=[False] * 10 + [True])
    def test_wait_for_os_type_enforcement(self, mock_is_alive, mock_pcf):
        """Test that wait_for_os enforces timeout typing"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        os.OS_POLL_INTERVAL = 0.1
        with mock.patch('fabric.Connection', return_value=self.create_mock_connection(None)):
            with self.assertRaises(ValueError):
                # noinspection PyTypeChecker
                os.wait_for_os({})  # Intentionally bad param

        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(0, mock_is_alive.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    def test_check_if_path_exists(self, mock_pcf):
        """Test a file that exists"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        expected = Namespace(exited=0, stdout="mock", stderr="")
        mock_connection = self.create_mock_connection(expected)
        with mock.patch('fabric.Connection', return_value=mock_connection):
            path_exists = os.check_if_path_exists("/my/fake/path")

        self.assertTrue(path_exists)
        self.assertEqual(1, mock_connection.__enter__().run.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    def test_check_if_path_exists_false(self, mock_pcf):
        """Test a file that doesn't exist"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        expected = Namespace(exited=1, stdout="mock", stderr="")
        mock_connection = self.create_mock_connection(expected)
        with mock.patch('fabric.Connection', return_value=mock_connection):
            path_exists = os.check_if_path_exists("/my/fake/path")

        self.assertFalse(path_exists)
        self.assertEqual(1, mock_connection.__enter__().run.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    def test_copy_local_file_to_sut(self, mock_pcf):
        """Test a file that doesn't exist"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        expected = Namespace(exited=1, stdout="mock", stderr="")
        mock_connection = self.create_mock_connection(expected)
        with mock.patch('fabric.Connection', return_value=mock_connection):
            path_exists = os.copy_local_file_to_sut("/my/fake/src_path", "my/fake/des_path")

        self.assertFalse(path_exists)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=mock_config_linux)
    def test_copy_file_from_sut_to_local(self, mock_pcf):
        """Test a file that doesn't exist"""
        os = SshSutOsProvider(self.mock_xml, logging.getLogger())  # type: SshSutOsProvider
        expected = Namespace(exited=1, stdout="mock", stderr="")
        mock_connection = self.create_mock_connection(expected)
        with mock.patch('fabric.Connection', return_value=mock_connection):
            path_exists = os.copy_file_from_sut_to_local("/my/fake/src_path", "my/fake/des_path")

        self.assertFalse(path_exists)


if __name__ == "__main__":
    unittest.main()
