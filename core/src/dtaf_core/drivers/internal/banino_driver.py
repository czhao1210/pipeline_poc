import os
import sys
import time
import ctypes
from dtaf_core.drivers.base_driver import BaseDriver
from dtaf_core.lib.configuration import ConfigurationHelper

class BaninoDriver(BaseDriver):
    def __init__(self, cfg_opts, log):
        super(BaninoDriver, self).__init__(cfg_opts, log)
        self._power_cmd = self._driver_cfg_model.banino_power_cmd
        self.chip_write_verification_ifwi = self._driver_cfg_model.chip_verification_ifwi
        self.chip_write_verification_bmc = self._driver_cfg_model.chip_verification_bmc
        #dll_path=()
        self.ladybird = ctypes.cdll.LoadLibrary(self._driver_cfg_model.banino_dll_path)
        self.rasp = self._driver_cfg_model.rasp

    def __enter__(self):
        return super(BaninoDriver, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(BaninoDriver, self).__exit__(exc_type, exc_val, exc_tb)

    def conect_relay(self,relay_num, relay_port):
        try:
            relay_state = self.ladybird.GetRelayState(1, relay_num, relay_port)
            self._log.info("Relay_status {0}".format(relay_state))
            if relay_state == 1:
                self._log.info("Relay Connected")
                return True
            else:
                self.ladybird.SetRelayState(1, relay_num, relay_port, 1)
                time.sleep(1)
                relay_state = self.ladybird.GetRelayState(1, relay_num, relay_port)
                if relay_state == 1:
                    self._log.info("Connecting Relay Successful")
                    return True
                else:
                    self._log.error("Connecting Relay Fail")
                    raise
        except Exception as ex:
            self._log.error("Relay Connect Error {0}".format(ex))
            raise

    def conect_relay_custom(self,relay_port):
        """
        SetRelayState(unsigned int baninoNumber, unsigned int relayGroup, unsigned int relayNumber, unsigned int relayState)
        relayGroup 2
        relayNumber 1 - 7
        """
        try:
            relay_state = self.ladybird.GetRelayState(1, 2, relay_port)
            self._log.info("Relay_status {0}".format(relay_state))
            if(relay_state == 1):
                self._log.info("Relay Connected")
                return True
            else:
                self.ladybird.SetRelayState(1, 2, relay_port, 1)
                time.sleep(1)
                relay_state = self.ladybird.GetRelayState(1, 2, relay_port)
                if(relay_state == 1):
                    self._log.info("Connecting Custom Relay Number {0} Successful".format(relay_port))
                    return True
                else:
                    self._log.error("Connecting Custom Relay Number {0} Failed".format(relay_port))
                    raise
        except Exception as ex:
            self._log.error("Custom Relay Connect Error {0}".format(ex))
            raise

    def disconnect_relay_custom(self,relay_port):
        """
        SetRelayState(unsigned int baninoNumber, unsigned int relayGroup, unsigned int relayNumber, unsigned int relayState)
        relayGroup 2
        relayNumber 1 - 7
        """
        try:
            relay_state = self.ladybird.GetRelayState(1, 2, relay_port)
            self._log.info("Relay_status {0}".format(relay_state))
            if(relay_state == 0):
                self._log.info("Relay Disconnected")
                return True
            else:
                self.ladybird.SetRelayState(1, 2, relay_port, 0)
                time.sleep(1)
                relay_state = self.ladybird.GetRelayState(1, 2, relay_port)
                if(relay_state == 0):
                    self._log.info("Disconnecting Custom Relay Number {0} Successful".format(relay_port))
                    return True
                else:
                    self._log.error("Disconnecting Custom Relay Number {0} Failed".format(relay_port))
                    raise
        except Exception as ex:
            self._log.error("Custom Relay Disconnect Error {0}".format(ex))
            raise

    def disconnect_relay(self,relay_num, relay_port):
        try:
            relay_state = self.ladybird.GetRelayState(1, relay_num, relay_port)
            if(relay_state == 0):
                self._log.info("Relay Disconnected")
                return True
            else:
                self.ladybird.SetRelayState(1, relay_num, relay_port, 0)
                time.sleep(1)
                relay_state = self.ladybird.GetRelayState(1, relay_num, relay_port)
                if relay_state == 0:
                    self._log.info("Disconnecting Relay Successful")
                    return True
                else:
                    self._log.error("Disconnecting Relay Fail")
                    raise
        except Exception as ex:
            self._log.error("Relay Disconnect Error {0}".format(ex))
            raise

    def connect_usb_to_sut(self, timeout=None):
        """
        Connect shared USB drive to the system under test.
        :exception Banino_Error: Banino Library Throws Error.
        """
        try:
            self._log.info("start to switch usb disk to sut")
            lbHandle = self.ladybird.OpenByBaninoNumber(1, 2)
            self.ladybird.SetGpioDirection(lbHandle, 1, 0x6000000, 0x6000000)
            self.ladybird.SetGpioState(lbHandle, 1,  0x4000000 , 0x00)
            time.sleep(2)
            self._log.debug("Short Relay_1_4")
            self.ladybird.SetGpioState(lbHandle, 1,  0x2000000, 0x00)
            self.ladybird.SetGpioState(lbHandle, 1, 0x4000000 , 0x4000000)
            time.sleep(3)
            # self.self.ladybird.close(lbHandle)
            return True
        except Exception as ex:
            self._log.error("Switch_Flash_Disk Usb_To_Sut_Failure {0}".format(ex))
            raise

    def connect_usb_to_host(self, timeout=None):
        """
        Connect shared USB drive to the lab host.
        :exception Banino_Error: Banino Library Throws Error.
        """
        try:
            self._log.info("start to switch usb disk to host")
            lbHandle = self.ladybird.OpenByBaninoNumber(1, 2)
            self.ladybird.SetGpioDirection(lbHandle, 1, 0x6000000, 0x6000000)
            self.ladybird.SetGpioState(lbHandle, 1,  0x4000000 , 0x00)
            time.sleep(8)
            self._log.debug("Short Relay_1_4")
            self.ladybird.SetGpioState(lbHandle, 1,  0x2000000, 0x2000000)
            self.ladybird.SetGpioState(lbHandle, 1, 0x4000000 , 0x4000000)
            time.sleep(8)
            # self.self.ladybird.close(lbHandle)
            return True
        except Exception as ex:
            self._log.error("Switch_Flash_Disk Usb_To_Host_Failure {0}".format(ex))
            raise
        
    def disconnect_usb(self, timeout=None):
        """
        Dis-connect USB drive From SUT and Host.
        :exception Banino_Error: Banino Library Throws Error.
        """
        try:
            self._log.info("start to Disconnect switch usb from Host and SUT")
            lbHandle = self.ladybird.OpenByBaninoNumber(1, 2)
            self.ladybird.SetGpioDirection(lbHandle, 1, 0x6000000, 0x6000000)
            self.ladybird.SetGpioState(lbHandle, 1,  0x4000000 , 0x00)
            time.sleep(2)
            self._log.debug("Short Relay_1_4")
            self.ladybird.SetGpioState(lbHandle, 1,  0x00, 0x00)
            time.sleep(3)
            # self.self.ladybird.close(lbHandle)
            return True
        except Exception as ex:
            self._log.error("Switch_Flash_Disk Usb_To_Host_Failure {0}".format(ex))
            raise

    def set_clear_cmos(self, timeout=None):
        """
        Clears the current configured data with factory setting
        :exception Banino_Error: Banino Library Throws Error.
        """
        try:
            if(self.conect_relay(1, 3) != True):
                self._log.error("Short Clear COMS Pin Failed")
                raise
            else:
                self._log.info("Short Clear COMS Pin pass")
            time.sleep(5)
            if(self.disconnect_relay(1, 3) != True):
                self._log.error("Open Clear COMS pin failed")
                raise
            else:
                self._log.info("Open Clear COMS Jumper Connected")
            return True
        except Exception as ex:
            self._log.error("Clear CMOS Failed To Happen {0}".format(ex))
            raise
        
    def dc_power_on(self, timeout=None):
        """
        :send DC_POWER_ON command to Gpio Turn The Relay to go High for Short Duration which physically interact with Front Panel Gpio.
        :return: True or None
        :exception Banino_Error: Banino Library Throws Error.
        """
        try:
            num = 1
            port = 1
            self.ladybird.SetRelayState(1, num, port, 1)
            relay_state = self.ladybird.GetRelayState(1, num, port)
            self._log.info("Short switch power button is {0}".format(relay_state))
            time.sleep(1)
            self.ladybird.SetRelayState(1, num, port, 0)
            time.sleep(1)
            relay_state = self.ladybird.GetRelayState(1, num, port)
            self._log.info("short switch power button is {0}".format(relay_state))
            return True
        except Exception as ex:
            self._log.error("Dc-Power ON via Banino Failed To Happen {0}".format(ex))
            raise
     
    def dc_power_off(self, timeout=None):
        """
        :send DC_POWER_OFF command to Gpio To Turn The Relay to go High which physically interact with Front Panel Gpio.
        :return: True or None
        :exception Banino_Error: Banino Library Throws Error.
        """
        try:
            num = 1
            port = 1
            self.ladybird.SetRelayState(1, num, port, 1)
            relay_state = self.ladybird.GetRelayState(1, num, port)
            self._log.info("short switch power off button is {}".format(relay_state))
            time.sleep(5)
            self.ladybird.SetRelayState(1, num, port, 0)
            time.sleep(1)
            relay_state = self.ladybird.GetRelayState(1, num, port)
            self._log.info("short switch power button is {}".format(relay_state))
            return True
        except Exception as ex:
            self._log.error("Dc-Power OFF via Banino Failed To Happen {0}".format(ex))
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
       :exception Banino_Error: Banino Library Throws Error.
        """
        output = os.popen(str("cd ") + self._power_cmd + str("& SxState.exe")).read()
        power_status = output.strip()
        self._log.info(power_status)
        if(power_status == "S0"):
            self._log.info("S0 State Detected")
            return True
        elif(power_status == "S5"):
            self._log.info("S5 State Detected")

    def get_sx_power_state(self):
        """
        :return Actuall state of the platform, combines function of get dc power and ac power
        :exception Banino_Error: Banino Library Throws Error.
        """
        try:
            output = os.popen(str("cd ") + self._power_cmd + str("& SxState.exe")).read()
            power_status = output.strip()
            self._log.info(power_status)
            return power_status
        except Exception as ex:
            self._log.error("Error Occured During Banino State Detection {0}".format(ex))
            raise

    def dc_power_reset(self):
        """
        :send DC_Reset command to Gpio To Turn The Relay to go High which physically interact with Front Panel Gpio.
        :return: True or None
        :exception Banino_Error: Banino Library Throws Error.
        """
        try:
            num = 1
            port = 2
            self.ladybird.SetRelayState(1, num, port, 1)
            relay_state = self.ladybird.GetRelayState(1, num, port)
            self._log.info("Short switch reset button is {0}".format(relay_state))
            time.sleep(2)
            self.ladybird.SetRelayState(1, num, port, 0)
            time.sleep(2)
            relay_state = self.ladybird.GetRelayState(1, num, port)
            self._log.info("short switch power button is {0}".format(relay_state))
            return True
        except Exception as ex:
            self._log.error("Dc-Power ON via Banino Failed To Happen {0}".format(ex))
            raise

    def read_s3_pin(self):
        # type: () -> bool
        """
        Read the state of the S3 pin
        :return: True if S3 pin is indicating SUT is in S3, None otherwise.
        """
        output = os.popen(str("cd ") + self._power_cmd + str("& SxState.exe")).read()
        power_status = output.strip()
        self._log.info(power_status)
        if(power_status == "S3"):
            self._log.info("S3 State Detected")
            return True
        else:
            self._log.info("S3 State is Not Detected")
       
    def read_s4_pin(self):
        # type: () -> bool
        """
        Read the state of the S4 pin
        :return: True if S4 pin is indicating SUT is in S4, None otherwise.
        """
        output = os.popen(str("cd ") + self._power_cmd + str("& SxState.exe")).read()
        power_status = output.strip()
        self._log.info(power_status)
        if(power_status == "S4"):
            self._log.info("Get S4 State Success")
            return True
        else:
            self._log.info("S4 State is Not Detected")

    def get_ac_power_state(self):
        """
        This API shields platform and control box difference.
        according to the platform setting in Config module,
        which signals' voltage need to be got are different support.
        Power states dependent on platform power schematic.
        :return:
        On      -   True
        Off     -   None
        :exception Banino_Error: Banino Library Throws Error
        """
        output = os.popen(self._power_cmd).read()
        power_status = output.strip()
        self._log.info(power_status)
        if(power_status == "G3"):
            self._log.info("G3 State Detected")
            return True
        else:
            self._log.info("G3 State is Not Detected")

    def program_jumper(self, state, gpio_pin_number, timeout=""):
        """
        program_jumper controls the gpio pins of Banino
        :param timeout:
        :param gpio_pin_number:
        :param state=set or unset this makes the gpio pin high or low to communicate with the relay
        gpio_pin_number which pins that needs to be programmed
        :return: True
        :exception Banino_Error: Banino Gpio Library Throws Error.
        """
        try:
            if(str(state) == "set"):
                if(self.conect_relay_custom(gpio_pin_number) == True):
                    return True
                else:
                    return False
            elif(str(state) == "unset"):
                if (self.disconnect_relay_custom(gpio_pin_number) == True):
                    return True
                else:
                    return False
        except Exception as ex:
            self._log.error("Failed to " + str(state) + " Jumper for Custom Relay Group 2 Channel {0}{1}".format(ex,gpio_pin_number))
            raise
       
    def chip_flash(self, path=None, image_name=None):
        """
        This function takes care of identifying and erasing and writing a new image from a location.
        it takes the ifwi image or the bmc image based on the modification/creation time it is going to take the latest time by default of the image.
        Image for flashing will be taken from the "+str(root)+"/firmware/ folder name is firmware from this the image will be taken.
        path in this are fixed path even though folders don't exists it will created it,2nd time run it will copy them
        """
        if(self.rasp == True):
            self._log.info("Banino is Configured For RASP")
            if self.conect_relay_custom(1) != True:
                self._log.error("connect VCC relay fail, please check the hard connection")
                return False
            if self.conect_relay(1, 5) != True:
                self._log.error("connect VCC relay fail, please check the hard connection")
                return False
        else:
            self._log.info("Banino is Configured For NON-RASP")
            if self.conect_relay_custom(1) != True:
                self._log.error("connect VCC relay fail, please check the hard connection")
                return False
            if self.conect_relay_custom(3) != True:
                self._log.error("connect VCC relay fail, please check the hard connection")
                return False
        try:
            self._log.info("Starting to do Flash IFWI with mentioned Version {0}".format(image_name))
            lbHandle = self.ladybird.OpenByBaninoNumber(1, 3)
            self._log.info("{0}".format(lbHandle))
            flashDevice = 0
            flashStartAddress = 0
            image_namepath = path + image_name
            filePath=ctypes.create_string_buffer(bytes(image_namepath,'utf-8'))
            writeSize = os.path.getsize(filePath.value)
            self._log.info("{0} object, size {1}".format(filePath, writeSize))
            fileOffset = 0
            result = 1
            result = self.ladybird.FlashReady(lbHandle, ctypes.c_char(flashDevice))
            if(result != 0):
                self._log.error("FlashReady:{}, IFWI SPI Chip not Detected".format(result))
                return False
            else:
                self._log.info("FlashReady:{}, IFWI SPI Chip have Detected".format(result))
                
            self._log.info("Start to Erase SPI flash Chip")
            result = self.ladybird.FlashErase(lbHandle, ctypes.c_char(flashDevice))
            if(result != 0):
                self._log.error("FlashErase:{}, Erase IFWI SPI chip Erase fail".format(result))
                return False
            else:
                self._log.info("FlashErase:{}, Erase IFWI chip passed ".format(result))
            self._log.info("Start to Write IFWI file to flash")
            result = self.ladybird.FlashWriteFile(lbHandle, ctypes.c_char(flashDevice), flashStartAddress, writeSize, filePath, fileOffset)
            if(result != 0):
                self._log.error("FlashWriteFile:{}, Burning IFWI SPI chip fail".format(result))
                return False
            else:
                self._log.info("FlashWriteFile:{}, Burning IFWI SPI chip pass".format(result))
            if(self.chip_write_verification_ifwi == False):
                self._log.info("Skipped to Verify SPI IFWI Chip")
            else:
                self._log.info("Start to Verify write file")
                result = self.ladybird.FlashVerifyFile(lbHandle, ctypes.c_char(flashDevice), flashStartAddress, writeSize, filePath, fileOffset)
                if(result != 0):
                    self._log.error("FlashVerifyFile:{}, Verify IFWI SPI chip fail".format(result))
                    return False
                else:
                    self._log.info("FlashVerifyFile:{}, Verify IFWI SPI chip pass".format(result))
            self._log.info("Flash IFWI successful")
            self.ladybird.Close(lbHandle)
            return True
        except Exception as ex:
            self._log.error("Error --> {0}".format(ex))
            return False
        finally:
            if (self.rasp == True):
                if (self.disconnect_relay_custom(1) != True):
                    self._log.error("disconnect VCC relay fail")
                    return False
                if (self.disconnect_relay(1, 5) != True):
                    self._log.error("disconnect VCC relay fail")
                    return False
            else:
                if(self.disconnect_relay_custom(1) != True):
                    self._log.error("disconnect VCC relay fail")
                    return False
                if (self.disconnect_relay_custom( 3) != True):
                    self._log.error("disconnect VCC relay fail")
                    return False

    def chip_flash_bmc(self, path=None, image_name=None):
        """
        This function takes care of identifying and erasing and writing a new image from a location.
        it takes the ifwi image or the bmc image based on the modification/creation time it is going to take the latest time by default of the image.
        Image for flashing will be taken from the "+str(root)+"/firmware/ folder name is firmware from this the image will be taken.
        path in this are fixed path even though folders don't exists it will created it,2nd time run it will copy them
        """
        if (self.rasp == True):
            self._log.info("Banino is Configured For RASP")
            if(self.conect_relay_custom(1) != True):
                self._log.error("connect VCC relay fail, please check the hard connection")
                return False
            if self.conect_relay(1, 5) != True:
                self._log.error("connect VCC relay fail, please check the hard connection")
                return False
        else:
            self._log.info("Banino is Configured For NON-RASP")
            if(self.conect_relay(1, 5) != True):
                self._log.error("connect VCC relay fail, please check the hard connection")
                return False
        try:
            self._log.info("Starting to do Flash BMC with mentioned Version {0}".format(image_name))
            lbHandle = self.ladybird.OpenByBaninoNumber(1, 1)
            flashDevice = 0
            flashStartAddress = 0
            image_namepath = path + image_name
            filePath=ctypes.create_string_buffer(bytes(image_namepath,'utf-8'))
            writeSize = os.path.getsize(filePath.value)
            self._log.info("{0} object, size {1}".format(filePath, writeSize))
            fileOffset = 0
            result = 1
            result = self.ladybird.FlashReady(lbHandle, ctypes.c_char(flashDevice))
            if(result != 0):
                self._log.error("FlashReady:{}, BMC Chip not Detectected".format(result))
                return False
            else:
                self._log.info("FlashReady:{}, BMC Chip have Detected".format(result))
            self._log.info("Start to Erase flash")
            result = self.ladybird.FlashErase(lbHandle, ctypes.c_char(flashDevice))
            if(result != 0):
                self._log.error("FlashErase:{}, Erase bmc chip Erase fail".format(result))
                return False
            else:
                self._log.info("FlashErase:{}, Erase bmc chip passed ".format(result))
            self._log.info("Start to Write BMC file to flash")
            result = self.ladybird.FlashWriteFile(lbHandle, ctypes.c_char(flashDevice), flashStartAddress, writeSize, filePath, fileOffset)
            if(result != 0):
                self._log.error("FlashWriteFile:{}, Burning bmc chip fail".format(result))
                return False
            else:
                self._log.info("FlashWriteFile:{}, Burning bmc chip pass".format(result))
            if (self.chip_write_verification_bmc == False):
                self._log.info("Skipped to Verify SPI BMC Chip")
            else:
                self._log.info("Start to Veritfy write file")
                result = self.ladybird.FlashVerifyFile(lbHandle, ctypes.c_char(flashDevice), flashStartAddress, writeSize,
                                                       filePath, fileOffset)
                if (result != 0):
                    self._log.error("FlashVerifyFile:{}, Verify BMC chip fail".format(result))
                    return False
                else:
                    self._log.info("FlashVerifyFile:{}, Verify BMC chip pass".format(result))
            self._log.info("Flash BMC successfully verified")
            self.ladybird.Close(lbHandle)
            return True
        except Exception as ex:
            self._log.error("Error --> {0}".format(ex))
            return False
        finally:
            if (self.rasp == True):
                if (self.disconnect_relay_custom(1) != True):
                    self._log.error("disconnect VCC relay fail")
                    return False
                if (self.disconnect_relay(1, 5) != True):
                    self._log.error("disconnect VCC relay fail")
                    return False
            else:
                if(self.disconnect_relay(1, 5) != True):
                    self._log.error("disconnect VCC relay fail")
                    return False
