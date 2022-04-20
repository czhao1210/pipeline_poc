#!/usr/bin/env python
#################################################################################
# INTEL CONFIDENTIAL
# Copyright Intel Corporation All Rights Reserved.
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material may contain trade secrets and proprietary
# and confidential information of Intel Corporation and its suppliers and
# licensors, and is protected by worldwide copyright and trade secret laws and
# treaty provisions. No part of the Material may be used, copied, reproduced,
# modified, published, uploaded, posted, transmitted, distributed, or disclosed
# in any way without Intel's prior express written permission.
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
#################################################################################
import time
import pyttk
import thread
import requests
import subprocess
from dtaf_core.drivers.base_driver import BaseDriver
from dtaf_core.lib.configuration import ConfigurationHelper

class TTKDriver(BaseDriver):
    def __init__(self, cfg_opts, log):
        super(TTKDriver, self).__init__(cfg_opts, log)
        self._localhost = self._driver_cfg_model.localhost

    def __enter__(self):
        return super(TTKDriver, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(TTKDriver, self).__exit__(exc_type, exc_val, exc_tb)

    def ac_power_on(self, timeout=None):
        """
        :send AC_POWER_ON command to Gpio To Turn The Relay Connect The Front Panle Gpio.
        :return: True or None
        :exception
        TTK_Error: TTK Gpio Library Throws Error.
        """

        try:
            aServer = pyttk.Server(self._localhost)
            aDevice = aServer.getDevices()[0]
            if aDevice.getStateSwitch(1)[1] == 0:
                self._log.info("Original state: AC off")
                aDevice.acon()
            while True:
                if aDevice.getStateSwitch(1)[1] == 1:
                    return True
                else:
                    self._log.error("AC Power is still OFF")
                    time.sleep(1)
        except Exception as ex:
            self._log.error("Ac-Power ON via TTK Failed To Happen {0}".format(ex))
            raise

    def ac_power_off(self, timeout=None):
        """
        :send AC_POWER_OFF command to Gpio To Turn The Relay Connect The Front Panle Gpio.
        :return: True or None
        :exception
        TTK_Error: TTK Gpio Library Throws Error.
        """
        try:
            aServer = pyttk.Server(self._localhost)
            aDevice = aServer.getDevices()[0]
            if aDevice.getStateSwitch(1)[1] == 1:
                ## power is now on
                self._log.info("Attempt to power off AC")
                aDevice.acoff()
            ## If power is on, turn it off.
            while True:
                if aDevice.getStateSwitch(1)[1] == 0:
                    return True
                else:
                    self._log.error("AC Power is still ON")
                time.sleep(1)
        except Exception as ex:
            self._log.error("Ac-Power OFF via TTK Failed To Happen {0}".format(ex))
            raise

    def get_ac_power_state(self):
        """
        This API shields platform and control box difference.
        according to the platform setting in Config module,
        which signals' voltage need to be got are different support.
        Power states dependent on platform power schematic.
        :return:
        On      -   True
        Off     -   None
        :raise TTKError:  Hardware Error from TTK Driver
        """
        raise NotImplementedError


    def dc_power_on(self, timeout=None):
        """
        :send DC_POWER_ON command to Gpio Turn The Relay to go High which physically interact with Front Panel Gpio.
        :return: True or None
        :exception
            TTKError:  ttk Driver Error.
        """
        try:
            aServer = pyttk.Server(self._localhost)
            aDevice = aServer.getDevices()[0]
            if aDevice.getFrontPanelStatus()[1] == 0:
                aDevice.pulsePower(200)
                time.sleep(1)
            while True:
                if aDevice.getFrontPanelStatus()[1] == 1:
                    self._log.info("DC Power is Turned ON")
                    return True
                else:
                    self._log.error("DC Power is still OFF")
                time.sleep(1)
        except Exception as ex:
            self._log.error("Dc-Power ON via TTK Failed To Happen {0}".format(ex))
            raise

    def dc_power_off(self, timeout=None):
        """
        :send DC_POWER_OFF command to Gpio To Turn The Relay to go Low which physically interact with Front Panel Gpio.
        :return: True or None
        :exception
            TTKError: TTK Driver Error.
        """
        try:
            aServer = pyttk.Server(self._localhost)
            aDevice = aServer.getDevices()[0]
            if aDevice.getFrontPanelStatus()[1] == 1:
                aDevice.pulsePower(5000)
                time.sleep(1)
            ## power off the front panel if it is on.
            while True:
                if aDevice.getFrontPanelStatus()[1] == 0:
                    self._log.info("DC Power is OFF")
                    return True
                else:
                    self._log.error("DC Power is still On")
        except Exception as ex:
            self._log.error("Dc-Power ON via TTK Failed To Happen {0}".format(ex))
            raise

    def get_dc_power_state(self):
        """
        This API shields platform and control box difference.
        according to the platform setting in Config module,
        which signals' voltage need to be got are different support.
        Power states dependent on platform power schematic.
        :return:
        On      -   True
        Off     -   NONE
        TTkError: TTK Driver Error.
        """
        raise NotImplementedError

    def dc_power_reset(self):
        """
        :send DC_Reset command to Gpio To Turn The Relay to go High which physically interact with Front Panel Gpio.
        :return: True or None
        :exception
        TTKError: TTK Driver Error.
        """
        raise NotImplementedError

    def printMsg(self,duration):
        for x in range(duration, 0, -1):
            print("Clearing CMOS in " + str(x) + " seconds")
            time.sleep(1)

    def set_clear_cmos(self, timeout=None):
        """
        Clears the current configured data with factory setting
        :exception TTK_Error: TTK Gpio Library Throws Error.
        """
        try:
            aServer = pyttk.Server(self._localhost)
            ## your server may have multiple devices, this code should be updated to get the right device (instead of just first device)
            ## we assume that the first device is able to perform clear CMOS
            aDevice = aServer.getDevices()[0]
            thread.start_new_thread(self.printMsg, (3,))
            aDevice.clearCMOS()
            time.sleep(5)
            thread.start_new_thread(self.printMsg, (5,))
            aDevice.clearCMOS(5)
            self._log.info("Clear CMOS Performed")
            return True
        except Exception as ex:
            self._log.error("Clear-Cmos Failed To Happen {0}".format(ex))
            raise

    def read_postcode(self):
        # type: () -> hex
        """
        Get the current POST code from the SUT.

        :return: Current POST code of the platform
        """
        try:
            aServer = pyttk.Server(self._localhost)
            aDevice = aServer.getDevices()[0]
            r = aDevice.getMCUPort80("TumaloFalls")
            if (r[1][1] < 16):
                ret=("0" + "%x" % (r[1][1]))
            else:
                ret=("%x" % (r[1][1]))
            return ret
        except Exception as ex:
            self._log.error("Couldn't Read Post Code MCU Port80 Failure {0}".format(ex))
            raise

    def program_jumper(self, state, gpio_pin_number, pinstate=None,timeout=""):
        """
        program_jumper controls the gpio pins of ttk
        :param timeout:
        :param gpio_pin_number:
        :param state=set or unset this makes the gpio pin high or low to communicate with the relay
        gpio_pin_number which pins that needs to be programmed
        :return: True
        :exception TTK_Error: ttk Gpio Library Throws Error.
        """
        direction=state
        pinState=gpio_pin_number
        try:
            aServer = pyttk.Server(self._localhost)
            aDevice = aServer.getDevices()[0]
            direction = [1]
            pinState = [0]
            pinPosition = [0]
            aDevice.setGPIO(0, direction, pinState, pinPosition)
            direction = [0, 1, 1]
            pinState = [0, 1, 0]
            pinPosition = [1, 2, 3]
            aDevice.setGPIO(0, direction, pinState, pinPosition)
            ## Read all GPIO
            direc, state = aDevice.getGPIO(0)
            tempValue = (0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x40, 0x80)
            for i in range(len(tempValue)):
                if (direc & tempValue[i] == tempValue[i]):
                    if (state & tempValue[i] == tempValue[i]):
                        self._log.info("GPIO " + str(i) + ": High")
                    else:
                        self._log.info("GPIO " + str(i) + ": Low")
                else:
                    self._log.info("GPIO " + str(i) + ": Input")
            return True
        except Exception as ex:
            self._log.error("Failed to " + str(state) + " Jumper {0}".format(ex))
            raise