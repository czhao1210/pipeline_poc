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
class AcPowerControlProvider(BaseProvider):
    """
    Class that control power of sut for testing

    This class cannot be used directly, instead, this interface is applied to the subclasses, with a different subclass
    communication (SOL, Serial) This makes the dependency on specific hardware setups easier to
    identify.
    """
    DEFAULT_CONFIG_PATH = "suts/sut/providers/ac"
    def __init__(self, cfg_opts, log):
        """
        Create an instance of AC power control

        :param cfg_opts: Configuration Object of provider
        :param log: Log object
        """
        super(AcPowerControlProvider, self).__init__(cfg_opts, log)

    @abstractmethod
    def ac_power_on(self, timeout=None):
        # type: (int) -> bool
        """
        This API changes SUT from G3 to S0/S5. API will not check the initial state of SUT. It just sends signal.

        :param timeout: the max time spend for executing AC_Power_On to SUT enter into S0/S5, it should more than 0. If it is None, API will refer to configuration for the default value.
        :return:
                True        :AC power supply has been connected.
                False       : Fail to send power on command
        :raise DriverIOError: if command execution failed in driver
        """
        raise NotImplementedError

    @abstractmethod
    def ac_power_off(self, timeout=None):
        # type: (int) -> str
        """
        This API will change SUT from S5/S0 to G3.
        It will check if the entrance state is S5 and if the final state is G3.

        :param: timeout  :second, the max time spend for executing AC_power_off to SUT enter into G3, it should more than 0. If it is None, API will refer to configuration for the default value.
        :return:
                True        :AC power supply has been removed.
                False       : Fail to send power off command
        :raise DriverIOError: if command execution failed in driver
        :raise TimeoutException: fail to respond before timeout

        """
        raise NotImplementedError

    @abstractmethod
    def get_ac_power_state(self):
        # type: () -> str
        """
        Get AC power state of SUT.

        :return:
            On      -   AC On
            Off     -   AC Off
            Unknown -   Unknown State
        :raise DriverIOError: if command execution failed in driver
        :raise TimeoutException: fail to respond before timeout
        """
        raise NotImplementedError

    @abstractmethod
    def set_username_password(self,channel=None,username=None,password=None):
        # type: (None) -> str
        """
        For Security Reason socket are controlled with username and Password
        :param: username needs to be given for the pdu secure login identification purpose
                password for verfication of the username exists
                channel which power socket on the PDU needs to be controlled
        :return:
            True    -   Password was set successfully.
            None    -   password failed to get set
        :raise DriverIOError: if command execution failed in driver
        :raise TimeoutException: fail to respond before timeout
        """
        raise NotImplementedError
        
    @abstractmethod
    def reset_username_password(self,channel=None,master_passkey=None):
        # type: (None) -> str
        """
        Reset Forgotten UserName and Password for PDU sockets
        
        Incase the user forgets username and password to override it from the API level

        :param channel which power socket on the PDU needs to be controlled
               masterkey which has super user access to override the existing username and password
        :return:
            True     -   if the reset of Username and Password was reset
            None     -   Unable to Do the restting of the username and password
        :raise PDUPIError:  Hardware Error from pi driver
        """
        raise NotImplementedError
