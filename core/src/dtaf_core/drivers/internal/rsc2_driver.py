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
RSC2 Driver Layer
"""
import re
import subprocess
import time
from abc import ABCMeta, abstractmethod
from os import linesep
from os.path import dirname, join

import six

from dtaf_core.drivers.base_driver import BaseDriver


class RscDriverException(Exception):
    """Exception for when RSC fails to execute the requested command."""
    pass


@six.add_metaclass(ABCMeta)
class BaseRsc2Driver(BaseDriver):
    """
    Wrapper interface for working with the RSC2 Python library.

    PhysicalControlProvider and PowerControlProvider
    use this driver to implement their interfaces with RSC2.
    """

    __rsc_instance = None  # RscProvider is a singleton class

    def __init__(self, cfg_opts, log):
        super(BaseRsc2Driver, self).__init__(cfg_opts, log)

    @abstractmethod
    def press_power_button(self):
        """
        Press the SUT's 'Front Panel Power' button.

        :raises RscDriverException: If RSC fails to execute the requested command.
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def press_reset_button(self):
        """
        Press the SUT's 'Front Panel Reset' button.

        :raises RscDriverException: If RSC fails to execute the requested command.
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def press_id_button(self):
        """
        Press the SUT's 'Front Panel ID' button.

        :raises RscDriverException: If RSC fails to execute the requested command.
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def remove_power(self):
        """
        Remove AC Power from the SUT.

        :raises RscDriverException: If RSC fails to execute the requested command.
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def connect_power(self):
        """
        Connect AC power to the SUT.

        :raises RscDriverException: If RSC fails to execute the requested command.
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def ac_connected(self):
        """
        Checks if AC power is currently connected to the device.

        :raises RscDriverException: If RSC fails to execute the requested command.
        :return: True if AC power is connected, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def connect_usb_to_sut(self):
        """
        Connect shared USB drive to the system under test.

        :raises RscDriverException: If RSC fails to execute the requested command.
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def connect_usb_to_host(self):
        """
        Connect shared USB drive to the lab host.

        :raises RscDriverException: If RSC fails to execute the requested command.
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def disconnect_usb(self):
        """
        Disconnect shared USB drive from both the SUT and host.

        :raises RscDriverException: If RSC fails to execute the requested command.
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def read_power_led(self):
        """
        Get the current state of the Power LED.

        :raises RscDriverException: If RSC fails to execute the requested command.
        :return: True if the Power LED is on, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def read_green_status_led(self):
        """
        Get the current state of the green Status LED.

        :raises RscDriverException: If RSC fails to execute the requested command.
        :return: True if the green Status LED is on, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def read_amber_status_led(self):
        """
        Get the current state of the amber Status LED.

        :raises RscDriverException: If RSC fails to execute the requested command.
        :return: True if the amber Status LED is on, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def read_id_led(self):
        """
        Get the current state of the blue ID LED.

        :raises RscDriverException: If RSC fails to execute the requested command.
        :return: True if the ID LED is on, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def set_jumper(self, jumper, state):
        """
        Set an RSC2 jumper output to On or Off.

        :raises KeyError: If jumper is not configured.
        :raises RscDriverException: If RSC fails to execute the requested command.
        :param jumper: Jumper (one of lib.jumpers.Jumpers) to set.
        :param state: If true, will set jumper to ON. Otherwise, set it to OFF.
        :return: None
        """
        raise NotImplementedError


class Rsc2Driver(BaseRsc2Driver):
    """
    Provides platform control through the RSC2 Python library running on the local machine.
    """

    __rsc_jumper_mapping = None

    def __init__(self, cfg_opts, log):
        super(Rsc2Driver, self).__init__(cfg_opts, log)
        dirname(__file__)
        join(dirname(__file__), r"wrapper", r"rsc2_wrapper.py")
        self.wrapper_script = join(dirname(__file__), "wrapper", r"rsc2_wrapper.py")


    def __call_wrapper(self, name, *args):
        # Assemble script command
        cmd = ["py", "-2", self.wrapper_script, name]
        if args is not None:
            cmd.extend(map(str, args))

        # Execute command
        try:
            cmd_output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as call_error:
            self._log.error("Failed first try of RSC2 {} command through wrapper, "
                            "trying again in 5 seconds {}".format(name, call_error))
            time.sleep(5.0)
            cmd_output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)

        # Grab output from the file
        # This will need to be extended to check multiple regexes per line
        # if any non-boolean return types are added
        result = None
        if six.PY2:
            cmd_output = cmd_output.decode('utf-8').split(linesep)
        if six.PY3:
            cmd_output = str(cmd_output, 'utf-8').split(linesep)

        for line in cmd_output:
            self._log.debug("RSC2 Wrapper Output: {}".format(line))
            matched_result = re.match(r"rsc2_return_bool=(True|False)$", line)
            if matched_result and result is None:
                result = matched_result.group(1) == "True"
            elif matched_result and result is not None:
                raise RscDriverException("RSC2 wrapper script returned multiple values!!")

        return result

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def press_power_button(self, power_button_down):
        """
        press power button
        :param power_button_down: timeout ot keep the button press
        :return:
        """
        return self.__call_wrapper("press_power_button {}".format(power_button_down))

    def press_reset_button(self):
        return self.__call_wrapper("press_reset_button")

    def press_id_button(self):
        raise NotImplementedError

    def remove_power(self):
        return self.__call_wrapper("remove_power")

    def connect_power(self):
        return self.__call_wrapper("connect_power")

    def ac_connected(self):
        cmd_result = self.__call_wrapper("ac_connected")
        if cmd_result is None:
            raise RscDriverException("Did not receive output from RSC wrapper script!")
        return cmd_result


    def connect_usb_to_sut(self):
        return self.__call_wrapper("connect_usb_to_sut")

    def connect_usb_to_host(self):
        return self.__call_wrapper("connect_usb_to_host")

    def disconnect_usb(self):
        return self.__call_wrapper("disconnect_usb")

    def __read_led(self, led):
        raise NotImplementedError

    def read_power_led(self):
        cmd_result = self.__call_wrapper("read_power_led")
        if cmd_result is None:
            raise RuntimeError("Did not receive output from RSC wrapper script!")
        print("read power led={}".format(cmd_result))
        return cmd_result

    def read_green_status_led(self):
        raise NotImplementedError

    def read_amber_status_led(self):
        cmd_result = self.__call_wrapper("read_amber_status_led")
        if cmd_result is None:
            raise RuntimeError("Did not receive output from RSC wrapper script!")
        return cmd_result


    def read_id_led(self):
        cmd_result = self.__call_wrapper("read_id_led")
        if cmd_result is None:
            raise RuntimeError("Did not receive output from RSC wrapper script!")
        return cmd_result

    def set_jumper(self, jumper, state):
        raise NotImplementedError

    def set_clear_cmos(self, timeout=None):
        raise NotImplementedError
