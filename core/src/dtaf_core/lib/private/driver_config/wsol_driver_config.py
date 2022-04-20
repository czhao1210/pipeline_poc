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

import xml
from xml.etree.ElementTree import Element, tostring

import xmltodict

from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig


class WsolDriverConfig(BaseDriverConfig):
    """
    WsolDriverConfig
    """

    def __init__(self, cfg_opts, log):
        super().__init__(cfg_opts, log)
        cfg_dict = dict(cfg_opts)
        if xml.etree.ElementTree.iselement(cfg_opts):
            cfg_dict = xmltodict.parse(tostring(cfg_opts))

        self.__ip = cfg_dict["wsol"]['ip']
        self.__port = cfg_dict["wsol"]['port']
        self.__timeout = int(cfg_dict["wsol"]['timeout'])
        self.__user = cfg_dict["wsol"]['credentials']['@user']
        self.__password = cfg_dict["wsol"]['credentials']['@password']

    @property
    def ip(self):
        """
        ip of wsol configuration
        :return:ip
        """
        return self.__ip

    @property
    def port(self):
        """
        port of wsol configuration
        :return:port
        """
        return self.__port

    @property
    def timeout(self):
        """
        timeout of wsol configuration
        :return:timeout
        """
        return self.__timeout

    @property
    def user(self):
        """
        username of wsol configuration
        :return:username
        """
        return self.__user

    @property
    def password(self):
        """
        password of wsol configuration
        :return:passwod
        """
        return self.__password
