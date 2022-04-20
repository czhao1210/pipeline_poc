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

import subprocess
import time
from dtaf_core.providers.ac_power import AcPowerControlProvider
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.drivers.base_driver import BaseDriver


class RaspberryDriver(BaseDriver):
    def __init__(self, log, cfg_opts):
        super(RaspberryDriver, self).__init__(cfg_opts, log)
        self._cfg = cfg_opts
        self.__logger = log

    def __enter__(self):
        return super(RaspberryDriver, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(RaspberryDriver, self).__exit__(exc_type, exc_val, exc_tb)

    def ac_power_on(self, timeout=None):
        """
        :send AC_POWER_ON command to Gpio To Turn The Relay Connect The Front Panle Gpio.
        :return: True or None
        :exception
        Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
        """
        try:
            ret = subprocess.check_output("curl -X GET http://" + self._driver_cfg_model.ip + "/acpower/1", shell=True)
            if b"Power Turned ON and Verified" in ret:
                return True
        except Exception:
            self._log.error("Ac-Power ON via R-pi Failed To Happen")
            raise

    def ac_power_off(self, timeout=None):
        """
        :send AC_POWER_OFF command to Gpio To Turn The Relay Connect The Front Panle Gpio.
        :return: True or None
        :exception
        Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
        """
        try:
            ret = subprocess.check_output("curl -X GET http://" + self._driver_cfg_model.ip + "/acpower/0", shell=True)
            if b"Power Turned OFF and Verified" in ret:
                return True
        except Exception:
            self._log.error("Ac-Power OFF via R-pi Failed To Happen")
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
        :raise RaspberrypiError:  Hardware Error from soundwave driver
        """
        try:
            ret = subprocess.check_output("curl -X GET http://" + self._driver_cfg_model.ip + "/acdetect", shell=True)
            if b"AC power detected" in ret:
                return True
        except Exception:
            self._log.error("Ac-Power OFF via R-pi Failed To Happen")
            raise

    def dc_power_on(self, timeout=None):
        """
        :send DC_POWER_ON command to Gpio Turn The Relay to go High which physcialy interact with Front Panel Gpio.
        :return: True or None
        :exception
            FlaskError: Raspberry Pi Flask Error.
        """
        try:
            ret = subprocess.check_output("curl -X GET http://" + self._driver_cfg_model.ip + "/dcpower/1", shell=True)
            if b"Dc Power Turned ON and Verfied" in ret:
                return True
        except Exception:
            self._log.error("Dc-Power ON via R-pi Failed To Happen")
            raise

    def dc_power_off(self, timeout=None):
        """
        :send DC_POWER_OFF command to Gpio To Turn The Relay to go Low which physcialy interact with Front Panel Gpio.
        :return: True or None
        :exception
            FlaskError: Raspberry Pi Flask Error.
        """
        try:
            ret = subprocess.check_output("curl -X GET http://" + self._driver_cfg_model.ip + "/dcpower/0", shell=True)
            if b"DC Power Turned OFF and Verified" in ret:
                return True
        except Exception:
            self._log.error("Dc-Power ON via R-pi Failed To Happen")
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
        FlaskError: Raspberry Pi Flask Error.
        """
        try:
            ret = subprocess.check_output("curl -X GET http://" + self._driver_cfg_model.ip + "/dcdetect", shell=True)
            if b"DC power detected" in ret:
                return True
        except Exception:
            self._log.error("Dc-Power ON via R-pi Failed To Happen")
            raise

    def dc_power_reset(self):
        """
        :send DC_Reset command to Gpio To Turn The Relay to go High which physcialy interact with Front Panel Gpio.
        :return: True or None
        :exception
        FlaskError: Raspberry Pi Flask Error.
        """
        try:
            ret = subprocess.check_output("curl -X GET http://" + self._driver_cfg_model.ip + "/reboot", shell=True)
            if b"Reboot Command Issued" in ret:
                return True
        except Exception:
            self._log.error("Dc-Reset via R-pi Failed To Happen")
            raise

    def connect_usb_to_sut(self, timeout=None):
        """
        Connect shared USB drive to the system under test.
        :exception Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
        """
        try:
            ret = subprocess.check_output("curl -X GET http://" + self._driver_cfg_model.ip + "/usb2sut", shell=True)
            if b"USB Switch to SUT Done" in ret:
                return True
        except Exception:
            self._log.error("switch_flash_disk Usb_To_sut_Failure")
            raise

    def connect_usb_to_host(self, timeout=None):
        """
        Connect shared USB drive to the lab host.
        :exception Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
        """
        try:
            ret = subprocess.check_output("curl -X GET http://" + self._driver_cfg_model.ip + "/usb2host", shell=True)
            if b"USB Switch to Host Done" in ret:
                return True
        except Exception:
            self._log.error("switch_flash_disk Usb_To_Host_Failure")
            raise

    def disconnect_usb(self, timeout=None):
        """
        Dis-connect Shared USB drive From SUT.
        :exception Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
        """
        try:
            ret = subprocess.check_output("curl -X GET http://" + self._driver_cfg_model.ip + "/usbdiscnt", shell=True)
            if b"USB Disconnect Done" in ret:
                return True
        except Exception:
            self._log.error("Dis-Connect USB Faield To Happen")
            raise

    def set_clear_cmos(self, timeout=None):
        """
        Clears the current configured data with factory setting
        :exception Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
        """
        try:
            ret = subprocess.check_output("curl -X GET http://" + self._driver_cfg_model.ip + "/clearcmos", shell=True)
            if b"ClearCmos Command Issued" in ret:
                return True
        except Exception:
            self._log.error("Clear-Cmos Failed To Happen")
            raise

    def read_post_code(self):
        # type: () -> hex
        """
        Get the current POST code from the SUT.

        :return: Current POST code of the platform
        """
        try:
            ret = subprocess.check_output("curl -X GET http://" + self._driver_cfg_model.ip + "/postcode", shell=True)
            if ret.isdigit():
                return ret
        except Exception:
            self._log.error("Couldn't Read Post Code SmBus Failure")
            raise

    def read_s3_pin(self):
        # type: () -> None
        """
        Read the state of the S3 pin
        :return: True if S3 pin is indicating SUT is in S3, False otherwise.
        """
        try:
            ret = subprocess.check_output("curl -X GET http://" + self._driver_cfg_model.ip + "/s3detect", shell=True)
            if b"S3 power detected" in ret:
                return True
        except Exception:
            self._log.error("Read s3 pin volt Failed")
            raise

    def read_s4_pin(self):
        # type: () -> None
        """
        Read the state of the S4 pin
        :return: True if S4 pin is indicating SUT is in S4, False otherwise.
        """
        try:
            ret = subprocess.check_output("curl -X GET http://" + self._driver_cfg_model.ip + "/s4detect", shell=True)
            if b"S4 power detected" in ret:
                return True
        except Exception:
            self._log.error("Read S4 pin volt Failed")
            raise

    def program_jumper(self, state, gpio_pin_number, timeout=""):
        """
        program_jumper controls the gpio pins of raspberry pi
        :param state=set or unset this makes the gpio pin high or low to cmmunicate with the relay
        gpio_pin_number which pins that needs to be programmed
        :return: True
        :exception Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
        """
        try:
            ret = subprocess.check_output("curl -X GET http://" + self._driver_cfg_model.ip + "/progjmpr/", shell=True)
            if b"Jumper set Done" or "Jumper unset Done" in ret:
                return True
        except Exception:
            self._log.error("Failed to " + str(state) + " Jumper")
            raise
