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
from dtaf_core.lib.private.provider_config.base_provider_config import BaseProviderConfig
from dtaf_core.lib.config_file_constants import ConfigFileParameters

class BaninoProviderConfig(BaseProviderConfig):
    def __init__(self, cfg_opts, log):
        super(BaninoProviderConfig, self).__init__(cfg_opts, log)
        provider_name = list(cfg_opts.keys())[0]
        try:
            self._banino_dll_path =cfg_opts[provider_name][r"banino_dll_path"].strip()
            self._banino_power_cmd =cfg_opts[provider_name][r"banino_power_cmd"].strip()
            self._ladybird_driver_serial =cfg_opts[provider_name][r"ladybird_driver_serial"].strip()
        except AttributeError as attrib_err:
            #print("eoor")
            self._banino_dll_path = None
            self._banino_power_cmd = None
            self._banino_self._ladybird_driver_serial = None

        try:
            self.__image_path =cfg_opts[provider_name][r"image_path"].strip()
        except AttributeError as attrib_err:
            self.__image_path = None

        try:
            self.__image_name =cfg_opts[provider_name][r"image_name"].strip()
        except AttributeError as attrib_err:
            self.__image_name = None

        try:
            self.__image_path_bmc =cfg_opts[provider_name][r"image_path_bmc"].strip()
        except AttributeError as attrib_err:
            self.__image_path_bmc = None

        try:
            self.__image_name_bmc =cfg_opts[provider_name][r"image_name_bmc"].strip()
        except AttributeError as attrib_err:
            self.__image_name_bmc = None
            
    @property
    def banino_dll_path(self):
        return self._banino_dll_path

    @property
    def banino_power_cmd(self):
        return self._banino_power_cmd
    
    @property
    def ladybird_driver_serial(self):
        return self._ladybird_driver_serial

    @property
    def image_path(self):
        return self.__image_path

    @property
    def image_name(self):
        return self.__image_name

    @property
    def image_path_bmc(self):
        return self.__image_path_bmc

    @property
    def image_name_bmc(self):
        return self.__image_name_bmc
