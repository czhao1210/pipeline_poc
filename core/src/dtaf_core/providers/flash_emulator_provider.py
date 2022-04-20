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
import six
from abc import ABCMeta, abstractmethod
from dtaf_core.providers.flash_provider import FlashProvider


@six.add_metaclass(ABCMeta)
class FlashEmulatorProvider(FlashProvider):
    """
    Flash provider that also provides emulator-specific functionality.

    This provider should be used when read/write capability is needed while system power is on.
    """

    # Constants for FlashEmulatorProvider
    DEFAULT_CONFIG_PATH = "suts/sut/providers/flash_emulator"

    @abstractmethod
    def start(self, target):
        # type: (str) -> None
        """
        Start flash emulation

        :param target: One of dtaf_core.lib.flash.FlashDevices, specifying which device to flash (PCH, BMC, etc)
        :raises FlashEmulatorException: Upon failure of emulator to start
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def stop(self, target):
        # type: (str) -> None
        """
        Stop flash emulation

        :param target: One of dtaf_core.lib.flash.FlashDevices, specifying which device to flash (PCH, BMC, etc)
        :raises FlashEmulatorException: Upon failure of emulator to stop
        :return: None
        """
        raise NotImplementedError
