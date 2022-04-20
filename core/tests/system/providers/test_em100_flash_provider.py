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
import random
import time
import unittest
import os

import pytest
from dtaf_core.lib.base_system_test import BaseSystemTest
from dtaf_core.lib.exceptions import FlashProgrammerException
from dtaf_core.lib.flash import FlashDevices
from dtaf_core.providers.internal.em100_flash_provider import Em100FlashProvider


@pytest.mark.em100
class Em100FlashProviderSystemTests(BaseSystemTest):
    """Live system tests for Em100FlashProvider"""
    # obj: Em100FlashProvider  # Uncomment this line for IDE type hinting (not supported in Python2)

    CLASS_UNDER_TEST = Em100FlashProvider

    def test_byte_read(self):
        for address in [0x0, 0x1, 0x10, 0x5342, 0xFFFEA4, 0x1FFFFFE, 0x1FFFFFF]:
            val = self.obj.read(address, 1, FlashDevices.PCH)
            self.assertEqual(1, len(val), "Read from address {} didn't succeed!".format(hex(address)))

    def test_byte_read_stress(self):
        for address in [random.randint(0x0, 0x1FFFFFF) for _ in range(0, 30)]:
            val = self.obj.read(address, 1, FlashDevices.PCH)
            self.assertEqual(1, len(val), "Read from address {} didn't succeed!".format(hex(address)))

    def test_range_read(self):
        for address in [0x0, 0x1FFFFF0, 0x100, 0x54320]:
            val = self.obj.read(address, 0x10, FlashDevices.PCH)
            self.assertEqual(0x10, len(val), "Range read from address {} didn't succeed!".format(hex(address)))

    @unittest.skip
    @pytest.mark.skip("EM100Pro software randomly fails on some addresses, even if reading less than 16 bytes")
    def test_range_read_stress(self):
        for address in [random.randrange(0x0, 0x1FFFFF0) for _ in range(0, 30)]:
            num_bytes = random.randint(0x2, 0xF)
            val = self.obj.read(address, num_bytes, FlashDevices.PCH)
            self.assertEqual(num_bytes, len(val))

    def test_read_large_amounts(self):
        full_flash = self.obj.read(0x0, 0x2000000, FlashDevices.PCH)
        self.assertEqual(0x2000000, len(full_flash))

    @unittest.skip
    @pytest.mark.skip("Need to determine how big the chip is")
    def test_read_past_end(self):
        with self.assertRaises(FlashProgrammerException):
            self.obj.read(0x2000000, 1, FlashDevices.PCH)

    @unittest.skip
    @pytest.mark.skip("Need to determine how big the chip is")
    def test_read_overflow_past_end(self):
        with self.assertRaises(ValueError):
            self.obj.read(0x1FFFFF0, 0x20, FlashDevices.PCH)

    def test_invalid_address(self):
        with self.assertRaises(ValueError):
            self.obj.read(-1, 20, FlashDevices.PCH)

    def test_invalid_length(self):
        with self.assertRaises(ValueError):
            self.obj.read(0x1000, -20, FlashDevices.PCH)

    def test_byte_write(self):
        for address in [0x0, 0x1, 0x10, 0x5342, 0xFFFEA4, 0x1FFFFFE, 0x1FFFFFF]:
            old_val = self.obj.read(address, 1, FlashDevices.PCH)
            new_val = bytearray([random.randint(0x00, 0xFF)])
            self.obj.write(address, new_val, FlashDevices.PCH)
            read_back = self.obj.read(address, 1, FlashDevices.PCH)
            self.assertEqual(new_val, read_back)
            self.obj.write(address, old_val, FlashDevices.PCH)
            self.assertEqual(old_val, self.obj.read(address, 1, FlashDevices.PCH))

    def test_byte_write_stress(self):
        for address in [random.randint(0x0, 0x1FFFFFF) for _ in range(0, 5)]:
            old_val = self.obj.read(address, 1, FlashDevices.PCH)
            new_val = bytearray([random.randint(0x00, 0xFF)])
            self.obj.write(address, new_val, FlashDevices.PCH)
            read_back = self.obj.read(address, 1, FlashDevices.PCH)
            self.assertEqual(new_val, read_back)
            self.obj.write(address, old_val, FlashDevices.PCH)
            self.assertEqual(old_val, self.obj.read(address, 1, FlashDevices.PCH))

    def test_range_write(self):
        for address in [0x0, 0x1FFFFF0, 0x100, 0x54320]:
            orig_val = self.obj.read(address, 0x10, FlashDevices.PCH)
            new_val = bytearray([random.randint(0x00, 0xFF) for _ in range(0, 16)])
            self.obj.write(address, new_val, FlashDevices.PCH)
            read_back = self.obj.read(address, 0x10, FlashDevices.PCH)
            self.assertNotEqual(orig_val, read_back)
            self.assertEqual(new_val, read_back)
            self.obj.write(address, orig_val, FlashDevices.PCH)
            self.assertEqual(orig_val, self.obj.read(address, 0x10, FlashDevices.PCH))

    def test_range_write_stress(self):
        for address in [random.randrange(0x0, 0x1FFFFF0) for _ in range(0, 5)]:
            orig_val = self.obj.read(address, 0x10, FlashDevices.PCH)
            new_val = bytearray([random.randint(0x00, 0xFF) for _ in range(0, 16)])
            self.obj.write(address, new_val, FlashDevices.PCH)
            read_back = self.obj.read(address, 0x10, FlashDevices.PCH)
            self.assertNotEqual(orig_val, read_back)
            self.assertEqual(new_val, read_back)
            self.obj.write(address, orig_val, FlashDevices.PCH)
            self.assertEqual(orig_val, self.obj.read(address, 0x10, FlashDevices.PCH))

    @unittest.skip
    @pytest.mark.skip("Need a way to determine how big the flash image is")
    def test_flash_erase_and_restore(self):
        full_flash = self.obj.read(0x0, 0x2000000, FlashDevices.PCH)
        bad_data = bytearray([random.randint(0x00, 0xFF) for _ in range(0x0, 0x2000000)])
        self.obj.write(0x0, bad_data, FlashDevices.PCH)
        read_back = self.obj.read(0x0, 0x2000000, FlashDevices.PCH)
        self.assertNotEqual(full_flash, read_back)
        self.assertEqual(bad_data, read_back)
        self.obj.write(0x0, full_flash, FlashDevices.PCH)
        self.assertEqual(full_flash, self.obj.read(0x0, 0x2000000, FlashDevices.PCH))

    @unittest.skip
    @pytest.mark.skip("Need a way to determine how big the flash image is")
    def test_write_past_end(self):
        with self.assertRaises(FlashProgrammerException):
            self.obj.write(0x2000000, bytearray([128]), FlashDevices.PCH)

    @unittest.skip
    @pytest.mark.skip("Need to determine how big the flash image is")
    def test_write_overflow_past_end(self):
        with self.assertRaises(ValueError):
            self.obj.write(0x1FFFFF0, bytearray([random.randint(0x00, 0xFF) for _ in range(0x0, 0x20)]),
                           FlashDevices.PCH)

    def test_write_invalid_address(self):
        with self.assertRaises(ValueError):
            self.obj.write(-1, bytearray([64]), FlashDevices.PCH)

    def test_write_invalid_value(self):
        with self.assertRaises(ValueError):
            # noinspection PyTypeChecker
            self.obj.write(0x100, "0xFFFA3581943", FlashDevices.PCH)

    def test_multiple_devices(self):
        if len(self.obj.device_mapping) < 2:
            self.skipTest("Only one device available! Retry with both PCH and BMC emulators available!")
        # read a value from each emulator
        pch_data = self.obj.read(0x0, 0x6, FlashDevices.PCH)
        bmc_data = self.obj.read(0x0, 0xA, FlashDevices.BMC)

        self.assertNotEqual(pch_data, bmc_data, "PCH and BMC returned same value! This is most likely a failure!")

        # write a value into each emulator
        pch_magic = bytearray(os.urandom(0x6))
        bmc_magic = bytearray(os.urandom(0xA))
        self.obj.write(0x0, pch_magic, FlashDevices.PCH)
        self.obj.write(0x0, bmc_magic, FlashDevices.BMC)

        time.sleep(2.0)
        # read back the values written
        try:
            read_back_pch = self.obj.read(0x0, 0x6, FlashDevices.PCH)
            read_back_bmc = self.obj.read(0x0, 0xA, FlashDevices.BMC)
            self.assertEqual(pch_magic, read_back_pch)
            self.assertEqual(bmc_magic, read_back_bmc)
            self.assertNotEqual(read_back_pch, read_back_bmc)

        # (attempt to) restore original values
        finally:
            self.obj.write(0x0, pch_data, FlashDevices.PCH)
            self.obj.write(0x0, bmc_data, FlashDevices.BMC)

        read_back_pch = self.obj.read(0x0, 0x6, FlashDevices.PCH)
        read_back_bmc = self.obj.read(0x0, 0xA, FlashDevices.BMC)
        self.assertEqual(pch_data, read_back_pch)
        self.assertEqual(bmc_data, read_back_bmc)
        self.assertNotEqual(read_back_pch, read_back_bmc)

    def test_start_stop(self):
        with self.assertRaises(NotImplementedError):
            self.obj.stop(FlashDevices.PCH)

        with self.assertRaises(NotImplementedError):
            self.obj.start(FlashDevices.BMC)


if __name__ == "__main__":
    unittest.main()
