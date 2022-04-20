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


class SimicsProviderConfig(BaseProviderConfig):
    """
    Configuration options for SimicsProvider
    """

    def __init__(self, cfg_opts, log):
        super(SimicsProviderConfig, self).__init__(cfg_opts, log)
        provider_name = list(cfg_opts.keys())[0]
        self.__telnet_port = int(cfg_opts[provider_name]["telnet_port"].strip())
        self.__workspace = cfg_opts[provider_name]["workspace"].strip()
        self.__simics_path = cfg_opts[provider_name]["simics_path"].strip()
        self.__serial_log = cfg_opts[provider_name]["serial_log"].strip()

    @property
    def telnet_port(self):
        return self.__telnet_port

    @property
    def serial_log(self):
        return self.__serial_log

    @property
    def workspace(self):
        return self.__workspace

    @property
    def simics_path(self):
        return self.__simics_path