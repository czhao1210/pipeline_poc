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


class State(object):
    """
    Class State includes Env State and Power State
    """
    def __init__(self, env_state, power_state):
        super(State, self).__init__()
        self.__env_state = env_state
        self.__power_state = power_state

    @property
    def env_state(self):
        return self.__env_state

    @env_state.setter
    def env_state(self, value):
        self.__env_state = value
        return self.__env_state

    @property
    def power_state(self):
        return self.__power_state

    @power_state.setter
    def power_state(self, value):
        self.__power_state = value
        return self.__power_state


class StateTransition(object):
    """
    This class provides a series of APIs to switch state gracefully. It is expected to be used in the scenarios which user doesn't case how to change the state.
    """
    def __init__(self, cfg_opts, logger):
        super(StateTransition, self).__init__()

    def switch_state(self, start_state, end_state, timeout=None):
        # type: (State, State, float) -> bool
        """
        Gracefully switch SUT state from <start_state> to <end_state>

        :param start_state: State object which specifies both env state and power state
        :param end_state: State object which specifies both env state and power state
        :param timeout: Estimation of State Transition. If it is None, the value in configuration will be used
        :return: True / False
        :raise CommunicationException: no response from SUT during communication
        :raise HardwareException: Hardware Issue
        :raise NotImplementedError: The transition is not supported.
        """
        raise NotImplementedError

    def move_to(self, end_state, timeout=None):
        # type: (State, float) -> bool
        """
        Gracefully move SUT state <end_state> regardless of the current state

        :param end_state: State object which specifies both env state and power state
        :param timeout: Estimation of State Transition. If it is None, the value in configuration will be used
        :return: True / False
        :raise CommunicationException: no response from SUT during communication
        :raise HardwareException: Hardware Issue
        :raise NotImplementedError: The transition is not supported.
        """
        raise NotImplementedError

    def get_state(self):
        # type: () -> State
        """
        get current state of SUT

        :return: State to specify both Power State and Env State
        :raise CommunicationException: no response from SUT during communication
        :raise HardwareException: Hardware Issue
        """
        raise NotImplementedError
