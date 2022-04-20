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

from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig
from xml.etree.ElementTree import Element, tostring
import xml
import xmltodict

class PuttyDriverConfig(BaseDriverConfig):
    def __init__(self, cfg_opts, log):
        super(PuttyDriverConfig, self).__init__(cfg_opts, log)
        cfg_dict = dict(cfg_opts)
        if xml.etree.ElementTree.iselement(cfg_opts):
            cfg_dict = xmltodict.parse(tostring(cfg_opts))
        self.__port = cfg_dict["putty"]['port']
        self.__baudrate = int(cfg_dict["putty"]['baudrate'].strip())
        self.__timeout = float(cfg_dict["putty"]['timeout'].strip())
        try:
            self.__app = cfg_dict["putty"]['app']
        except KeyError as e:
            self.__app = "putty"

    @property
    def port(self):
        return self.__port

    @property
    def baudrate(self):
        return self.__baudrate

    @property
    def timeout(self):
        return self.__timeout

    @property
    def app(self):
        return self.__app


