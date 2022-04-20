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
from abc import ABCMeta, abstractmethod
from dtaf_core.providers.base_provider import BaseProvider

@six.add_metaclass(ABCMeta)
class FlashProvider(BaseProvider):
    """Provider for manipulating flash chips attached to the SUT."""

    # Constants for FlashProvider
    DEFAULT_CONFIG_PATH = "suts/sut/providers/flash"

    def __init__(self, cfg_opts, log):
        """
        Create a new FlashProvider object

        :param self._log: Logger object to use for debug and info messages
        :param cfg_opts: Dictionary of configuration options for execution environment.
        """
        super(FlashProvider, self).__init__(cfg_opts, log)

    def __enter__(self):
        return super(FlashProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(FlashProvider, self).__exit__(exc_type, exc_val, exc_tb)

    @abstractmethod
    def flash_image(self, path=None,image_name=None, target=None, amc=None):
        # type: (str, str) -> None
        """
        Flash image from 'path' to the emulator.

        :param path: Local path to the binary file to load into the emulator.
        :param target: One of dtaf_core.lib.flash.FlashDevices selecting which device on the platform to flash
        :raises FlashProgrammerException: If image flashing fails.
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def chip_identify(self):
        # type: (str, str) -> None
        """
        this is to identify the chip name and the size of the chip and company that manufactured this chip
        identifies the chip whether it is getting detected and supported for flashing using spi interface or not
        chips size that supports 8mb,16mb,32mb,64mb chips are supported from all major manufacturers
        :raises FlashProgrammerException: If image flashing fails.
        :return: True,Flash Chip Name,Manufacturer Name,Size of the CHIP or False,Not Detected 
        """
        raise NotImplementedError

    @abstractmethod
    def read(self, address=None, length=None, target=None):
        # type: (int, int, str) -> bytearray
        """
        Read data from loaded image.

        :param address: Flash address to read from.
        :param length: Number of bytes to read starting at address.
        :param target: One of dtaf_core.lib.flash.FlashDevices selecting which device on the platform to read from
        :raises FlashProgrammerException: If read action fails.
        :raises ValueError: If input arguments are out of range.
        :return: Data stored at 'address'
        """
        raise NotImplementedError

    @abstractmethod
    def write(self, address=None, data=None, target=None):
        # type: (int, bytearray, str) -> None
        """
        Modify loaded image.

        :param address: Flash address to modify.
        :param data: Python bytearray used to overwrite existing values starting at address.
        :param target: One of dtaf_core.lib.flash.FlashDevices selecting which device on the platform to write to
        :raises FlashProgrammerException: If write action fails.
        :raises ValueError: If input arguments are out of range.
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def current_bios_version_check(self):
        # type: () -> None
        """
        Get Current BIOS FLASHED VERSION ON Platform
        :return: True,version name
        """
        raise NotImplementedError

    @abstractmethod
    def current_bmc_version_check(self):
        # type: () -> None
        """
        Get Current BMC FLASHED VERSION ON Platform
        :return: True,version name
        """
        raise NotImplementedError

    @abstractmethod
    def current_cpld_version_check(self):
        # type: () -> None
        """
        Get Current CPLD FLASHED VERSION ON Platform via Redfish Interface
        :return: True,version name
        """
        raise NotImplementedError

    @abstractmethod
    def flash_image_bmc(self, path=None, image_name=None, target=None, amc=None):
        # type: (str, str) -> None
        """
        Flash image from 'path' to the emulator.

        :param path: Local path to the binary file to load into the emulator.
        :param target: One of dtaf_core.lib.flash.FlashDevices selecting which device on the platform to flash
        :raises FlashProgrammerException: If image flashing fails.
        :return: None
        """
        raise NotImplementedError

