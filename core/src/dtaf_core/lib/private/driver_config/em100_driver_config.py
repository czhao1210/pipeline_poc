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
from dtaf_core.lib.config_file_constants import ConfigFileParameters
from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig
from xml.etree.ElementTree import Element
import xmltodict

class Em100DriverConfig(BaseDriverConfig):

    def __init__(self, cfg_opts, log):
        super(Em100DriverConfig, self).__init__(cfg_opts, log)
        # Get path to EM100 software
        driver_name = list(cfg_opts.keys())[0]
        cfg_opts = dict(cfg_opts)
        self._cli_path = cfg_opts[driver_name]["@cli_path"]

        # Get the flash device configuration of the platform
        self._chip_config = {}
        for device in cfg_opts[driver_name]["device"]:
            chip = device["@{}".format(ConfigFileParameters.ATTR_CHIP)]
            ports = device["@{}".format(ConfigFileParameters.ATTR_USB_PORTS)]
            # Some modular configurations have multiple chips that have to be flashed per device.
            programmers = ports.split(",") if ports.count(',') > 0 else [ports]
            self._chip_config[device["@{}".format(ConfigFileParameters.ATTR_FLASH_DEVICE_NAME)]] = (chip, programmers)

    @property
    def chip_config(self):
        return self._chip_config

    @property
    def cli_path(self):
        return self._cli_path
