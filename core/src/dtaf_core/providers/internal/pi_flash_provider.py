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
import os
import time
import sys
import subprocess
import datetime
import glob
from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.drivers.internal.pi_driver import PiDriver
from dtaf_core.providers.flash_provider import FlashProvider
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.provider_factory import ProviderFactory


class PiFlashProvider(FlashProvider,PiDriver):
    def __init__(self,cfg_opts,log):
        """
        :param self._log: Logger object to use for debug and info messages
        :param cfg_opts: Dictionary of configuration options for execution environment.
        """
        super(PiFlashProvider, self).__init__(cfg_opts,log)
        self.__image_name=self._config_model.driver_cfg.image_name

    def __enter__(self):
        return super(PiFlashProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(PiFlashProvider, self).__exit__(exc_type, exc_val, exc_tb)
        
    def flash_image(self,path=None,image_name=None):
        """
        This function takes care of identifying and erasing and writing a new image from a location.
        it takes the ifwi image or the bmc image based on the modification/creation time it is going to take the lateset time by default of the image.
        Image for flashing will be taken from the "+str(root)+"/firmware/ folder name is frimware from this the image will be taken.
        path in this are fixed path even though folders don't exists it will created it,2nd time run it will copy them
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,driver_name=r"pi")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            if image_name:
                image_name=image_name
            else:
                image_name=self.__image_name
            try:
                 if sw.chip_flash(path,image_name):
                     return True
            except Exception:
                 self._log.error("Couldn't Detect The Flash Chip In Platform Failure")
                 raise

    def current_bios_version_check(self):
        """
        Get Current BIOS FLASHED VERSION ON Platform
        :return: True,version name
        """
        raise NotImplementedError

    def chip_identify(self):
        """
        this is to identify the chip name and the size of the chip and company that manufactured this chip
        identifies the chip whether it is getting detected and supported for flashing using spi interface or not
        chips size that supports 8mb,16mb,32mb,64mb chips are supported from all major manufacturers
        :raises FlashProgrammerException: If image flashing fails.
        :return: True,Flash Chip Name,Manufacturer Name,Size of the CHIP or False,Not Detected 
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,driver_name=r"pi")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                 if sw.chip_identify():
                     return True
            except Exception:
                 self._log.error("Couldn't Detect The Flash Chip In Platform Failure")
                 raise
           
    def read(self):
        """
        To get the image stored in the bios chip or the bmc chip read and storing the chip data can be done.
        location after reading it will store it in this location "+str(root)+"/chipread with the current date and time beiging the file name
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,driver_name=r"pi")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                 if sw.chip_reading():
                     return True
            except Exception:
                 self._log.error("Couldn't Detect The Flash Chip In Platform Failure")
                 raise
        raise NotImplementedError

    def write(self, address, data, target):
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

    def current_bmc_version_check(self):
        """
        Get Current BMC FLASHED VERSION ON Platform
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

    def flash_image_bmc(self, path=None, image_name=None):
        # type: (str, str) -> None
        """
        Flash image from 'path' to the emulator.

        :param path: Local path to the binary file to load into the emulator.
        :param target: One of dtaf_core.lib.flash.FlashDevices selecting which device on the platform to flash
        :raises FlashProgrammerException: If image flashing fails.
        :return: None
        """
        raise NotImplementedError


