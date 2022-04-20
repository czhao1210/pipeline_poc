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
import mock
import logging
import unittest
import xml.etree.ElementTree
from argparse import Namespace
from dtaf_core.lib.exceptions import DebuggerException, RegisterInconsistencyException, ReadBackException
from dtaf_core.lib.silicon import CPUID
from dtaf_core.providers.internal.xdp_silicon_debug_provider import XdpSiliconDebugProvider


class MockXdpThread(object):
    """
    Mock thread objects for unit testing.
    TODO: Investigate move to mocking the thread object directly
          However, this would require installing itpii and/or ipccli, which is less than ideal.
          This works for now.
    """

    def __init__(self):
        self.msr = mock.MagicMock()
        self.cpuid_eax = mock.MagicMock()
        self.cpuid_ebx = mock.MagicMock()
        self.cpuid_ecx = mock.MagicMock()
        self.cpuid_edx = mock.MagicMock()
        self.msr = mock.MagicMock()
        self.mem = mock.MagicMock()
        self.wbinvd = mock.MagicMock()
        self.device = Namespace(isenabled=True)

    @staticmethod
    def make_threads(num_threads):
        # type: (int) -> list
        """Return a list with num_threads mock threads."""
        return [MockXdpThread() for _ in range(0, num_threads)]


