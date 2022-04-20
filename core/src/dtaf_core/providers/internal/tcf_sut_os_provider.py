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
import time

from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.exceptions import OsStateTransitionException
from dtaf_core.providers.internal.ssh_sut_os_provider import SshSutOsProvider
from dtaf_core.drivers.driver_factory import DriverFactory


class TcfSutOsProvider(SshSutOsProvider):
    """
    Executes provided commands on a remote SUT over SSH.
    """

    def _load_config(self):
        self._tcf = DriverFactory.create(
            cfg_opts=ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"tcf"),
            logger=self._log)
        dynamic_conf = self._tcf.get_target().kws
        self._ip = dynamic_conf['dtaf']['SutOsProvider']['sut_address']
        self._user = dynamic_conf['dtaf']['SutOsProvider']['user']
        self._password = dynamic_conf['dtaf']['SutOsProvider']['sut_private_key']
        try:
            self._jump_user = dynamic_conf['dtaf']['SutOsProvider']['jump_user']
            self._jump_host = dynamic_conf['dtaf']['SutOsProvider']['jump_host']
            self._jump_auth = dynamic_conf['dtaf']['SutOsProvider']['jump_key']
        except KeyError:
            self._jump_user = None
            self._jump_host = None
            self._jump_auth = None
