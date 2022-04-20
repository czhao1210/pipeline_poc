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

from dtaf_core.lib.private.provider_config.base_provider_config import BaseProviderConfig
from dtaf_core.lib.private.providercfg_factory import ProviderCfgFactory
from dtaf_core.lib.test_context import TestContext


class ProviderFactory(object):
    """
    Factory is used to initiate Provider based on Configuration
    """

    @staticmethod
    def create(cfg_opts, logger):
        # type: (Element, Logger) -> BaseProvider
        """
        This is static function to create provider based on configuration

        :param cfg_opts: XML Element of configuration
        :param logger: logger
        :return: BaseProvider

        """
        provider_cfg = ProviderCfgFactory.create(cfg_opts=cfg_opts, log=logger)  # type: BaseProviderConfig
        import dtaf_core.providers.internal as provider_internal
        package = r"{}.{}_{}_provider".format(
            provider_internal.__name__,
            provider_cfg.driver_cfg.name,
            provider_cfg.provider_name)
        provider_name_sections = provider_cfg.provider_name.split(r"_")
        for i in range(0, len(provider_name_sections)):
            provider_name_sections[i] = "".join(
                [provider_name_sections[i][0].upper(), provider_name_sections[i][1:]])
        mod_name = r"{}Provider".format(
            provider_cfg.driver_cfg.name[0].upper()
            + provider_cfg.driver_cfg.name[1:]
            + "".join(provider_name_sections))
        mod = import_module(package, mod_name)
        provider_class = getattr(mod, mod_name)
        instance = provider_class(cfg_opts=cfg_opts, log=logger)
        TestContext().enter_context(instance)
        return instance

