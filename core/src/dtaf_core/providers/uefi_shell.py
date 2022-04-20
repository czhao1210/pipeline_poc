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
APIs to interact with UEFI Shell
"""
from abc import ABCMeta
from six import add_metaclass
from dtaf_core.providers.base_provider import BaseProvider


@add_metaclass(ABCMeta)
class UefiShellProvider(BaseProvider):
    """
    Base Class that communicates with UEFI shell.
    """
    DEFAULT_CONFIG_PATH = 'suts/sut/providers/uefi_shell'

    def __init__(self, cfg_opts, log):
        """
        Create a new UEFIProvider object.

        :param cfg_opts: xml.etree.ElementTree.Element of configuration options for execution environment
        :param log: Logger object to use for output messages
        """
        super(UefiShellProvider, self).__init__(cfg_opts, log)

    def __enter__(self):
        return super(UefiShellProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(UefiShellProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def wait_for_uefi(self, timeout):
        # type: (int) -> None
        """
        Wait for SUT booting/rebooting into UEFI shell within specific timeout.

        :param timeout: Maximum timeout seconds
        :raise InvalidParameterError: If timeout is a negative value
        :raise TimeoutException: If not get result within specific timeout
        :return: None
        """
        raise NotImplementedError

    def exit_uefi(self):
        # type: () -> None
        """
        Exit UEFI shell.

        :return: None
        """
        raise NotImplementedError

    def in_uefi(self):
        # type: () -> bool
        """
        Check if the SUT is really in UEFI shell or not.

        :return: True if in UEFI else False
        """
        raise NotImplementedError

    def shutdown(self):
        # type: () -> None
        """
        Do shutdown action in UEFI shell.

        :return: None
        """
        raise NotImplementedError

    def reboot(self):
        # type: () -> None
        """
        Do reboot action in UEFI shell.

        :return: None
        """
        raise NotImplementedError

    def warm_reset(self):
        # type: () -> None
        """
        Do warm reset action in UEFI shell.

        :return: None
        """
        raise NotImplementedError

    def cold_reset(self):
        # type: () -> None
        """
        Do cold reset action in UEFI shell.

        :return: None
        """
        raise NotImplementedError

    def execute(self, cmd, timeout=0, end_pattern=None):
        # type: (str, int) -> str
        """
        Execute cmd in UEFI shell.

        :param cmd: UEFI command
        :param timeout: Maximum execution timeout, 0 means no need to wait for output data
        :param end_pattern: search pattern in output of command. if any match, API will return the data received.
        :raise InvalidParameterError: If input is an empty string, or timeout is a negative value
        :raise TimeoutException: If not get result within specific timeout
        :return: Execution result
        """
        raise NotImplementedError
