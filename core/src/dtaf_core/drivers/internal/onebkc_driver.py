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

from abc import ABCMeta
from binascii import a2b_hex, b2a_hex
import xml.dom.minidom
from serial import Serial
from serial import SerialException, SerialTimeoutException
from six import add_metaclass
from dtaf_core.drivers.base_driver import BaseDriver
from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.exceptions import SoundWaveError, InvalidParameterError, InputError


@add_metaclass(ABCMeta)
class OnebkcDriver(BaseDriver):
    """
    OneBKC Driver
    """

    def __enter__(self):
        """
        Enter resource context for this driver.

        :return: Resource to use (usually self)
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit resource context for this driver.

        :param exc_type: Exception type
        :param exc_val: Exception value
        :param exc_tb: Exception traceback
        :return: None
        """
        return None

    def __init__(self, cfg_opts, log):
        """
        Create a new driver object.

        :param cfg_opts: Dictionary of configuration options provided by the ConfigFileParser.
        :param log: logging.Logger object to use to store debug output from this Provider.
        """
        BaseDriver.__init__(self, cfg_opts, log)

    def parse_ingredient_info_from_manifest(self, manifest, ingredient_name):
        """
        :param manifest:
        :param ingredient_name:
        :return:
        """
        dom = xml.dom.minidom.parse(manifest)
        root = dom.documentElement
        item_list = root.getElementsByTagName('project')
        ingredient_info_dict = {}

        for i in range(item_list.length):
            item = item_list[i]
            name = item.getAttribute("ingredient")
            if name == ingredient_name:
                ingredient_info_dict["ingredient"] = ingredient_name
                ingredient_info_dict["version"] = item.getAttribute("version")
                ingredient_info_dict["pkg-path"] = item.getAttribute("pkg-path")
                ingredient_info_dict["artifactory"] = item.getAttribute("artifactory")
                return ingredient_info_dict
        return ingredient_info_dict
