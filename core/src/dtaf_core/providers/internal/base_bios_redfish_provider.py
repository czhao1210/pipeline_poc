#!/usr/bin/env python
"""
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
"""
from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.bios_provider import BiosProvider
from dtaf_core.drivers.internal.redfish_driver import RedfishDriver

class BaseBiosRedfishProvider(BiosProvider,RedfishDriver):
    def __init__(self, cfg_opts, log):
        """
        :param self._log: Logger object to use for debug and info messages
        :param cfg_opts: Dictionary of configuration options for execution environment.
        """
        super(BaseBiosRedfishProvider, self).__init__(cfg_opts, log)

    def __enter__(self):
        return super(BaseBiosRedfishProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(BaseBiosRedfishProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def set_bios_bootorder(self, first_boot=""):
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"redfish")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                ret = sw.set_bios_category_bootorder(first_boot)
                if (ret == True):
                    self._log.info(
                        "Redfish Based Change Boot order successfull with the passed value {0}".format(first_boot))
                    return True
            except Exception as ex:
                self._log.error("Redfish Based Change Boot order caused Error:{}".format(ex))
                return False

    def get_bios_bootorder(self):
        self._log.info(
            "Redfish Based get Boot order works only with pre-defined Tags \"Pxe\",\"Hdd\",\"Cd\",\"Diags\",\"BiosSetup\",\"Usb\"")
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,driver_name=r"redfish")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                ret = sw.get_bios_category_bootorder()
                if (ret[0] == True):
                    self._log.info(
                        "Redfish Based GET Boot order successfull with the passed value")
                    return True, ret[1]
            except Exception as ex:
                self._log.error("Redfish Based GET Boot order caused Error:{}".format(ex))
                return False

    def select_boot_device(self, boot_device):
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,driver_name=r"redfish")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw: #type: RedfishDriver
            return sw.select_boot_device(boot_device)

    def get_boot_device(self):
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,driver_name=r"redfish")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw: #type: RedfishDriver
            return sw.get_boot_device()