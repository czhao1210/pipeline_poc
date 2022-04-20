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

class UsbblasterProviderConfig(BaseProviderConfig):
    def __init__(self, cfg_opts, log):
        super(UsbblasterProviderConfig, self).__init__(cfg_opts, log)
        try:
            self.__cpld_application_path = cfg_opts.find(r"cpld_application_path").text.strip()
        except AttributeError as attrib_err:
            self.__cpld_application_path = None

        try:
            self.__primary_image_path = cfg_opts.find(r"primary_image_path").text.strip()
        except AttributeError as attrib_err:
            self.__primary_image_path = None

        try:
            self.__primary_image_name = cfg_opts.find(r"primary_image_name").text.strip()
        except AttributeError as attrib_err:
            self.__primary_image_name = None

        try:
            self.__secondary_image_path = cfg_opts.find(r"secondary_image_path").text.strip()
        except AttributeError as attrib_err:
            self.__secondary_image_path = None

        try:
            self.__secondary_image_name = cfg_opts.find(r"secondary_image_name").text.strip()
        except AttributeError as attrib_err:
            self.__secondary_image_name = None

    @property
    def cpld_application_path(self):
        return self.__cpld_application_path

    @property
    def primary_image_path(self):
        return self.__primary_image_path

    @property
    def primary_image_name(self):
        return self.__primary_image_path

    @property
    def secondary_image_path(self):
        return self.__secondary_image_path

    @property
    def secondary_image_name(self):
        return self.__secondary_image_name