class TestXdpSiliconDebugProvider(unittest.TestCase):
    """Unit tests for XdpSiliconDebugProvider"""

    # Mock Provider configurations
    mock_xml = xml.etree.ElementTree.fromstring("<mock />")
    mock_config_itpii = Namespace(driver_cfg=Namespace(debugger_type="ITP"))
    mock_config_openipc = Namespace(driver_cfg=Namespace(debugger_type="IPC"))

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_itp_no_ipc_import(self, mock_pcf):
        """
        Ensure that provider only imports and uses the itpii library if that is what is specified in the configuration
        file. Since ipccli is not mocked, an ImportError will be raised if it is called.
        """
        mock_itpii = mock.MagicMock()
        mock_baseaccess = mock.MagicMock()
        mock_itpii.baseaccess = mock.MagicMock(return_value=mock_baseaccess)
        sys.modules['itpii'] = mock_itpii

        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            self.assertIs(mock_baseaccess, xdp.itp)

        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_itp_bad_import(self, mock_pcf):
        """
        Ensure that provider reports an error if the ITPII library is not available but is configured to use it.
        """
        sys.modules['itpii'] = None
        with self.assertRaises(ImportError):
            with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()):
                pass

        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_ipc_no_itp_import(self, mock_pcf):
        """
        Ensure that provider only imports and uses the ipccli library if that is what is specified in the configuration
        file. Since itpii is not mocked, an ImportError will be raised if it is called.
        """
        mock_ipccli = mock.MagicMock()
        mock_baseaccess = mock.MagicMock()
        mock_ipccli.baseaccess = mock.MagicMock(return_value=mock_baseaccess)
        sys.modules['ipccli'] = mock_ipccli

        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            self.assertIs(mock_baseaccess, xdp.itp)

        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_ipc_bad_import(self, mock_pcf):
        """
        Ensure that provider reports an error if the IPCCLI library is not available but is configured to use it.
        """
        sys.modules['ipccli'] = None
        with self.assertRaises(ImportError):
            with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()):
                pass

        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_is_halted_true(self, mock_pcf):
        """Ensure that provider reports True when probe reports that the SUT is halted"""
        sys.modules['itpii'] = mock.MagicMock()
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            type(xdp.itp.cv).ishalted = mock.PropertyMock(return_value=True)
            self.assertTrue(xdp.is_halted())

        self.assertEqual(1, sys.modules['itpii'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_is_halted_false(self, mock_pcf):
        """Ensure that provider reports False when probe reports that the SUT is not halted"""
        sys.modules['itpii'] = mock.MagicMock()
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            type(xdp.itp.cv).ishalted = mock.PropertyMock(return_value=False)
            self.assertFalse(xdp.is_halted())

        self.assertEqual(1, sys.modules['itpii'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_is_powered_true(self, mock_pcf):
        """Ensure that provider reports True when probe reports that the SUT is powered on"""
        sys.modules['itpii'] = mock.MagicMock()
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            type(xdp.itp.cv).targpower = mock.PropertyMock(return_value=True)
            self.assertTrue(xdp.is_powered())

        self.assertEqual(1, sys.modules['itpii'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_is_powered_false(self, mock_pcf):
        """Ensure that provider reports False when probe reports that the SUT is powered off"""
        sys.modules['itpii'] = mock.MagicMock()
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            type(xdp.itp.cv).targpower = mock.PropertyMock(return_value=False)
            self.assertFalse(xdp.is_powered())

        self.assertEqual(1, sys.modules['itpii'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=False)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_cpuid_not_halted(self, mock_pcf, mock_halt):
        """Ensure that provider raises an exception if a CPUID access is requested when the SUT is not halted"""
        sys.modules['itpii'] = mock.MagicMock()
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            with self.assertRaises(DebuggerException):
                xdp.cpuid(CPUID.EAX, 0)

        self.assertEqual(1, sys.modules['itpii'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_cpuid_invalid_register(self, mock_pcf, mock_halt):
        """Ensure that provider raises an exception if an invalid CPUID register is requested"""
        sys.modules['itpii'] = mock.MagicMock()
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            with self.assertRaises(ValueError):
                xdp.cpuid("eaz", 0)  # simulate a bad input with a realistic typo

        self.assertEqual(1, sys.modules['itpii'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'go')
    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_auto_resume(self, mock_pcf, mock_is_halted, mock_go):
        """Ensure that provider automatically resumes the system when leaving the test context"""
        sys.modules['itpii'] = mock.MagicMock()
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()):
            pass

        self.assertEqual(1, mock_go.call_count)
        self.assertEqual(1, mock_is_halted.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'go')
    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=False)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_no_auto_resume(self, mock_pcf, mock_is_halted, mock_go):
        """
        Ensure that provider doesn't try to resume the system if it is already running when leaving the test context
        """
        sys.modules['itpii'] = mock.MagicMock()
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()):
            pass

        self.assertEqual(0, mock_go.call_count)
        self.assertEqual(1, mock_is_halted.call_count)
        self.assertEqual(1, mock_pcf.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=False)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_terminate_on_exit_itp(self, mock_pcf, mock_is_halted):
        """Ensure that provider terminates ITP connection cleanly when it is in use"""
        sys.modules['itpii'] = mock.MagicMock()
        mock_terminate = mock.MagicMock()
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            xdp.itp.terminate = mock_terminate

        self.assertEqual(1, mock_is_halted.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(1, mock_terminate.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=False)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_no_terminate_on_exit_ipc(self, mock_pcf, mock_is_halted):
        """
        Ensure that provider does not try to terminate IPC connection when leaving the test context.
        The terminate function from itpii does not exist in ipccli.
        """
        sys.modules['ipccli'] = mock.MagicMock()
        mock_terminate = mock.MagicMock()
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            xdp.itp.terminate = mock_terminate

        self.assertEqual(1, mock_is_halted.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(0, mock_terminate.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_cpuid_eax_squash_pass(self, mock_pcf, mock_halt):
        """Test that CPUID_EAX returns a single result when squash is enabled"""
        sys.modules['ipccli'] = mock.MagicMock()
        cpuid_val = 0xdecaf
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(5)
            for thread in xdp.itp.threads:
                thread.cpuid_eax.return_value = cpuid_val

            # Run test
            result = xdp.cpuid(CPUID.EAX, 0x2, squash=True)

            # Check results
            self.assertEqual(cpuid_val, result)
            for thread in xdp.itp.threads:
                self.assertEqual(1, thread.cpuid_eax.call_count)
                self.assertEqual(0, thread.cpuid_ebx.call_count)
                self.assertEqual(0, thread.cpuid_ecx.call_count)
                self.assertEqual(0, thread.cpuid_edx.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_cpuid_ebx_squash_pass(self, mock_pcf, mock_halt):
        """Test that CPUID_EBX returns a single result when squash is enabled"""
        sys.modules['ipccli'] = mock.MagicMock()
        cpuid_val = 0xdecaf
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(5)
            for thread in xdp.itp.threads:
                thread.cpuid_ebx.return_value = cpuid_val

            # Run test
            result = xdp.cpuid(CPUID.EBX, 0x2, squash=True)

            # Check results
            self.assertEqual(cpuid_val, result)
            for thread in xdp.itp.threads:
                self.assertEqual(0, thread.cpuid_eax.call_count)
                self.assertEqual(1, thread.cpuid_ebx.call_count)
                self.assertEqual(0, thread.cpuid_ecx.call_count)
                self.assertEqual(0, thread.cpuid_edx.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_cpuid_ecx_squash_pass(self, mock_pcf, mock_halt):
        """Test that CPUID_ECX returns a single result when squash is enabled"""
        sys.modules['ipccli'] = mock.MagicMock()
        cpuid_val = 0xdecaf
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(5)
            for thread in xdp.itp.threads:
                thread.cpuid_ecx.return_value = cpuid_val

            # Run test
            result = xdp.cpuid(CPUID.ECX, 0x2, squash=True)

            # Check results
            self.assertEqual(cpuid_val, result)
            for thread in xdp.itp.threads:
                self.assertEqual(0, thread.cpuid_eax.call_count)
                self.assertEqual(0, thread.cpuid_ebx.call_count)
                self.assertEqual(1, thread.cpuid_ecx.call_count)
                self.assertEqual(0, thread.cpuid_edx.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_cpuid_edx_squash_pass(self, mock_pcf, mock_halt):
        """Test that CPUID_EDX returns a single result when squash is enabled"""
        sys.modules['ipccli'] = mock.MagicMock()
        cpuid_val = 0xdecaf
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(5)
            for thread in xdp.itp.threads:
                thread.cpuid_edx.return_value = cpuid_val

            # Run test
            result = xdp.cpuid(CPUID.EDX, 0x2, squash=True)

            # Check results
            self.assertEqual(cpuid_val, result)
            for thread in xdp.itp.threads:
                self.assertEqual(0, thread.cpuid_eax.call_count)
                self.assertEqual(0, thread.cpuid_ebx.call_count)
                self.assertEqual(0, thread.cpuid_ecx.call_count)
                self.assertEqual(1, thread.cpuid_edx.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_cpuid_squash_one_thread(self, mock_pcf, mock_halt):
        """Test that squash doesn't break when there is only one thread"""
        sys.modules['ipccli'] = mock.MagicMock()
        cpuid_val = 0xdecaf
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(1)
            for thread in xdp.itp.threads:
                thread.cpuid_edx.return_value = cpuid_val

            # Run test
            result = xdp.cpuid(CPUID.EDX, 0x2, squash=True)

            # Check results
            self.assertEqual(cpuid_val, result)
            for thread in xdp.itp.threads:
                self.assertEqual(0, thread.cpuid_eax.call_count)
                self.assertEqual(0, thread.cpuid_ebx.call_count)
                self.assertEqual(0, thread.cpuid_ecx.call_count)
                self.assertEqual(1, thread.cpuid_edx.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_cpuid_no_squash_one_thread(self, mock_pcf, mock_halt):
        """Test that non-squashed mode works with only one thread"""
        sys.modules['ipccli'] = mock.MagicMock()
        cpuid_val = 0xdecaf
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(1)
            for thread in xdp.itp.threads:
                thread.cpuid_edx.return_value = cpuid_val

            # Run test
            result = xdp.cpuid(CPUID.EDX, 0x2)

            # Check results
            self.assertIsInstance(result, list)
            self.assertEqual([cpuid_val], result)
            for thread in xdp.itp.threads:
                self.assertEqual(0, thread.cpuid_eax.call_count)
                self.assertEqual(0, thread.cpuid_ebx.call_count)
                self.assertEqual(0, thread.cpuid_ecx.call_count)
                self.assertEqual(1, thread.cpuid_edx.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_cpuid_squash_fail(self, mock_pcf, mock_halt):
        """Test that CPUID raises an exception if values are not the same across threads when squash is True"""
        sys.modules['ipccli'] = mock.MagicMock()
        cpuid_val_0 = 0xdecaf
        cpuid_val_1 = 0xface
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(12)
            for thread_idx in range(0, len(xdp.itp.threads)):
                xdp.itp.threads[thread_idx].cpuid_eax.return_value = cpuid_val_0 if thread_idx % 2 == 0 else cpuid_val_1

            # Run test
            with self.assertRaises(RegisterInconsistencyException):
                xdp.cpuid(CPUID.EAX, 0x2, squash=True)

            for thread in xdp.itp.threads:
                self.assertEqual(1, thread.cpuid_eax.call_count)
                self.assertEqual(0, thread.cpuid_ebx.call_count)
                self.assertEqual(0, thread.cpuid_ecx.call_count)
                self.assertEqual(0, thread.cpuid_edx.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_cpuid_eax_no_squash(self, mock_pcf, mock_halt):
        """Test that CPUID_EAX returns a list of thread values without the squash feature."""
        sys.modules['ipccli'] = mock.MagicMock()
        cpuid_val_0 = 0xdecaf
        cpuid_val_1 = 0xface
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(12)
            expected = []
            for thread_idx in range(0, len(xdp.itp.threads)):
                val = cpuid_val_0 if thread_idx % 2 == 0 else cpuid_val_1
                xdp.itp.threads[thread_idx].cpuid_eax.return_value = val
                expected.append(val)

            # Run test
            result = xdp.cpuid(CPUID.EAX, 0x2)

            self.assertEqual(expected, result)
            for thread in xdp.itp.threads:
                self.assertEqual(1, thread.cpuid_eax.call_count)
                self.assertEqual(0, thread.cpuid_ebx.call_count)
                self.assertEqual(0, thread.cpuid_ecx.call_count)
                self.assertEqual(0, thread.cpuid_edx.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_cpuid_ebx_no_squash(self, mock_pcf, mock_halt):
        """Test that CPUID_EBX returns a list of thread values without the squash feature."""
        sys.modules['ipccli'] = mock.MagicMock()
        cpuid_val_0 = 0xdecaf
        cpuid_val_1 = 0xface
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(12)
            expected = []
            for thread_idx in range(0, len(xdp.itp.threads)):
                val = cpuid_val_0 if thread_idx % 2 == 0 else cpuid_val_1
                xdp.itp.threads[thread_idx].cpuid_ebx.return_value = val
                expected.append(val)

            # Run test
            result = xdp.cpuid(CPUID.EBX, 0x2)

            self.assertEqual(expected, result)
            for thread in xdp.itp.threads:
                self.assertEqual(0, thread.cpuid_eax.call_count)
                self.assertEqual(1, thread.cpuid_ebx.call_count)
                self.assertEqual(0, thread.cpuid_ecx.call_count)
                self.assertEqual(0, thread.cpuid_edx.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_cpuid_ecx_no_squash(self, mock_pcf, mock_halt):
        """Test that CPUID_ECX returns a list of thread values without the squash feature."""
        sys.modules['ipccli'] = mock.MagicMock()
        cpuid_val_0 = 0xdecaf
        cpuid_val_1 = 0xface
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(12)
            expected = []
            for thread_idx in range(0, len(xdp.itp.threads)):
                val = cpuid_val_0 if thread_idx % 2 == 0 else cpuid_val_1
                xdp.itp.threads[thread_idx].cpuid_ecx.return_value = val
                expected.append(val)

            # Run test
            result = xdp.cpuid(CPUID.ECX, 0x2)

            self.assertEqual(expected, result)
            for thread in xdp.itp.threads:
                self.assertEqual(0, thread.cpuid_eax.call_count)
                self.assertEqual(0, thread.cpuid_ebx.call_count)
                self.assertEqual(1, thread.cpuid_ecx.call_count)
                self.assertEqual(0, thread.cpuid_edx.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_cpuid_edx_no_squash(self, mock_pcf, mock_halt):
        """Test that CPUID_EDX returns a list of thread values without the squash feature."""
        sys.modules['ipccli'] = mock.MagicMock()
        cpuid_val_0 = 0xdecaf
        cpuid_val_1 = 0xface
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(12)
            expected = []
            for thread_idx in range(0, len(xdp.itp.threads)):
                val = cpuid_val_0 if thread_idx % 2 == 0 else cpuid_val_1
                xdp.itp.threads[thread_idx].cpuid_edx.return_value = val
                expected.append(val)

            # Run test
            result = xdp.cpuid(CPUID.EDX, 0x2)

            self.assertEqual(expected, result)
            for thread in xdp.itp.threads:
                self.assertEqual(0, thread.cpuid_eax.call_count)
                self.assertEqual(0, thread.cpuid_ebx.call_count)
                self.assertEqual(0, thread.cpuid_ecx.call_count)
                self.assertEqual(1, thread.cpuid_edx.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_cpuid_cmd_fail(self, mock_pcf, mock_halt):
        """Test that CPUID doesn't mask exceptions if the command raises one."""
        sys.modules['ipccli'] = mock.MagicMock()
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(12)
            for thread_idx in range(0, len(xdp.itp.threads)):
                xdp.itp.threads[thread_idx].cpuid_edx.return_value = 0xdecaf
            xdp.itp.threads[-1].cpuid_edx.side_effect = RuntimeError  # Trigger an exception

            # Run test
            with self.assertRaises(RuntimeError):
                xdp.cpuid(CPUID.EDX, 0x2)

            for thread in xdp.itp.threads:
                self.assertEqual(0, thread.cpuid_eax.call_count)
                self.assertEqual(0, thread.cpuid_ebx.call_count)
                self.assertEqual(0, thread.cpuid_ecx.call_count)
                self.assertEqual(1, thread.cpuid_edx.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_cpuid_cmd_no_active_threads(self, mock_pcf, mock_halt):
        """Test that CPUID doesn't mask exceptions if the command raises one."""
        sys.modules['ipccli'] = mock.MagicMock()
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(12)
            for thread_idx in range(0, len(xdp.itp.threads)):
                xdp.itp.threads[thread_idx].cpuid_edx.return_value = 0xdecaf
                xdp.itp.threads[thread_idx].device.isenabled = False

            # Run test
            with self.assertRaises(DebuggerException):
                xdp.cpuid(CPUID.EDX, 0x2)

            for thread in xdp.itp.threads:
                self.assertEqual(0, thread.cpuid_eax.call_count)
                self.assertEqual(0, thread.cpuid_ebx.call_count)
                self.assertEqual(0, thread.cpuid_ecx.call_count)
                self.assertEqual(0, thread.cpuid_edx.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_msr_read_squash_pass(self, mock_pcf, mock_halt):
        """Test that MSR_READ returns a single result when squash is enabled"""
        sys.modules['ipccli'] = mock.MagicMock()
        msr_val = 0xface
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            for thread in xdp.itp.threads:
                thread.msr.return_value = msr_val

            # Run test
            result = xdp.msr_read(0x13a, squash=True)

            # Check results
            self.assertEqual(msr_val, result)
            for thread in xdp.itp.threads:
                self.assertEqual(1, thread.msr.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_msr_read_squash_fail(self, mock_pcf, mock_halt):
        """Test that MSR_READ raises an exception when squash is enabled but values are not consistent"""
        sys.modules['ipccli'] = mock.MagicMock()
        msr_val_0 = 0xface
        msr_val_1 = 0xdecaf
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            for thread_idx in range(0, len(xdp.itp.threads)):
                xdp.itp.threads[thread_idx].msr.return_value = msr_val_0 if thread_idx % 2 == 0 else msr_val_1

            # Run test
            with self.assertRaises(RegisterInconsistencyException):
                xdp.msr_read(0x13a, squash=True)

            # Check results
            for thread in xdp.itp.threads:
                self.assertEqual(1, thread.msr.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_msr_read_single_thread(self, mock_pcf, mock_halt):
        """Test MSR_READ with one thread"""
        sys.modules['ipccli'] = mock.MagicMock()
        msr_val = 0xface
        msr_val_check = 0xdeadbeef
        checked_idx = 10
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            for thread in xdp.itp.threads:
                thread.msr.return_value = msr_val
            xdp.itp.threads[checked_idx].msr.return_value = msr_val_check

            # Run test
            result = xdp.msr_read(0x13a, thread=10, squash=True)

            # Check results
            self.assertEqual(msr_val_check, result)
            self.assertEqual(1, xdp.itp.threads[checked_idx].msr.call_count)
            for thread_idx in range(0, len(xdp.itp.threads)):
                if thread_idx == checked_idx:
                    continue
                self.assertEqual(0, xdp.itp.threads[thread_idx].msr.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_msr_read_all_no_squash(self, mock_pcf, mock_halt):
        """Test MSR_READ with all threads. Return type should be list without squash."""
        sys.modules['ipccli'] = mock.MagicMock()
        msr_val_0 = 0xface
        msr_val_1 = 0xdecaf
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            expected = []
            for thread_idx in range(0, len(xdp.itp.threads)):
                val = msr_val_0 if thread_idx % 2 == 0 else msr_val_1
                xdp.itp.threads[thread_idx].msr.return_value = val
                expected.append(val)

            # Run test
            result = xdp.msr_read(0x13a)

            # Check results
            self.assertEqual(expected, result)
            for thread_idx in range(0, len(xdp.itp.threads)):
                self.assertEqual(1, xdp.itp.threads[thread_idx].msr.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_msr_read_cmd_fail(self, mock_pcf, mock_halt):
        """Test MSR_READ to ensure that it does not mask exceptions if the command fails."""
        sys.modules['ipccli'] = mock.MagicMock()
        msr_val = 0xdecaf
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            for thread_idx in range(0, len(xdp.itp.threads)):
                xdp.itp.threads[thread_idx].msr.return_value = msr_val
            xdp.itp.threads[-1].msr.side_effect = RuntimeError

            # Run test
            with self.assertRaises(RuntimeError):
                xdp.msr_read(0x13a)

            # Check results
            for thread_idx in range(0, len(xdp.itp.threads)):
                self.assertEqual(1, xdp.itp.threads[thread_idx].msr.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_msr_read_cmd_no_active_threads(self, mock_pcf, mock_halt):
        """Test that msr_read raises an exception if there are no active threads"""
        sys.modules['ipccli'] = mock.MagicMock()
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            for thread_idx in range(0, len(xdp.itp.threads)):
                xdp.itp.threads[thread_idx].msr.return_value = 0xdecaf
                xdp.itp.threads[thread_idx].device.isenabled = False

            # Run test
            with self.assertRaises(DebuggerException):
                xdp.msr_read(0x13a)

            for thread in xdp.itp.threads:
                self.assertEqual(0, thread.msr.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_msr_read_cmd_inactive_thread(self, mock_pcf, mock_halt):
        """Test that msr_read raises an exception if specified thread is inactive"""
        sys.modules['ipccli'] = mock.MagicMock()
        test_idx = 15
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            for thread_idx in range(0, len(xdp.itp.threads)):
                xdp.itp.threads[thread_idx].msr.return_value = 0xdecaf
            xdp.itp.threads[test_idx].device.isenabled = False

            # Run test
            with self.assertRaises(DebuggerException):
                xdp.msr_read(0x13a, thread=test_idx)

            for thread in xdp.itp.threads:
                self.assertEqual(0, thread.msr.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_msr_write_all_threads(self, mock_pcf, mock_halt):
        """Test that msr_write will write to all threads"""
        sys.modules['ipccli'] = mock.MagicMock()
        test_val = 0xdecaf
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            for thread in xdp.itp.threads:
                thread.msr.return_value = test_val

            # Run test
            xdp.msr_write(0x6, test_val)

            # Check results
            self.assertEqual(1, xdp.itp.msr.call_count)
            for thread in xdp.itp.threads:
                self.assertEqual(1, thread.msr.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(3, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_msr_write_one_thread(self, mock_pcf, mock_halt):
        """Test that msr_write will only write to one thread when requested"""
        sys.modules['ipccli'] = mock.MagicMock()
        test_val_0 = 0xdecaf
        test_val_1 = 0xface
        test_idx = 16
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            for thread in xdp.itp.threads:
                thread.msr.return_value = test_val_0
            xdp.itp.threads[test_idx].msr.return_value = test_val_1

            # Run test
            xdp.msr_write(0x6, test_val_1, thread=test_idx)

            # Check results
            self.assertEqual(2, xdp.itp.threads[test_idx].msr.call_count)
            for thread_idx in range(0, len(xdp.itp.threads)):
                if thread_idx == test_idx:
                    continue
                self.assertEqual(0, thread.msr.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(3, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_msr_write_readback_fail_multiple_threads_one_fail(self, mock_pcf, mock_halt):
        """Test that msr_write will detect write issues on one thread if user did not bypass readback"""
        sys.modules['ipccli'] = mock.MagicMock()
        test_val = 0xdecaf
        fail_val = 0xface
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            for thread in xdp.itp.threads:
                thread.msr.return_value = test_val
            xdp.itp.threads[-1].msr.return_value = fail_val

            # Run test
            with self.assertRaises(ReadBackException):
                xdp.msr_write(0x6, test_val)

            # Check results
            self.assertEqual(1, xdp.itp.msr.call_count)
            for thread in xdp.itp.threads:
                self.assertEqual(1, thread.msr.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(3, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_msr_write_readback_fail_multiple_threads_all_fail(self, mock_pcf, mock_halt):
        """Test that msr_write will detect write issues on all threads if user did not bypass readback"""
        sys.modules['ipccli'] = mock.MagicMock()
        test_val = 0xdecaf
        fail_val = 0xface
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            for thread in xdp.itp.threads:
                thread.msr.return_value = fail_val

            # Run test
            with self.assertRaises(ReadBackException):
                xdp.msr_write(0x6, test_val)

            # Check results
            self.assertEqual(1, xdp.itp.msr.call_count)
            for thread in xdp.itp.threads:
                self.assertEqual(1, thread.msr.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(3, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_msr_write_readback_fail_one_thread(self, mock_pcf, mock_halt):
        """Test that msr_write will detect write issues if user did not bypass readback for one thread"""
        sys.modules['ipccli'] = mock.MagicMock()
        test_val = 0xdecaf
        fail_val = 0xface
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            for thread in xdp.itp.threads:
                thread.msr.return_value = test_val
            xdp.itp.threads[-1].msr.return_value = fail_val

            # Run test
            with self.assertRaises(ReadBackException):
                xdp.msr_write(0x6, test_val)

            # Check results
            self.assertEqual(1, xdp.itp.msr.call_count)
            for thread in xdp.itp.threads:
                self.assertEqual(1, thread.msr.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(3, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_msr_write_cmd_fail(self, mock_pcf, mock_halt):
        """Test that msr_write will not mask exceptions if the command fails"""
        sys.modules['ipccli'] = mock.MagicMock()
        test_val = 0xdecaf
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            for thread in xdp.itp.threads:
                thread.msr.return_value = test_val
            xdp.itp.msr.side_effect = RuntimeError

            # Run test
            with self.assertRaises(RuntimeError):
                xdp.msr_write(0x6, test_val)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_mem_read_first_thread(self, mock_pcf, mock_halt):
        """Test that mem read works when user doesn't specify a thread to use"""
        sys.modules['ipccli'] = mock.MagicMock()
        test_mem_val = 0xdeadbeef
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            for thread in xdp.itp.threads:
                thread.mem.return_value = test_mem_val

            # Run test
            result = xdp.mem_read("0x1000p", 8)

            # Check results
            self.assertEqual(1, xdp.itp.threads[0].mem.call_count)
            self.assertEqual(test_mem_val, result)
            for thread_idx in range(1, len(xdp.itp.threads)):
                self.assertEqual(0, xdp.itp.threads[thread_idx].mem.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_mem_read_specific_thread(self, mock_pcf, mock_halt):
        """Test that mem read works when user specifies a specific thread to use"""
        sys.modules['ipccli'] = mock.MagicMock()
        test_mem_val = 0xdeadbeef
        test_idx = 5
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            for thread in xdp.itp.threads:
                thread.mem.return_value = test_mem_val

            # Run test
            result = xdp.mem_read("0x1000p", 8, thread_index=test_idx)

            # Check results
            self.assertEqual(1, xdp.itp.threads[test_idx].mem.call_count)
            self.assertEqual(test_mem_val, result)
            for thread_idx in range(0, len(xdp.itp.threads)):
                if thread_idx == test_idx:
                    continue
                self.assertEqual(0, xdp.itp.threads[thread_idx].mem.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_mem_read_cmd_fail(self, mock_pcf, mock_halt):
        """Test that mem read doesn't mask exceptions if the command fails"""
        sys.modules['ipccli'] = mock.MagicMock()
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            xdp.itp.threads[0].mem.side_effect = RuntimeError

            # Run test
            with self.assertRaises(RuntimeError):
                xdp.mem_read("0x1000p", 8)

            # Check results
            self.assertEqual(1, xdp.itp.threads[0].mem.call_count)
            for thread_idx in range(1, len(xdp.itp.threads)):
                self.assertEqual(0, xdp.itp.threads[thread_idx].mem.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_mem_read_inactive_thread(self, mock_pcf, mock_halt):
        """Test that mem read raises an exception if an inactive thread is specified"""
        sys.modules['ipccli'] = mock.MagicMock()
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            xdp.itp.threads[0].device.isenabled = False

            # Run test
            with self.assertRaises(DebuggerException):
                xdp.mem_read("0x1000p", 8, thread_index=0)

            # Check results
            for thread in xdp.itp.threads:
                self.assertEqual(0, thread.mem.call_count)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_openipc)
    def test_mem_read_empty_response(self, mock_pcf, mock_halt):
        """Test that mem read raises an exception if response from itpii/ipccli is empty"""
        sys.modules['ipccli'] = mock.MagicMock()
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            for thread in xdp.itp.threads:
                thread.mem.return_value = None

            # Run test
            with self.assertRaises(TypeError):
                xdp.mem_read("0x1000p", 8, thread_index=0)

        self.assertEqual(1, sys.modules['ipccli'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_mem_write_first_thread(self, mock_pcf, mock_halt):
        """Test that mem write works when no thread is specified"""
        sys.modules['itpii'] = mock.MagicMock()
        test_mem_val = 0xdecaf
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            xdp.itp.threads[0].mem.return_value = test_mem_val

            # Run test
            xdp.mem_write("0x100p", 8, test_mem_val)

            # Check results
            self.assertEqual(2, xdp.itp.threads[0].mem.call_count)

        self.assertEqual(1, sys.modules['itpii'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(4, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_mem_write_specific_thread(self, mock_pcf, mock_halt):
        """Test that mem write works on specific threads"""
        sys.modules['itpii'] = mock.MagicMock()
        test_mem_val = 0xdecaf
        test_idx = 19
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            xdp.itp.threads[test_idx].mem.return_value = test_mem_val

            # Run test
            xdp.mem_write("0x100p", 8, test_mem_val, thread_index=test_idx)

            # Check results
            self.assertEqual(2, xdp.itp.threads[test_idx].mem.call_count)
            for thread_idx in range(0, len(xdp.itp.threads)):
                if thread_idx == test_idx:
                    continue
                self.assertEqual(0, xdp.itp.threads[thread_idx].mem.call_count)

        self.assertEqual(1, sys.modules['itpii'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(4, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_mem_write_readback_fail(self, mock_pcf, mock_halt):
        """Test that an exception is raised if readback check fails"""
        sys.modules['itpii'] = mock.MagicMock()
        test_mem_val = 0xdecaf
        test_mem_val_return = 0xdeadbeef
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            xdp.itp.threads[0].mem.return_value = test_mem_val_return

            # Run test
            with self.assertRaises(ReadBackException):
                xdp.mem_write("0x100p", 8, test_mem_val)

            # Check results
            self.assertEqual(2, xdp.itp.threads[0].mem.call_count)
            for thread_idx in range(1, len(xdp.itp.threads)):
                self.assertEqual(0, xdp.itp.threads[thread_idx].mem.call_count)

        self.assertEqual(1, sys.modules['itpii'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(4, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_mem_write_readback_bypass(self, mock_pcf, mock_halt):
        """Test that the readback check can be bypassed"""
        sys.modules['itpii'] = mock.MagicMock()
        test_mem_val = 0xdecaf
        test_mem_val_return = 0xdeadbeef
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            xdp.itp.threads[0].mem.return_value = test_mem_val_return

            # Run test
            xdp.mem_write("0x100p", 8, test_mem_val, no_readback=True)

            # Check results
            self.assertEqual(1, xdp.itp.threads[0].mem.call_count)
            for thread_idx in range(1, len(xdp.itp.threads)):
                self.assertEqual(0, xdp.itp.threads[thread_idx].mem.call_count)

        self.assertEqual(1, sys.modules['itpii'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(3, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_mem_write_cmd_fail(self, mock_pcf, mock_halt):
        """Test that mem write doesn't mask exceptions when the command fails"""
        sys.modules['itpii'] = mock.MagicMock()
        test_mem_val = 0xdecaf
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            xdp.itp.threads[0].mem.side_effect = RuntimeError

            # Run test
            with self.assertRaises(RuntimeError):
                xdp.mem_write("0x100p", 8, test_mem_val)

            # Check results
            self.assertEqual(1, xdp.itp.threads[0].mem.call_count)
            for thread_idx in range(1, len(xdp.itp.threads)):
                self.assertEqual(0, xdp.itp.threads[thread_idx].mem.call_count)

        self.assertEqual(1, sys.modules['itpii'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_mem_write_inactive_thread(self, mock_pcf, mock_halt):
        """Test that exception is raised if an inactive thread is targeted for mem write"""
        sys.modules['itpii'] = mock.MagicMock()
        test_val = 0xface
        test_idx = 23
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            xdp.itp.threads[test_idx].device.isenabled = False

            # Run test
            with self.assertRaises(DebuggerException):
                xdp.mem_write("0x100p", 8, test_val, thread_index=test_idx)

            # Check results
            for thread in xdp.itp.threads:
                self.assertEqual(0, thread.mem.call_count)

        self.assertEqual(1, sys.modules['itpii'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_flush_cache(self, mock_pcf, mock_halt):
        """Test that flush cache is called"""
        sys.modules['itpii'] = mock.MagicMock()
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)

            # Run test
            xdp.flush_cache()

            # Check results
            self.assertEqual(1, xdp.itp.threads[0].wbinvd.call_count)
            for thread_idx in range(1, len(xdp.itp.threads)):
                self.assertEqual(0, xdp.itp.threads[thread_idx].wbinvd.call_count)

        self.assertEqual(1, sys.modules['itpii'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_flush_cache_specific_thread(self, mock_pcf, mock_halt):
        """Test that flush cache is called on a specific thread"""
        sys.modules['itpii'] = mock.MagicMock()
        test_idx = 12
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)

            # Run test
            xdp.flush_cache(thread_index=test_idx)

            # Check results
            self.assertEqual(1, xdp.itp.threads[test_idx].wbinvd.call_count)
            for thread_idx in range(0, len(xdp.itp.threads)):
                if thread_idx == test_idx:
                    continue
                self.assertEqual(0, xdp.itp.threads[thread_idx].wbinvd.call_count)

        self.assertEqual(1, sys.modules['itpii'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_flush_cache_inactive_thread(self, mock_pcf, mock_halt):
        """Test that an exception is raised if cache flush is attempted on an inactive thread"""
        sys.modules['itpii'] = mock.MagicMock()
        test_idx = 12
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)
            xdp.itp.threads[test_idx].device.isenabled = False

            # Run test
            with self.assertRaises(DebuggerException):
                xdp.flush_cache(thread_index=test_idx)

            # Check results
            for thread in xdp.itp.threads:
                self.assertEqual(0, thread.wbinvd.call_count)

        self.assertEqual(1, sys.modules['itpii'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(2, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_get_first_active_thread_first_active(self, mock_pcf, mock_halt):
        """Test that get first active thread works when first thread is active"""
        sys.modules['itpii'] = mock.MagicMock()
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(24)

            # Run test
            result = xdp._get_first_active_thread()
            self.assertIs(xdp.itp.threads[0], result)

        self.assertEqual(1, sys.modules['itpii'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(1, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_get_first_active_thread_middle_active(self, mock_pcf, mock_halt):
        """Test that get first active thread works when it is in the middle"""
        sys.modules['itpii'] = mock.MagicMock()
        test_idx = 50
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(100)
            for thread in xdp.itp.threads[:test_idx]:
                thread.device.isenabled = False

            # Run test
            result = xdp._get_first_active_thread()
            self.assertIs(xdp.itp.threads[test_idx], result)

        self.assertEqual(1, sys.modules['itpii'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(1, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_get_first_active_thread_last_active(self, mock_pcf, mock_halt):
        """Test that get first active thread works when only the last thread is active"""
        sys.modules['itpii'] = mock.MagicMock()
        test_idx = 99
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(100)
            for thread in xdp.itp.threads[:test_idx]:
                thread.device.isenabled = False

            # Run test
            result = xdp._get_first_active_thread()
            self.assertIs(xdp.itp.threads[test_idx], result)
        self.assertEqual(1, sys.modules['itpii'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(1, mock_halt.call_count)

    @mock.patch.object(XdpSiliconDebugProvider, 'is_halted', return_value=True)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config_itpii)
    def test_get_first_active_thread_no_result(self, mock_pcf, mock_halt):
        """Test that an exception is raised when no threads are active"""
        sys.modules['itpii'] = mock.MagicMock()
        test_idx = 99
        with XdpSiliconDebugProvider(self.mock_xml, logging.getLogger()) as xdp:
            # Set up mock threads
            xdp.itp.threads = MockXdpThread.make_threads(100)
            for thread in xdp.itp.threads:
                thread.device.isenabled = False

            # Run test
            with self.assertRaises(DebuggerException):
                result = xdp._get_first_active_thread()

        self.assertEqual(1, sys.modules['itpii'].baseaccess.call_count)
        self.assertEqual(1, mock_pcf.call_count)
        self.assertEqual(1, mock_halt.call_count)


if __name__ == "__main__":
    unittest.main()
