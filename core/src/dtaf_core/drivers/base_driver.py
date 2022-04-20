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

from dtaf_core.lib.private.drivercfg_factory import DriverCfgFactory
from six import add_metaclass


@add_metaclass(ABCMeta)
class BaseDriver(object):
    """
    Abstract base class for Drivers, classes that provide low-level abstractions for external resources.
    """

    def __init__(self, cfg_opts, log):
        """
        Create a new driver object.

        :param cfg_opts: xml.etree.ElementTree.Element with configuration options provided by the instantiating Provider
        :param log: logging.Logger object to use to store debug output from this Provider.
        """
        self._cfg = cfg_opts
        self._log = log
        self._driver_cfg_model = DriverCfgFactory.create(cfg_opts=cfg_opts, log=log)

    def __enter__(self):
        """
        Enter resource context for this driver.

        :return: Resource to use (usually self)
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit resource context for this driver.

        :param exc_type: Exception type
        :param exc_val: Exception value
        :param exc_tb: Exception traceback
        :return: None
        """
        return None  # Note: DO NOT return a "True" value if you override this function. Otherwise, exceptions will be hidden!
