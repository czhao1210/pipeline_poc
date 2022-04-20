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
"""
sound wave driver configuration
"""
from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig
from dtaf_core.lib.config_file_constants import ConfigFileParameters
from xml.etree.ElementTree import Element, tostring
import xmltodict
import xml

class Soundwave2kDriverConfig(BaseDriverConfig):
    """
    Soundwave2k Driver Configuration Class: parsing value from XML
    """

    def __init__(self, cfg_opts, log):
        super(Soundwave2kDriverConfig, self).__init__(cfg_opts, log)
        cfg_dict = dict(cfg_opts)
        if xml.etree.ElementTree.iselement(cfg_opts):
            cfg_dict = xmltodict.parse(tostring(cfg_opts))
        self.__enable_s3_detect = eval(cfg_dict["soundwave2k"]["@enable_s3_detect"])
        try:
            self.__serial_type = cfg_dict[r"serial"][r"@type"]
        except KeyError as error:
            self.__serial_type = "1"
        self.__serial_baudrate = int(cfg_dict["soundwave2k"][r"baudrate"])
        self.__serial_port = cfg_dict["soundwave2k"]["port"]
        self.__low_main_power_voltage = float(cfg_dict["soundwave2k"]["voltagethreholds"]["main_power"]["low"])
        self.__high_main_power_voltage = float(cfg_dict["soundwave2k"]["voltagethreholds"]["main_power"]["high"])
        self.__low_dsw_voltage = float(cfg_dict["soundwave2k"]["voltagethreholds"]["dsw"]["low"])
        self.__high_dsw_voltage = float(cfg_dict["soundwave2k"]["voltagethreholds"]["dsw"]["high"])
        self.__low_memory_voltage = float(cfg_dict["soundwave2k"]["voltagethreholds"]["memory"]["low"])
        self.__high_memory_voltage = float(cfg_dict["soundwave2k"]["voltagethreholds"]["memory"]["high"])

    @property
    def enable_s3_detect(self):
        """
        serial_type
        :return: True / False
        """
        return self.__enable_s3_detect

    @enable_s3_detect.setter
    def enable_s3_detect(self, value):
        """
        enable s3 detect flag
        :param value:
        :return:
        """
        self.__enable_s3_detect = value
        return self.__enable_s3_detect

    @property
    def serial_type(self):
        """
        serial_type
        :return: string type
        """
        return self.__serial_type

    @property
    def serial_baudrate(self):
        """
        serial_baudrate
        :return: string type
        """
        return self.__serial_baudrate

    @property
    def serial_port(self):
        """
        serial_port
        :return: string type
        """
        return self.__serial_port

    @property
    def low_main_power_voltage(self):
        """
        low_main_power_voltage
        :return: float type
        """
        return self.__low_main_power_voltage

    @property
    def high_main_power_voltage(self):
        """
        high_main_power_voltage
        :return: float type
        """
        return self.__high_main_power_voltage

    @property
    def low_dsw_voltage(self):
        """
        low_dsw_voltage
        :return: float type
        """
        return self.__low_dsw_voltage

    @property
    def high_dsw_voltage(self):
        """
        high_dsw_voltage
        :return: float type
        """
        return self.__high_dsw_voltage

    @property
    def low_memory_voltage(self):
        """
        low_memory_voltage
        :return: float type
        """
        return self.__low_memory_voltage

    @property
    def high_memory_voltage(self):
        """
        high_memory_voltage
        :return: float type
        """
        return self.__high_memory_voltage
