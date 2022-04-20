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
import mmap
import os
import platform
import subprocess

import six
from dtaf_core.lib.dtaf_constants import OperatingSystems
from dtaf_core.lib.exceptions import FlashEmulatorException, FlashProgrammerException
from dtaf_core.providers.flash_emulator_provider import FlashEmulatorProvider


class Em100FlashEmulatorProvider(FlashEmulatorProvider):
    """
    Class that interfaces with Dediprog EM100 Flash emulators.

    For best results, ensure that the EM100Pro GUI is closed when running automation. The GUI can interfere with the CLI
    and force the emulator/driver into a state which requires a host restart.

    Ensure that the following items are fully up-to-date. Older versions of Dediprog software will not work properly:
    1 - Dediprog EM100Pro/-G2 host software
    2 - Dediprog EM100Pro/-G2 host USB driver
    3 - Dediprog EM100Pro/-G2 FPGA Firmware
    """

    SMUCMD = "smucmd.exe"
    DEVICE = "--device"
    CHIP = "--set"
    DP_START = "--start"
    DP_STOP = "--stop"
    DP_FLASH = "--download"
    DP_VERIFY = "--verify"
    DP_ADDRESS = "--addr"
    DP_READ = "--read"
    DP_LENGTH = "--length"

    @classmethod
    def _disable_multi_chip(cls, device_mapping):
        # TODO: Remove this once multiple emulator per device functionality is tested!
        for device in device_mapping:
            if len(device_mapping[device][1]) != 1:
                raise NotImplementedError("Multiple emulators per device is not yet tested!")

    def __init__(self, cfg_opts, log):
        super(Em100FlashEmulatorProvider, self).__init__(cfg_opts, log)
        if platform.system() != OperatingSystems.WINDOWS:
            raise RuntimeError("Dediprog EM100Pro software can only run on Windows hosts!")

        # Get active devices from the config file
        # Format: { "Device (PCH, BMC, etc)": ("Chip type", ["List", "Of", "Emulators"]) }
        self.device_mapping = self._config_model.driver_cfg.chip_config
        self.base_cmd = self._config_model.driver_cfg.cli_path + self.SMUCMD

        # TODO: Test multi-emulator per device support - disabled for now.
        self._disable_multi_chip(self.device_mapping)

    def _try_emulator_recovery(self, usb_port, chip):
        self._log.error("Attempting to restart the flash emulator...")
        try:
            subprocess.check_output([self.base_cmd,
                                     self.DEVICE, str(usb_port),
                                     self.CHIP, chip,
                                     self.DP_START], stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError:
            self._log.error("Flash emulator may not have been restarted properly!")

    def start(self, target):
        target_device = self.device_mapping[target]
        for emulator in target_device[1]:
            self._start(emulator, target_device[0])

    def _start(self, usb_port, chip):
        try:
            subprocess.check_output([self.base_cmd,
                                     self.DEVICE, str(usb_port),
                                     self.CHIP, chip,
                                     self.DP_START], shell=True)
        except subprocess.CalledProcessError as e:
            self._log.exception("Start failed! Process output: {}".format(e.output))
            raise FlashEmulatorException("Failed to start the EM100 attached to USB port {}".format(usb_port))

    def stop(self, target):
        target_device = self.device_mapping[target]
        for emulator in target_device[1]:
            self._stop(emulator, target_device[0])

    def _stop(self, usb_port, chip):
        try:
            subprocess.check_output([self.base_cmd,
                                     self.DEVICE, str(usb_port),
                                     self.CHIP, chip,
                                     self.DP_STOP], stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            self._log.exception("Stop failed! Process output: {}".format(e.output))
            raise FlashEmulatorException("Failed to stop the EM100 attached to USB port {}".format(usb_port))

    def flash_image(self, path, target):
        target_device = self.device_mapping[target]
        for emulator in target_device[1]:
            self._flash_image(path, emulator, target_device[0])

    def _flash_image(self, path, usb_port, chip):
        self._log.debug("Flashing image {} to EM100 on USB port {}".format(path, usb_port))
        try:
            subprocess.check_output([self.base_cmd,
                                     self.DEVICE, str(usb_port),
                                     self.CHIP, chip,
                                     self.DP_STOP,
                                     self.DP_FLASH, path,
                                     self.DP_VERIFY,
                                     self.DP_START], stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            self._log.exception("Image flash failed! Process output: {}".format(e.output))
            self._try_emulator_recovery(usb_port, chip)
            raise FlashProgrammerException("Failed to flash the EM100 attached to USB port {}".format(usb_port))

    def read(self, address, length, target):
        target_device = self.device_mapping[target]
        results = []
        for emulator in target_device[1]:
            results.append(self._read(address, length, emulator, target_device[0]))

        if results.count(results[0]) != len(results):
            raise FlashProgrammerException("Not all emulators had a consistent value! Got: {}".format(results))
        return results[0]

    def _read(self, address, length, usb_port, chip):
        temp_file = "read.bin"
        try:
            # Sanity check inputs
            if address < 0 or length < 0:
                raise ValueError("Address and length must be integers >= 0! address = {} length = {}"
                                 .format(hex(address), length))
            if length > 0xF:
                self._log.warning("Some addresses cause the EM100 software to crash when reading more than 15 bytes "
                                  "at a time.")

            # Execute read command to dump flash[address, address + length] to a binary file.
            try:
                subprocess.check_output([self.base_cmd,
                                         self.DEVICE, str(usb_port),
                                         self.CHIP, chip,
                                         self.DP_STOP,
                                         self.DP_READ, temp_file,
                                         self.DP_LENGTH, str(hex(length)),
                                         self.DP_ADDRESS, str(hex(address)),
                                         self.DP_START], stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError as e:
                self._log.error("Read from emulator failed! Output: {}".format(e.output))
                self._try_emulator_recovery(usb_port, chip)
                raise FlashProgrammerException("Unable to read data from the EM100 on USB port {}! "
                                               "Ensure that address+length does not go beyond the end of the flash! "
                                               "Address = {} Length = {}".format(usb_port, hex(address), hex(length)))
        except TypeError:
            self._log.error("Flash address and read length must be integers!")
            raise

        try:
            # Check that file is not empty.
            flash_size = os.stat(temp_file).st_size
            if flash_size != length:
                raise FlashProgrammerException("Failed to read data from the EM100 on USB port {}".format(usb_port))

            # Open the binary file created and return a byte array
            with open(temp_file, "rb") as read_bytes:
                result = bytearray(read_bytes.read())
        except Exception as e:
            self._log.exception(e)
            raise
        else:
            if len(result) <= 0xF:
                self._log.debug("Read {} from EM100 on USB port {}".format(binascii.hexlify(result), usb_port))
            else:
                self._log.debug("Read from EM100 on USB port {} successful".format(usb_port))
            return result
        finally:
            # Try to remove temporary file and return result.
            os.remove(temp_file)

    def write(self, address, data, target):
        target_device = self.device_mapping[target]
        for emulator in target_device[1]:
            self._write(address, data, emulator, target_device[0])
    

    def _write(self, address, data, usb_port, chip):
        # Save current flash data from the emulator to a temporary file.
        if type(data) != bytearray:
            raise ValueError("data must be a byte array!")
        if address < 0:
            raise ValueError("Address must be >= 0! address = {}".format(hex(address)))
        temp_file = "mod.bin"  # TODO: Write to this file and apply with --addr and --length flags
        try:
            subprocess.check_output([self.base_cmd,
                                     self.DEVICE, str(usb_port),
                                     self.CHIP, chip,
                                     self.DP_STOP,
                                     self.DP_READ, temp_file,
                                     self.DP_START], stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            self._log.error("Flash dump from emulator failed! Output: {}".format(e.output))
            self._try_emulator_recovery(usb_port, chip)
            raise FlashProgrammerException("Unable to read flash image from EM100 on USB port {}".format(usb_port))
        try:
            # Get flash size and sanity check inputs.
            flash_size = os.stat(temp_file).st_size
            if flash_size < 1:
                raise FlashProgrammerException("Failed to save flash image from the flash emulator!")
            elif address + len(data) > flash_size:
                raise ValueError("Requested data would overflow end of flash! Cannot proceed.")

            # Modify flash image with the provided data
            with open(temp_file, "rb+") as flash:
                flash_map = mmap.mmap(flash.fileno(), 0)
                if six.PY2:
                    flash_map[address:address + len(data)] = str(data)
                else:
                    flash_map[address:address + len(data)] = data
                flash_map.flush()
                flash_map.close()

            # Download modified image to the emulator
            self._log.debug("Loading modified image to EM100 on USB port {}".format(usb_port))
            self._flash_image(temp_file, usb_port, chip)
        except Exception as e:
            self._log.exception(e)
            raise
        finally:
            os.remove(temp_file)
    
    def chip_identify(self):
        """
        this is to identify the chip name and the size of the chip and company that manufactured this chip
        identifies the chip whether it is getting detected and supported for flashing using spi interface or not
        chips size that supports 8mb,16mb,32mb,64mb chips are supported from all major manufacturers
        :raises FlashProgrammerException: If image flashing fails.
        :return: True,Flash Chip Name,Manufacturer Name,Size of the CHIP or False,Not Detected 
        """
        raise NotImplementedError

    def current_bmc_version_check(self):
        """
        Get Current BMC FLASHED VERSION ON Platform
        :return: True,version name
        """
        raise NotImplementedError

    def current_bios_version_check(self):
        """
        Get Current BIOS FLASHED VERSION ON Platform
        :return: True,version name
        """
        raise NotImplementedError

    def current_cpld_version_check(self):
        # type: () -> None
        """
        Get Current CPLD FLASHED VERSION ON Platform via Redfish Interface
        :return: True,version name
        """
        raise NotImplementedError

    def flash_image_bmc(self, path=None,image_name=None, target=None, amc=None):
        # type: (str, str) -> None
        """
        Flash image from 'path' to the emulator.

        :param path: Local path to the binary file to load into the emulator.
        :param target: One of dtaf_core.lib.flash.FlashDevices selecting which device on the platform to flash
        :raises FlashProgrammerException: If image flashing fails.
        :return: None
        """
        raise NotImplementedError

