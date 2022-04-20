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
from abc import ABCMeta
from xml.etree.ElementTree import Element

from six import add_metaclass

from dtaf_core.lib.private.providercfg_factory import ProviderCfgFactory


@add_metaclass(ABCMeta)
class BaseProvider(object):
    """
    Abstract base class for Providers, classes that provide high-level abstractions for external resources.
    """

    def __init__(self, cfg_opts, log):
        """
        Create a new Provider object.

        :param log: logging.Logger object to use to store debug output from this Provider.
        :param cfg_opts: Dictionary of configuration options provided by the ConfigFileParser.
        """
        self._cfg = cfg_opts
        if isinstance(self._cfg, dict):
            self._cfg = self._cfg[list(self._cfg.keys())[0]]
        self._log = log
        self._config_model = ProviderCfgFactory.create(cfg_opts=cfg_opts, log=log)

    def __enter__(self):
        """
        Enter resource context for this Provider.

        :return: Resource to use (usually self)
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit resource context for this Provider.

        :param exc_type: Exception type
        :param exc_val: Exception value
        :param exc_tb: Exception traceback
        :return: None
        """
        self.close()

    def get_configuration(self):
        return self._config_model

    def close(self):
        pass

    def update_configuration(self, update_cfg_opts, update_log):
        driver_name = list(self._config_model.__dict__.get('_BaseProviderConfig__driver_cfg').__dict__.get(
            '_BaseDriverConfig__cfg').keys())[0]
        update_driver_name = None
        if not isinstance(update_cfg_opts, dict) and not isinstance(update_cfg_opts, Element):
            raise TypeError("update_cfg_opts must be dict or Element")
        elif isinstance(update_cfg_opts, dict):
            update_driver_name = update_cfg_opts[self._config_model.provider_name]["driver"][driver_name]
        elif isinstance(update_cfg_opts, Element):
            update_driver_name = update_cfg_opts.find('driver').find(driver_name)
        if not update_driver_name:
            raise Exception("The driver type is not allowed to change")
