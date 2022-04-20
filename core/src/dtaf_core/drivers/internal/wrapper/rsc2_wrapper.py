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
import argparse
import os
import time

from dtaf_core.collateral.rsc2 import rsc2


class RscWrapper(object):

    AC_SETTLE_TIME = 40
    CMOS_CLEAR_TIME = 10
    CMOS_RELEASE_JMP_TIME = 2

    def __init__(self):
        # Connect to local RSC2
        self._rsc2 = rsc2
        self._host = self._rsc2.Host('localhost')
        if self._host.getNumBoxes() != 1:
            raise IOError("Unable to connect to the RSC2. Boxes detected = " + str(self._host.getNumBoxes()))
        self._box = self._host.getBox(0)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._box.setUsbMux(self._rsc2.MUX_DISCONNECTED)

    def press_power_button(self, *arg_list):
        """
        press power button
        :param arg_list:
        :return:
        """
        print("Power Button Press {}".format(float(arg_list[0])))
        button = self._box.getSignal(self._rsc2.ID_FPBUT_PWR)
        button.setSigAssertionState(self._rsc2.BUTTON_PRESSED)
        if arg_list:
            time.sleep(float(arg_list[0]))
        button.setSigAssertionState(self._rsc2.BUTTON_RELEASED)
        print("Power button pressed.")
        return True

    def press_reset_button(self, *arg_list):
        """
        press reset button
        :param arg_list:
        :return:
        """
        button = self._box.getSignal(self._rsc2.ID_FPBUT_RESET)
        button.setSigAssertionState(self._rsc2.BUTTON_PRESSED)
        button.setSigAssertionState(self._rsc2.BUTTON_RELEASED)
        print("Reset button pressed.")
        return True

    def remove_power(self, *arg_list):
        """
        remove power
        :param arg_list:
        :return:
        """
        button = self._box.getSignal(self._rsc2.ID_AC_1)
        button.setSigAssertionState(self._rsc2.ACTIVE_LOW)
        button = self._box.getSignal(self._rsc2.ID_AC_2)
        button.setSigAssertionState(self._rsc2.ACTIVE_LOW)
        print("AC power removed.")
        return True

    def connect_power(self, *arg_list):
        """
        connect power
        :param arg_list:
        :return:
        """
        button = self._box.getSignal(self._rsc2.ID_AC_1)
        button.setSigAssertionState(self._rsc2.ACTIVE_HIGH)
        button = self._box.getSignal(self._rsc2.ID_AC_2)
        button.setSigAssertionState(self._rsc2.ACTIVE_HIGH)
        print("AC power connected.")

    def ac_connected(self, *arg_list):
        """
        check ac connection
        :param arg_list:
        :return:
        """
        ac1 = self._box.getSignal(self._rsc2.ID_AC_1)
        ac2 = self._box.getSignal(self._rsc2.ID_AC_2)
        result = ac1.getSigAssertionState() == self._rsc2.AC_ON and ac2.getSigAssertionState() == self._rsc2.AC_ON
        print("rsc2_return_bool={}".format(result))
        return result  # This doesn't actually matter for the wrapper, the previous line is the real return value.

    def _press_clear_cmos_button(self, *arg_list):
        if self.ac_connected():
            raise self._rsc2.RscException("Device is not powered down - cannot clear CMOS.")

        cmos_button = self._box.getSignal(self._rsc2.ID_JMP_CLR_CMOS)
        cmos_button.setSigAssertionState(self._rsc2.BUTTON_PRESSED)
        self.connect_power()
        time.sleep(self.CMOS_CLEAR_TIME)
        self.remove_power()
        time.sleep(self.AC_SETTLE_TIME)
        cmos_button.setSigAssertionState(self._rsc2.BUTTON_RELEASED)
        time.sleep(self.CMOS_RELEASE_JMP_TIME)
        print("CMOS cleared.")

    def clear_cmos(self, *arg_list):
        """
        clear cmos
        :param arg_list:
        :return:
        """
        boot_delay = float(arg_list[0])  # Parse boot_delay from string argument
        print("Remove power from the SUT")
        self.remove_power()
        time.sleep(self.AC_SETTLE_TIME)

        print("Clear CMOS")
        self._press_clear_cmos_button()

        print("Connect power to the SUT and wait " + str(boot_delay) + " seconds for system to boot")
        self.connect_power()
        time.sleep(boot_delay)

    def connect_usb_to_sut(self, *arg_list):
        """
        connect usb to sut
        :param arg_list:
        :return:
        """
        self._box.setUsbMux(self._rsc2.MUX_TO_SUT)

    def connect_usb_to_host(self, *arg_list):
        """
        connect usb to host
        :param arg_list:
        :return:
        """
        self._box.setUsbMux(self._rsc2.MUX_TO_HOST)

    def disconnect_usb(self, *arg_list):
        """
        disconnect usb
        :param arg_list:
        :return:
        """
        self._box.setUsbMux(self._rsc2.MUX_DISCONNECTED)

    def _read_led(self, led):
        result = self._box.getSignal(led).getSigAssertionState() == self._rsc2.LED_ON
        print("rsc2_return_bool={}".format(result))
        return result  # This doesn't actually matter for the wrapper, the previous line is the real return value.

    def read_power_led(self):
        """
        read power led
        :return:
        """
        return self._read_led(self._rsc2.LED_ON)

    def read_green_status_led(self):
        """
        read green status led
        :return:
        """
        return self._read_led(self._rsc2.ID_LED_STATUS_GREEN)

    def read_amber_status_led(self):
        """
        read amber status led
        :return:
        """
        return self._read_led(self._rsc2.ID_LED_STATUS_AMBER)

    def read_id_led(self):
        """
        read id led
        :return:
        """
        return self._read_led(self._rsc2.ID_LED_ID_BLUE)


if __name__ == "__main__":
    ARG_PARSER = argparse.ArgumentParser()
    ARG_PARSER.add_argument('function_name', help="RscProvider function to call")
    ARG_PARSER.add_argument('function_args', nargs=argparse.REMAINDER,
                            help="Arguments to pass to called function (see RscProvider interface)")
    ARGUMENTS = ARG_PARSER.parse_args()
    try:
        RSC_WRAPPER = RscWrapper()
        getattr(RSC_WRAPPER, ARGUMENTS.function_name)(*ARGUMENTS.function_args)
        os._exit(0)
    except Exception as general_exception:
        print("Failed to execute function " + str(ARGUMENTS.function_name) + " with arguments " + str(ARGUMENTS.function_args))
        print(general_exception)
        raise
