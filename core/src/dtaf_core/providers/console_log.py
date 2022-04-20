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
"""
APIs to read/write console log
"""
from abc import ABCMeta
from six import add_metaclass
from dtaf_core.providers.base_provider import BaseProvider


@add_metaclass(ABCMeta)
class ConsoleLogProvider(BaseProvider):
    """
    Base Class that record all output data into log file.
    """
    DEFAULT_CONFIG_PATH = 'suts/sut/providers/console_log'

    def __init__(self, cfg_opts, log):
        """
        Create a new ConsoleLogProvider object.

        :param cfg_opts: xml.etree.ElementTree.Element of configuration options for execution environment
        :param log: Logger object to use for output messages
        """
        super(ConsoleLogProvider, self).__init__(cfg_opts, log)

    def __enter__(self):
        return super(ConsoleLogProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(ConsoleLogProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def inject_line(self, line):
        # type: (str) -> None
        """
        Insert a separate line into serial log file.

        :param line: data line, any sequence that can be converted into string
        :return: None
        """
        raise NotImplementedError

    def read(self):
        # type: () -> str
        """
        Read from your serial port.
        :return:
        """
        raise NotImplementedError

    def write(self, buf):
        # type: () -> None
        """
        Write to your serial port.
        :param buf:
        :return:
        """
        raise NotImplementedError

    def make_repo(self, path):
        # type: (str) -> None
        """
        log will be moved to the repo after case is executed.

        :param path: path of repo
        :return:
        """
        raise NotImplementedError
