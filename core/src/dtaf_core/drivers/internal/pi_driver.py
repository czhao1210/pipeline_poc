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
import paramiko
import platform
import requests
import subprocess
from dtaf_core.drivers.base_driver import BaseDriver
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.ac_power import AcPowerControlProvider

class PiDriver(BaseDriver):

    def __init__(self, cfg_opts, log):
        super(PiDriver, self).__init__(cfg_opts, log)
        self._user = self._driver_cfg_model.username
        self._ip = self._driver_cfg_model.ip
        self._password = self._driver_cfg_model.password
        self._type = self._driver_cfg_model.type

    def __enter__(self):
        return super(PiDriver, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(PiDriver, self).__exit__(exc_type, exc_val, exc_tb)

    def execute(self, cmd="", Timeout=None):
        """
        This Function is a workaround function for communicating with SUT via SSH or serial.
        To make the Bios Knob Change Happen from The Os Level.
        """
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(self._ip, port=22, username=self._user, password=self._password)
            ssh_session = ssh_client.get_transport().open_session()
            if ssh_session.active:
                stdout = ""
                stderr = ""
                stdin, stdout, stderr = ssh_client.exec_command(cmd)
                # received_output=ssh_session.recv(9000)
                stdout = stdout.readlines()
                stderr = stderr.readlines()
                if stdout:
                    self._log.info("=========== >>> got the output", ''.join(stdout))
                    return True
                elif stderr:
                    self._log.error("=========== >>> captured the error", ''.join(stderr))
                    return False
            else:
                self._log.error("SSH not their use microsoft openssh to refer P4V configure it")
        except Exception as e:
            self._log.error("connection didn't happen", e)

        finally:
            try:
                ssh_client.close()
            except:
                pass


    def ac_power_on(self, timeout=None):
        """
        :send AC_POWER_ON command to Gpio To Turn The Relay Connect The Front Panle Gpio.
        :return: True or None
        :exception
        Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
        """
        if(self._driver_cfg_model.type == "aurora"):
            if(PiDriver.execute("gpio_control 19 out 1") == True):
                return True
            else:
                return False
        else:
            try:
                url = "curl -X GET http://" + self._driver_cfg_model.ip + "/acpower/1/" + str(int(timeout))

                if self._driver_cfg_model.proxy:
                    url += ' -x ' + self._driver_cfg_model.proxy

                ret = subprocess.check_output(url, shell=True)
                if b"Power Turned ON and Verified" in ret:
                    return True
            except Exception as ex:
                self._log.error("Ac-Power ON via R-pi Failed To Happen {0}".format(ex))
                raise

    def ac_power_off(self, timeout=None):
        """
        :send AC_POWER_OFF command to Gpio To Turn The Relay Connect The Front Panle Gpio.
        :return: True or None
        :exception
        Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
        """
        if (self._driver_cfg_model.type == "aurora"):
            if (PiDriver.execute("gpio_control 19 out 0") == True):
                return True
            else:
                return False
        else:
            try:
                url = "curl -X GET http://" + self._driver_cfg_model.ip + "/acpower/0/" + str(int(timeout))
                if self._driver_cfg_model.proxy:
                    url += ' -x ' + self._driver_cfg_model.proxy

                ret = subprocess.check_output(url, shell=True)
                if b"Power Turned OFF and Verified" in ret:
                    return True
            except Exception as ex:
                self._log.error("Ac-Power OFF via R-pi Failed To Happen {0}".format(ex))
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
        :raise RaspberrypiError:  Hardware Error from pi driver
        """
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/acdetect"
            if self._driver_cfg_model.proxy:
                url += ' -x ' + self._driver_cfg_model.proxy
            ret = subprocess.check_output(url, shell=True)
            if b"AC power detected" in ret:
                return True
        except Exception as ex:
            self._log.error("Ac-Power OFF via R-pi Failed To Happen {0}".format(ex))
            raise

    def dc_power_on(self, timeout=None):
        """
        :send DC_POWER_ON command to Gpio Turn The Relay to go High which physically interact with Front Panel Gpio.
        :return: True or None
        :exception
            FlaskError: Raspberry Pi Flask Error.
        """
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/dcpower/1/" + str(int(timeout))
            if self._driver_cfg_model.proxy:
                url += ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            if b"Dc Power Turned ON and Verfied" in ret:
                return True
        except Exception as ex:
            self._log.error("Dc-Power ON via R-pi Failed To Happen {0}".format(ex))
            raise

    def dc_power_off(self, timeout=None):
        """
        :send DC_POWER_OFF command to Gpio To Turn The Relay to go Low which physically interact with Front Panel Gpio.
        :return: True or None
        :exception
            FlaskError: Raspberry Pi Flask Error.
        """
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/dcpower/0/" + str(int(timeout))
            if self._driver_cfg_model.proxy:
                url += ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            if b"DC Power Turned OFF and Verified" in ret:
                return True
        except Exception as ex:
            self._log.error("Dc-Power ON via R-pi Failed To Happen {0}".format(ex))
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
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/dcdetect"
            if self._driver_cfg_model.proxy:
                url += ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            if b"DC power detected" in ret:
                return True
        except Exception as ex:
            self._log.error("Dc-Power ON via R-pi Failed To Happen {0}".format(ex))
            raise

    def dc_power_reset(self):
        """
        :send DC_Reset command to Gpio To Turn The Relay to go High which physically interact with Front Panel Gpio.
        :return: True or None
        :exception
        FlaskError: Raspberry Pi Flask Error.
        """
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/reboot"
            if self._driver_cfg_model.proxy:
                url += ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            if b"Reboot Command Issued" in ret:
                return True
        except Exception as ex:
            self._log.error("Dc-Reset via R-pi Failed To Happen {0}".format(ex))
            raise

    def connect_usb_to_sut(self, timeout=None):
        """
        Connect shared USB drive to the system under test.
        :exception Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
        """
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/usb2sut"
            if self._driver_cfg_model.proxy:
                url += ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            if b"USB Switch to SUT Done" in ret:
                return True
        except Exception as ex:
            self._log.error("switch_flash_disk Usb_To_sut_Failure {0}".format(ex))
            raise

    def connect_usb_to_host(self, timeout=None):
        """
        Connect shared USB drive to the lab host.
        :exception Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
        """
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/usb2host"
            if self._driver_cfg_model.proxy:
                url += ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            if b"USB Switch to Host Done" in ret:
                return True
        except Exception as ex:
            self._log.error("switch_flash_disk Usb_To_Host_Failure {0}".format(ex))
            raise

    def disconnect_usb(self, timeout=None):
        """
        Dis-connect USB drive From SUT and Host.
        :exception Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
        """
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/usbdiscnt"
            if self._driver_cfg_model.proxy:
                url += ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            if b"USB Disconnect Done" in ret:
                return True
        except Exception as ex:
            self._log.error("Dis-Connect USB Faield To Happen {0}".format(ex))
            raise

    def set_clear_cmos(self, timeout=None):
        """
        Clears the current configured data with factory setting
        :exception Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
        """
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/clearcmos"
            if self._driver_cfg_model.proxy:
                url += ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            if b"ClearCmos Command Issued" in ret:
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
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/postcode"
            if self._driver_cfg_model.proxy:
                url += ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            # if ret.isdigit():
            return ret
        except Exception as ex:
            self._log.error("Couldn't Read Post Code SmBus Failure {0}".format(ex))
            raise

    def read_s3_pin(self):
        # type: () -> bool
        """
        Read the state of the S3 pin
        :return: True if S3 pin is indicating SUT is in S3, False otherwise.
        """
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/s3detect"
            if self._driver_cfg_model.proxy:
                url += ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            if b"S3 power detected" in ret:
                return True
        except Exception as ex:
            self._log.error("Read s3 pin volt Failed {0}".format(ex))
            raise

    def read_s4_pin(self):
        # type: () -> bool
        """
        Read the state of the S4 pin
        :return: True if S4 pin is indicating SUT is in S4, False otherwise.
        """
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/s4detect"
            if self._driver_cfg_model.proxy:
                url += ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            if b"S4 power detected" in ret:
                return True
        except Exception as ex:
            self._log.error("Read S4 pin volt Failed {0}".format(ex))
            raise

    def program_jumper(self, state, gpio_pin_number, timeout=""):
        """
        program_jumper controls the gpio pins of raspberry pi
        :param timeout:
        :param gpio_pin_number:
        :param state=set or unset this makes the gpio pin high or low to communicate with the relay
        gpio_pin_number which pins that needs to be programmed
        :return: True
        :exception Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
        """
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/progjmpr/" + str(state) + "/" + str(
                gpio_pin_number) + "/" + str(timeout)
            if self._driver_cfg_model.proxy:
                url += ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            print(ret)
            if b"Jumper set Done" in ret:
                return True
            elif b"Jumper unset Done" in ret:
                return True
        except Exception as ex:
            self._log.error("Failed to " + str(state) + " Jumper {0}".format(ex))
            raise

    def chip_identify(self):
        """
        this is to identify the chip name and the size of the chip and company that manufactured this chip
        identifies the chip whether it is getting detected and supported for flashing using spi interface or not
        chips size that supports 8mb,16mb,32mb,64mb chips are supported from all major manufacturers
        :raises FlashProgrammerException: If image flashing fails.
        :return: True,Flash Chip Name,Manufacturer Name,Size of the CHIP or False,Not Detected 
        """
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/identify_chip"
            if self._driver_cfg_model.proxy:
                url += ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            self._log.info(ret)
            if b"True" in ret:
                return ret
        except Exception as ex:
            self._log.error("Failed to Detect Flash Chip {0}".format(ex))
            raise

    def chip_reading(self):
        """
        this is to identify the chip name and the size of the chip and company that manufactured this chip
        identifies the chip whether it is getting detected and supported for flashing using spi interface or not
        chips size that supports 8mb,16mb,32mb,64mb chips are supported from all major manufacturers
        :raises FlashProgrammerException: If image flashing fails.
        :return: True,Flash Chip Name,Manufacturer Name,Size of the CHIP or False,Not Detected 
        """
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/read_chip"
            if self._driver_cfg_model.proxy:
                url += ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            self._log.info(ret)
            if b"True" in ret:
                return ret
        except Exception as ex:
            self._log.error("Failed to Detect Flash Chip {0}".format(ex))
            raise

    def chip_flash(self, path=None, image_name=None):
        """
        This function takes care of identifying and erasing and writing a new image from a location.
        it takes the ifwi image or the bmc image based on the modification/creation time it is going to take the latest time by default of the image.
        Image for flashing will be taken from the "+str(root)+"/firmware/ folder name is firmware from this the image will be taken.
        path in this are fixed path even though folders don't exists it will created it,2nd time run it will copy them
        """
        # uploading img_from windows to rpi flashing location
        if path:
            path = path
        else:
            path = self._driver_cfg_model.image_path

        try:
            if str(platform.architecture()).find("WindowsPE") != -1:
                url = r"curl -T " + str(path) + "\\" + str(
                    image_name) + " -X POST http://" + self._driver_cfg_model.ip + "/img_upload/"
            elif str(platform.architecture()).find(r"ELF") != -1:
                url = "curl -T " + str(path) + "/" + str(
                    image_name) + " -X POST http://" + self._driver_cfg_model.ip + "/img_upload/"
                url += ' -x ' + self._driver_cfg_model.proxy
            else:
                self._log.error("Url not specified")
                return False
            try:
                ret = subprocess.check_output(url, shell=True)
                if b"Completed" in ret:
                    self._log.info("Uploading Flashing Image {0} To Rpi Was Successful".format(image_name))
            except subprocess.CalledProcessError as e:
                self._log.error(e.output)
        except Exception as ex:
            self._log.error("Unable To Upload Flashing {0} Image File {1}".format(image_name, ex))
            return None
        self._log.info("Flashing Of IFWI-Image {0} Is In-Progress".format(image_name))
        try:
            if image_name:
                url=  "http://" + self._driver_cfg_model.ip + "/write_chip/" + str(image_name)
            else:
                url = "http://" + self._driver_cfg_model.ip + "/write_chip/"
            response = requests.get(url)
            self._log.info(response.content)
            if b"True" in response.content:
                return True
        except Exception as ex:
            self._log.error("Failed to Detect Flash Chip {0}".format(ex))
            raise
