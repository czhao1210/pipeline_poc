#!/usr/bin/env python
"""
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
"""
from abc import ABCMeta

from six import add_metaclass

from dtaf_core.providers.console_log import ConsoleLogProvider


@add_metaclass(ABCMeta)
class LogProvider(ConsoleLogProvider):
    """
    Base Class that record all output data into log file.
    """
    DEFAULT_CONFIG_PATH = 'suts/sut/providers/console_log'

    def __init__(self, cfg_opts, log):
        """
        Create a new LogProvider object.

        :param cfg_opts: xml.etree.ElementTree.Element
        :param log: Logger object to use for output messages
        """
        super(LogProvider, self).__init__(cfg_opts, log)

    def __enter__(self):
        return super(LogProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(LogProvider, self).__exit__(exc_type, exc_val, exc_tb)
