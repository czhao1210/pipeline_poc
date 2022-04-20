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
from dtaf_core.lib.private.driver_config.tcf_driver_config import TcfDriverConfig
from dtaf_core.lib.private.provider_config.base_provider_config import BaseProviderConfig


class SutOsProviderConfig(BaseProviderConfig):
    """
    Configuration options for SutOsProviders, regardless of concrete implementation.
    """

    _DEFAULT_SHUTDOWN_DELAY = 5

    def __init__(self, cfg_opts, log):
        super(SutOsProviderConfig, self).__init__(cfg_opts, log)
        if isinstance(self.driver_cfg, TcfDriverConfig):  # TCF
            if len(self.driver_cfg.targets) != 1 or len(self.driver_cfg.interconnects) != 1:
                raise RuntimeError("Only one TCF target supported!")

            self.__target = self.driver_cfg.targets[0]
            self.__os_type = self.__target.kws["dtaf"]["SutOsProvider"]["os_type"]
            self.__os_subtype = self.__target.kws["dtaf"]["SutOsProvider"]["os_subtype"]
            self.__os_version = self.__target.kws["dtaf"]["SutOsProvider"]["os_version"]
            self.__os_kernel = self.__target.kws["dtaf"]["SutOsProvider"]["os_kernel"]

            try:
                self.__shutdown_delay = self.__target.kws["dtaf"]["SutOsProvider"]["shutdown_delay"]
            except KeyError:
                self.__shutdown_delay = self._DEFAULT_SHUTDOWN_DELAY

        else:  # DTAF config file
            prvider_name = list(cfg_opts.keys())[0]
            self.__os_type = cfg_opts[prvider_name]["@{}".format(ConfigFileParameters.ATTR_SUT_OS_TYPE)]
            self.__os_subtype = cfg_opts[prvider_name]["@{}".format(ConfigFileParameters.ATTR_SUT_OS_SUBTYPE)]
            self.__os_version = cfg_opts[prvider_name]["@{}".format(ConfigFileParameters.ATTR_SUT_OS_VERSION)]
            self.__os_kernel = cfg_opts[prvider_name]["@{}".format(ConfigFileParameters.ATTR_SUT_OS_KERNEL)]

            try:
                self.__verify = cfg_opts[prvider_name]["@verify"]
            except KeyError:
                self.__verify = 'false'

            try:
                self.__shutdown_delay = float(cfg_opts[prvider_name][r"shutdown_delay"].strip())
            except AttributeError:
                self.__shutdown_delay = self._DEFAULT_SHUTDOWN_DELAY

    @property
    def shutdown_delay(self):
        return self.__shutdown_delay

    @property
    def os_type(self):
        return self.__os_type

    @property
    def os_subtype(self):
        return self.__os_subtype

    @property
    def os_version(self):
        return self.__os_version

    @property
    def os_kernel(self):
        return self.__os_kernel

    @property
    def verify(self):
        return self.__verify
