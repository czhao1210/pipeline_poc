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
from abc import ABCMeta, abstractmethod

from six import add_metaclass
from dtaf_core.providers.base_provider import BaseProvider


@add_metaclass(ABCMeta)
class DeploymentProvider(BaseProvider):
    """
    Class used to deploy sut and host before testing

    This class cannot be used directly, instead, this interface is applied to the subclasses, with a different subclass
    communication (SOL, Serial) This makes the dependency on specific hardware setups easier to
    identify.
    """
    DEFAULT_CONFIG_PATH = "suts/sut/providers/deployment"

    def __init__(self, cfg_opts, log):
        """
        Create a new DeploymentProvider object

        :param self._log: Logger object to use for debug and info messages
        :param cfg_opts: Dictionary of configuration options for execution environment.
        """
        super(DeploymentProvider, self).__init__(cfg_opts, log)

    @abstractmethod
    def download(self, package_url):
        # type:(str) -> None
        """
        download ingredient to local

        :param ingredient_url: ingredient name

        :return: local path of ingredient / None if failed
        """
        raise NotImplementedError

    @abstractmethod
    def get_ingredient_info(self, kit_path, kit_name, ingredient_name):
        # type:(str, str, str) -> None
        """
        download ingredient to local

        :param kit_path: kit repo path
        :param kit_name: kit name
        :param ingredient_name: ingredient name

        :return: dict(ingreident name, version, url)
        """
        raise NotImplementedError

    @abstractmethod
    def get_device_property(self, name):
        # type:(str) -> None
        raise NotImplementedError
