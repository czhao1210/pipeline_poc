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
import binascii
import os
import re
import sys

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.dtaf_constants import Framework, OperatingSystems
from dtaf_core.lib.flash import FlashDevices
from dtaf_core.providers.flash_emulator_provider import FlashEmulatorProvider
from dtaf_core.providers.provider_factory import ProviderFactory
from dtaf_core.providers.sut_os_provider import SutOsProvider


class OsBiosIdHelper(object):
    os_cmd_strings = {
        OperatingSystems.LINUX: 'dmesg | grep "EDK II BIOS ID"',
        OperatingSystems.WINDOWS: 'wmic bios get smbiosbiosversion'
    }

    cmd_parse_strings = {
        OperatingSystems.LINUX: r"\[.+\] efi: EFI v[0-9]*.[0-9]+ by EDK II BIOS ID:(.+)$",
        OperatingSystems.WINDOWS: r"SMBIOSBIOSVersion\s+(.+)$"
    }


class FlashEmulatorExample(BaseTestCase):
    """
    Basic test case demonstrating the use of FlashProvider.

    Add the IFWI file you want to use to the working directory as IFWI.bin. This example test assumes 32MB flash and
    that the SUT is already powered-on and booted to the OS.
    This is designed to be triggered manually, and as such, is not marked as a system test for Pytest to pick up.
    """

    def __init__(self, test_log, arguments, cfg_opts):
        super(FlashEmulatorExample, self).__init__(test_log, arguments, cfg_opts)
        flash_cfg = cfg_opts.find(FlashEmulatorProvider.DEFAULT_CONFIG_PATH)
        self._emulator = ProviderFactory.create(flash_cfg, test_log)  # type: FlashEmulatorProvider
        sut_os_cfg = cfg_opts.find(SutOsProvider.DEFAULT_CONFIG_PATH)
        self._os = ProviderFactory.create(sut_os_cfg, test_log)  # type: SutOsProvider

    def get_bios_version(self):
        """
        Get the BIOS version number of the BIOS image currently programmed on the SUT.

        :return: String with the version of the BIOS.
        """
        if not self._os.is_alive():
            raise RuntimeError("The SUT should be powered on and alive before starting this test!")

        # Get the BIOS ID from the OS
        try:
            result = self._os.execute(OsBiosIdHelper.os_cmd_strings[self._os.os_type], 1.0)
        except KeyError:
            raise KeyError("This function does not currently support " + str(self._os.os_type))

        if result.cmd_failed():
            self._log.error("OS command failed! Output follows.")
            self._log.error(str(result.stderr))
            raise RuntimeError("Could not get the BIOS ID from the SUT! The OS command failed.")

        # Reduce output from OS to the BIOS ID.
        result = result.stdout.strip()
        bios_id = re.match(OsBiosIdHelper.cmd_parse_strings[self._os.os_type], result)

        # Return the BIOS ID
        if bios_id is None:
            raise RuntimeError("Could not find BIOS ID in the OS output!")
        else:
            return bios_id.group(1)

    def execute(self):
        bios_version = self.get_bios_version()
        self._log.info("The BIOS version on the SUT is: " + bios_version)

        self._log.info("Loading IFWI.bin onto the flash emulator.")
        self._log.debug("Note that the provider will stop and start the emulator automatically.")
        if not os.path.exists("IFWI.bin"):
            raise RuntimeError("IFWI.bin doesn't exist in the working directory!")
        self._emulator.flash_image("IFWI.bin", FlashDevices.PCH)

        self._log.info("Let's corrupt the new IFWI before restarting the SUT. "
                       "This section of flash was unused on CLX-AP...")
        self._log.info(
            "Before modification, 0x9B0={}".format(binascii.hexlify(self._emulator.read(0x9B0, 3, FlashDevices.PCH))))
        self._emulator.write(0x9B0, bytearray([0x0d, 0xec, 0xaf]), FlashDevices.PCH)
        self._log.info("Writing 0x0decaf into 0x9B0...")
        magic = int(binascii.hexlify(self._emulator.read(0x9B0, 3, FlashDevices.PCH)), 16)
        self._log.info("After modification, 0x9B0={}".format(hex(magic)))
        if magic != 0x0decaf:
            raise RuntimeError("Was expecting 0x0decaf after modification, but got {} instead!".format(magic))

        self._log.info("Restarting SUT.")
        self._os.reboot(400.0)

        new_bios_version = self.get_bios_version()
        self._log.info("New BIOS revision: " + new_bios_version)
        if bios_version == new_bios_version:
            self._log.warning("BIOS version did not change. If IFWI.bin is the same version as the original SUT image, "
                              "then there is no issue.")

        self._log.info("Checking that our magic number is still in the flash.")
        magic = int(binascii.hexlify(self._emulator.read(0x9B0, 3, FlashDevices.PCH)), 16)
        self._log.info("0x9B0={}".format(hex(magic)))
        result = magic == 0x0decaf
        if not result:
            self._log.error("Was expecting 0x0decaf after restart, but got {} instead!".format(magic))
        return result


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if FlashEmulatorExample.main() else Framework.TEST_RESULT_FAIL)
