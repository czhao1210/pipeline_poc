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
class DcPowerControlProvider(BaseProvider):
    """
    Class that control power of sut for testing

    This class cannot be used directly, instead, this interface is applied to the subclasses, with a different subclass
    communication (SOL, Serial) This makes the dependency on specific hardware setups easier to
    identify.
    """
    DEFAULT_CONFIG_PATH = "suts/sut/providers/dc"
    def __init__(self, cfg_opts, log):
        """
        Create a new PowerControlProvider object

        :param self._log: Logger object to use for debug and info messages
        :param cfg_opts: Dictionary of configuration options for execution environment.
        """
        super(DcPowerControlProvider, self).__init__(cfg_opts, log)

    @abstractmethod
    def dc_power_on(self, timeout=None):
        # type: (int) -> bool
        """
        This API changes SUT from S5 to S0. DO NOT use this API to simulate short press power button to power on SUT.

        :param timeout: seconds. The max time spend for executing DC Power On to SUT enter into OS. It should more than 0. If it is None, API will refer to configuration for the default value.
        :return:
            True    -   if power-on command has been sent successful.
            False   -   if command failed to be sent out.
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise DriverIOError: if command execution failed in driver. Depends on driver it will raised SoundwaveError, RSC2Err, PIError. Anyway, all of them are inherited from DriverIOError.
        :raise TypeError: if input parameter type is not correct
        """
        raise NotImplementedError

    @abstractmethod
    def dc_power_off(self, timeout=None):
        # type: (int) -> bool
        """
        This API changes SUT from S0 to S5. DO NOT use this API to simulate long press power button to shut down SUT.

        :param: timeout, seconds. the max time spend for executing DC Power Off to SUT enter into OS, it should more than 0. If it is None, API will refer to configuration for the default value.
        :return:
            True    -   if power-off command has been sent successfull
            False   -   if command failed to be sent out.
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise DriverIOError: if command execution failed in driver. Depends on driver it will raised SoundwaveError, RSC2Err, PIError. Anyway, all of them are inherited from DriverIOError.
        :raise TypeError: if input parameter type is not correct
        """
        raise NotImplementedError

    @abstractmethod
    def dc_power_reset(self):
        # type: () -> str
        """
        This API reset SUT power. The max time spend for executing DC Power Reset to SUT enter into OS, it should more than 0.

        :return:
                True        : power supply has been reset.
                False       : Fail to send power reset command
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise DriverIOError: if command execution failed in driver. Depends on driver it will raised SoundwaveError, RSC2Err, PIError. Anyway, all of them are inherited from DriverIOError.
        :raise TimeoutException: fail to respond before timeout
        """
        raise NotImplementedError

    @abstractmethod
    def get_dc_power_state(self):
        # type: () -> str
        """
        get dc power state of SUT

        :return:
            True        : AC ON
            None        : AC OFF
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise DriverIOError: if command execution failed in driver. Depends on driver it will raised SoundwaveError, RSC2Err, PIError. Anyway, all of them are inherited from DriverIOError.
        :raise TimeoutException: fail to respond before timeout
        """
        raise Exception


