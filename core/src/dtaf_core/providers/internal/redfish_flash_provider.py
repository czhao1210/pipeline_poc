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
import sys
import glob
import time
import json
import requests
import datetime
import subprocess
from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.providers.flash_provider import FlashProvider
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.provider_factory import ProviderFactory
from dtaf_core.drivers.internal.redfish_driver import RedfishDriver

class RedfishFlashProvider(FlashProvider,RedfishDriver):
    NO_HTTP_RESPONSE = 0 #changed
    def __init__(self,cfg_opts,log):
        """
        :param self._log: Logger object to use for debug and info messages
        :param cfg_opts: Dictionary of configuration options for execution environment.
        """
        super(RedfishFlashProvider, self).__init__(cfg_opts,log)
        self.__image_path_bmc=self._config_model.driver_cfg.image_path
        self.__image_name_bmc=self._config_model.driver_cfg.image_name
        self.__image_path_bios = self._config_model.driver_cfg.image_path_bios
        self.__image_name_bios = self._config_model.driver_cfg.image_name_bios
        self.__image_path_cpld = self._config_model.driver_cfg.image_path_cpld
        self.__image_name_cpld = self._config_model.driver_cfg.image_name_cpld

        #changes for seamless
        self._ip = self._config_model.driver_cfg.ip
        self.last_resp_status_code = self.NO_HTTP_RESPONSE
        self.REDFISH_VERSION = "v1/"
        self.BMC_PATH = "https://" + self._ip + "/redfish/" + self.REDFISH_VERSION
        self.verbose = True
        self._skip_sel_count = 9999999  # very high to ensure old records are not returned
        self.eve_skip_sel_count = 9999999  # very high to ensure old records are not returned

    def __enter__(self):
        return super(RedfishFlashProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(RedfishFlashProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def flash_image(self,path=None,image_name=None,target=None):
        """
        This function takes care of identifying and erasing and writing a new image from a location.
        it takes the ifwi image or the bmc image based on the modification/creation time it is going to take the lateset time by default of the image.
        Image for flashing will be taken from the "+str(root)+"/firmware/ folder name is frimware from this the image will be taken.
        path in this are fixed path even though folders don't exists it will created it,2nd time run it will copy them
        """
        if(target.lower() == "cpld"):
            driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"redfish")
            with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
                if path:
                    path = path
                else:
                    path = self.__image_path_cpld
                if image_name:
                    image_name = image_name
                else:
                    image_name = self.__image_name_cpld
                try:
                    if (sw.chip_flash_cpld(path, image_name) == True):
                        return True
                    else:
                        return False
                except Exception as ex:
                    self._log.error("Couldn't Detect The cpld http Flash Response From Platform {0}".format(ex))
                    raise
        else:
            driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"redfish")
            with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
                if path:
                    path = path
                else:
                    path = self.__image_path_bios
                if image_name:
                    image_name = image_name
                else:
                    image_name = self.__image_name_bios
                try:
                    if (sw.chip_flash_bios(path, image_name) == True):
                        return True
                    else:
                        return False
                except Exception as ex:
                    self._log.error("Couldn't Detect The bios http Flash Response In Platform {0}".format(ex))
                    raise

    def current_bios_version_check(self):
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"redfish")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                ret = sw.current_bios_version_check()
                if (ret[0] == True):
                    return True, ret[1]
                else:
                    return False
            except Exception as ex:
                self._log.error("Couldn't Detect The BIOS http Flash Response In Platform {0}".format(ex))
                raise

    def chip_identify(self):
        """
        this is to identify the chip name and the size of the chip and company that manufactured this chip
        identifies the chip whether it is getting detected and supported for flashing using spi interface or not
        chips size that supports 8mb,16mb,32mb,64mb chips are supported from all major manufacturers
        :raises FlashProgrammerException: If image flashing fails.
        :return: True,Flash Chip Name,Manufacturer Name,Size of the CHIP or False,Not Detected 
        """
        raise NotImplementedError

    def read(self):
        """
        To get the image stored in the bios chip or the bmc chip read and storing the chip data can be done.
        location after reading it will store it in this location "+str(root)+"/chipread with the current date and time beiging the file name
        """
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
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"redfish")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                ret = sw.current_bmc_version_check()
                if (ret[0] == True):
                    return True, ret[1]
                else:
                    return False
            except Exception as ex:
                self._log.error("Couldn't Detect The BMC http Flash Response From Platform {0}".format(ex))
                raise

    def current_cpld_version_check(self):
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"redfish")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                ret = sw.current_cpld_version_check()
                if (ret[0] == True):
                    return True, ret[1]
                else:
                    return False
            except Exception as ex:
                self._log.error("Couldn't Detect The cpld http Flash Response From Platform {0}".format(ex))
                raise

    def flash_image_bmc(self, path=None, image_name=None):
        """
        This function takes care of identifying and erasing and writing a new image from a location.
        it takes the ifwi image or the bmc image based on the modification/creation time it is going to take the lateset time by default of the image.
        Image for flashing will be taken from the "+str(root)+"/firmware/ folder name is frimware from this the image will be taken.
        path in this are fixed path even though folders don't exists it will created it,2nd time run it will copy them
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"redfish")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            if path:
                path = path
            else:
                path = self.__image_path_bmc
            if image_name:
                image_name = image_name
            else:
                image_name = self.__image_name_bmc
            try:
                if (sw.chip_flash_bmc(path, image_name) == True):
                    return True
                else:
                    return False
            except Exception as ex:
                 self._log.error("Couldn't Detect The BMC http Flash Response In Platform {0}".format(ex))
                 raise

    #changes from here

    def reset_bmc(self):
        """Issues reset command to BMC, raises exception if it fails"""
        self.execute_command("Managers/bmc/Actions/Manager.Reset", data=json.dumps({'ResetType': 'GracefulRestart'}))

    def stage_capsule_update(self, update_path):
        """
        Opens file at provided location and streams data via POST request through Redfish.
        :param update_path: path available to ITP host for update capsule to be staged
        """
        if self.verbose:
            self._log.info("Staging capsule update to BMC with address " + self._ip)
        with open(update_path, 'rb') as upload:
            self.execute_command("UpdateService", data=upload)

    def execute_command(self, cmd, log_all_output=False, power_loss_expected=False, timeout=None, verify_ssl=False, data=None, is_get=False, is_patch=False):
        """
        Executes a generic command. Raises exception if the send fails
        :return: The response data if the command was successful
        """
        self.last_resp_status_code = self.NO_HTTP_RESPONSE
        command = self.BMC_PATH + cmd
        if self.verbose:
            self._log.info("Running command -- " + command)

        if is_get:
            resp = requests.get(command, auth=(self._config_model.driver_cfg.username, self._config_model.driver_cfg.password), verify=verify_ssl)
        elif is_patch:
            resp = requests.patch(command, auth=(self._config_model.driver_cfg.username, self._config_model.driver_cfg.password), verify=verify_ssl, data=data)
        else:
            resp = requests.post(command, auth=(self._config_model.driver_cfg.username, self._config_model.driver_cfg.password), verify=verify_ssl, data=data)
        self.last_resp_status_code = resp.status_code
        if not (resp.status_code == requests.codes.ok or resp.status_code == requests.codes.accepted):
            error_msg = ("Received bad response from BMC [{}]".format(resp.status_code))
            self._log.error(error_msg)
            if resp.status_code == 503:
                raise RuntimeError(error_msg)

        return resp

    def get_bmc_sel(self):
        """
        Gets the SEL of the BMC
        :return: The JSON object of the SEL entries
        """
        resp = self.execute_command("Systems/system/LogServices/EventLog/Entries?$skip={}".format(self.eve_skip_sel_count),
                                    is_get=True)
        content = json.loads(resp.content)
        self.eve_skip_sel_count = int(content["Members@odata.count"])
        return content

    def get_bmc_jnl(self):
        """
        Gets the Journal of the BMC
        :return: The JSON object of the Journal entries
        """
        resp = self.execute_command("Managers/bmc/LogServices/Journal/Entries?$skip={}".format(self._skip_sel_count),
                                    is_get=True)
        content = json.loads(resp.content)
        self._skip_sel_count = int(content["Members@odata.count"])
        return content

    def get_bmc_version(self):
        """
        Checks for the FW version of the BMC
        :return: The version of BMC fw
        """
        version = ""
        VERSION_NAME = "FirmwareVersion"
        resp = self.execute_command("Managers/bmc", is_get=True)
        content = json.loads(resp.content)
        #todo - remove when https://hsdes.intel.com/appstore/article/#/2209857016 is resolved
        # if not self.last_resp_status_code == self.BMC_HTTP_SCREWED_UP:
        if VERSION_NAME not in content:
            raise RuntimeError("Failed to discover a BMC firmware version in the BMC response")
        version = content[VERSION_NAME]
        # else:
        #     version = "Unknown (500 error)"

        return version

    def get_bmc_bios_version(self):
        """
        Checks for the active BIOS version via the BMC
        :return: The version of active BIOS
        """
        resp = self.execute_command("UpdateService/FirmwareInventory/bios_active", is_get=True)
        content = json.loads(resp.content)
        if "Version" not in content:
            raise RuntimeError("Failed to discover a BIOS version in the BMC response")
        version = content["Version"]
        return version

    def get_bmc_cpld_version(self):
        """
        Checks for the active BIOS version via the BMC
        :return: The version of active BIOS
        """
        resp = self.execute_command("UpdateService/FirmwareInventory/cpld_active", is_get=True)
        content = json.loads(resp.content)
        if "Version" not in content:
            raise RuntimeError("Failed to discover a CPLD version in the BMC response")
        version = content["Version"]
        return version

    def get_firmwareinventory(self):
        """
        Get firmware inventory from BMC
        :return: Firmware inventory
        """
        resp = self.execute_command("UpdateService/FirmwareInventory", is_get=True)
        content = json.loads(resp.content)
        firmware_inventory = content["Members"]
        firmware_inventory_list = []
        for item in firmware_inventory:
            item = '/'.join(item["@odata.id"].split('/')[-3:])
            item_resp = self.execute_command(item, is_get=True)
            item_content = json.loads(item_resp.content)
            firmware_inventory_list.append({"Description": item_content["Description"], "Id": item_content["Id"],
                                            "Version": item_content["Version"]})

        return firmware_inventory_list
