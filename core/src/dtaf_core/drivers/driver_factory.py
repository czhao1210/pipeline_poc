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

from importlib import import_module
from xml.etree.ElementTree import Element

from dtaf_core.drivers.base_driver import BaseDriver
from dtaf_core.lib.test_context import TestContext
from dtaf_core.lib.private.provider_config.base_provider_config import BaseDriverConfig
from dtaf_core.lib.private.drivercfg_factory import DriverCfgFactory


class DriverFactory(object):
    """
    Factory is used to initiate Provider based on Configuration
    """

    @staticmethod
    def create(cfg_opts, logger):
        # type: (Element, Logger) -> BaseDriver
        """
        This is static function to create provider based on configuration

        :param cfg_opts: XML Element of configuration
        :param logger: logger
        :return: BaseDriver

        """
        driver_cfg = DriverCfgFactory.create(cfg_opts=cfg_opts, log=logger)  # type: BaseDriverConfig
        import dtaf_core.drivers.internal as internal_driver
        mod = import_module("{}.{}_driver".format(internal_driver.__name__, driver_cfg.name))
        mod_name = r"{}Driver".format("".join([driver_cfg.name[0].upper(), driver_cfg.name[1:]]))
        class_obj = getattr(mod, mod_name)
        driver = class_obj(cfg_opts=cfg_opts, log=logger)  # type: BaseDriver
        TestContext().enter_context(driver)
        return driver
