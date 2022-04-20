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
from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.drivers.internal.redfish_driver import RedfishDriver
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.physical_control import PhysicalControlProvider

class RedfishPhysicalControlProvider(PhysicalControlProvider, RedfishDriver):
    """
    This class is used to provide interfaces for the Physical controlling on PI Control box.
    """

    def __init__(self, cfg_opts, log):
        super(RedfishPhysicalControlProvider, self).__init__(cfg_opts, log)

    def __enter__(self):
        return super(RedfishPhysicalControlProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(RedfishPhysicalControlProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def connect_usb_to_sut(self,timeout=None, image=None, username=None, password=None):
        """
        Connect shared USB drive to the system under test.
        :exception Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"redfish")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                ret = sw.insert_virtual_media(image,username, password, None, None, None, None)
                if (ret[0] == True):
                    return True
            except Exception as ex:
                self._log.error("Insert virtual media failed.")
                return False

    def connect_usb_to_host(self, timeout=None):
        """
        Connect shared USB drive to the lab host.
        :exception Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
        """
        raise NotImplementedError

    def disconnect_usb(self, timeout=None):
        """
        Dis-connect Shared USB drive From SUT.
        :exception Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"redfish")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                ret = sw.eject_virtual_media()
                if (ret[0] == True):
                    return True
            except Exception as ex:
                self._log.error("Eject virtual media failed.")
                return False

    def set_clear_cmos(self, timeout=None):
        """
        Clears the current configured data with factory setting
        :exception Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"redfish")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                if(sw.clear_cmos() == True):
                    return True
                else:
                    return False
            except Exception as ex:
                self._log.error("Redfish Based Factory Bios Setting Default error:{}".format(ex))
                return False

    def read_postcode(self):
        # type: () -> hex
        """
        Get the current POST code from the SUT.

        :return: Current POST code of the platform
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"redfish")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                ret = sw.platform_postcode()
                if (ret[0] == True):
                    return True, ret[1]
            except Exception as ex:
                self._log.error("Redfish Based Reading Platform post error:{}".format(ex))
                return False

    def read_s3_pin(self):
        # type: () -> None
        """
        Read the state of the S3 pin
        :return: True if S3 pin is indicating SUT is in S3, False otherwise.
        """
        raise NotImplementedError

    def read_s4_pin(self):
        # type: () -> None
        """
        Read the state of the S4 pin
        :return: True if S4 pin is indicating SUT is in S4, False otherwise.
        """
        raise NotImplementedError

    def get_voltages(self, namelist):
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"redfish")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            voltages = sw.read_voltages()
            ret_volts = dict()
            if namelist is None:
                return voltages
            for name in namelist:
                ret_volts[name] = voltages.get(name)
            return ret_volts


    def get_power_state(self):
        """
        :return Actuall state of the platform, combines function of get dc power and ac power
        :exception Banino_Error: Banino Library Throws Error.
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"redfish")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                ret = sw.get_dc_power_state()
                if (ret == True ):
                    return "S0"
                elif(ret == False):
                    return "S5"
                else:
                    return "N/A"
            except Exception as ex:
                self._log.error("Redfish Based Reading Platform Volt error:{}".format(ex))
                return False


    def program_jumper(self, state, gpio_pin_number, timeout=None):
        """
        program_jumper controls the gpio pins of raspberry pi
        :param state=set or unset this makes the gpio pin high or low to cmmunicate with the relay
        gpio_pin_number which pins that needs to be programmed
        :return: True
        :exception Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
        """
        raise NotImplementedError

    def get_platform_volt(self):
        """
        :return actual dc volt of the platform index[0] True index[1] dc_volt
        :exception redfish error: Redfish driver throws error
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"redfish")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                ret = sw.read_volt()
                if (ret[0] == True):
                    return True, ret[1]
            except Exception as ex:
                self._log.error("Redfish Based Reading Platform Volt error:{}".format(ex))
                return False

    def enable_usb_ports(self, *port):
        # type: () -> bool
        """
        :return actual dc volt of the platform index[0] True index[1] dc_volt
        :exception redfish error: Redfish driver throws error
        """
        self._log.error("Applicable only for Ykush Device")
        return True

    def disable_usb_ports(self, *port):
        # type: () -> bool
        """
        :return actual dc volt of the platform index[0] True index[1] dc_volt
        :exception redfish error: Redfish driver throws error
        """
        self._log.error("Applicable only for Ykush Device")
        return True

    def get_system_id(self):
        """
        :return actual manufacturer name, Model, ChassisType,SerialNumber,PartNumber
        :exception redfish error: Redfish driver throws error
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"redfish")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                ret = sw.get_system_info()
                if (ret[0] == True):
                    return True, ret[1]
            except Exception as ex:
                self._log.error("Redfish Based Getting platform Details FAILED error:{}".format(ex))
                return False

    def platform_health_status(self):
        """
         :return Platform Health of Memory Processor OverAll Health Critical ok Warning amber Green amber-blink
         :exception redfish error: Redfish driver throws error
         """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"redfish")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                ret = sw.get_system_status_led()
                if (ret[0] == True):
                    return True, ret[1]
            except Exception as ex:
                self._log.error("Redfish Based Getting platform Health Led Status Details FAILED error:{}".format(ex))
                return False

    def get_bmc_mac(self):
        """
        :return Platform BMC Mac id
        :exception error: User has not give the platform mac id
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"redfish")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                ret = sw.get_platform_bmc_mac()
                if (ret[0] == True):
                    return ret[1]
                elif(ret[0] ==  False):
                    return "N/A"
            except Exception as ex:
                self._log.error("Failed to get BMC MAC ADDRESS Details FAILED error:{}".format(ex))
                return False