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
from xml.etree.ElementTree import Element, tostring
import xml
import xmltodict


class ConsoleProviderConfig(BaseProviderConfig):
    def __init__(self, cfg_opts, log):
        super(ConsoleProviderConfig, self).__init__(cfg_opts, log)
        cfg_dict = dict(cfg_opts)
        if xml.etree.ElementTree.iselement(cfg_opts):
            cfg_dict = dict(xmltodict.parse(tostring(cfg_opts)))
        provider_name = list(cfg_dict.keys())[0]
        self.__credentials = cfg_dict[provider_name]['credentials']
        self.__user = cfg_dict[provider_name]['credentials']["@user"]
        self.__password = cfg_dict[provider_name]['credentials']["@password"]
        try:
            self.__login_time_delay = int(cfg_dict[provider_name]['login_time_delay'])
        except KeyError as error:
            self.__login_time_delay = 60
        except ValueError as error:
            self.__login_time_delay = 60

    @property
    def credentials(self):
        return self.__credentials

    @property
    def user(self):
        return self.__user

    @property
    def password(self):
        return self.__password

    @property
    def login_time_delay(self):
        return self.__login_time_delay
