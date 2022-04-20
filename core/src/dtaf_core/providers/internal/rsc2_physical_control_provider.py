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
from datetime import datetime
import time
from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.providers.physical_control import PhysicalControlProvider
from dtaf_core.lib.configuration import ConfigurationHelper

class Rsc2PhysicalControlProvider(PhysicalControlProvider):
    def __init__(self, cfg_opts, log):
        super(Rsc2PhysicalControlProvider, self).__init__(cfg_opts, log)
        self.__driver = DriverFactory.create(
            cfg_opts=ConfigurationHelper.get_driver_config(provider=cfg_opts, driver_name=r"rsc2"),
            logger=log)
        
    def __enter__(self):
        return super(Rsc2PhysicalControlProvider, self).__enter__()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        super(Rsc2PhysicalControlProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def connect_usb_to_sut(self,timeout):
        """
        Connect shared USB drive to the system under test.

        :exception RSC2_Error: Throws Error.
        """
        try:
            self.__driver.connect_usb_to_sut()
            now = datetime.now()
            if timeout is None:
                timeout = int(self._config_model.usb_switch_timeout)
                time.sleep(timeout)
            if not isinstance(timeout, int):
                raise AttributeError(r"Timeout value is not correctly set. It should be configured in  "
                                     r"either XML file or the input parameter list of function.")
            self.__driver.connect_usb_to_sut()
            return True
        except Exception as ex:
            self._log.error(r'switch_flash_disk Usb_To_Sut_Failure')
            raise
    

    def connect_usb_to_host(self,timeout):
        """
        Connect shared USB drive to the system under test.

        :exception RSC2_Error: Throws Error.
        """
        try:
            self.__driver.connect_usb_to_host()
            now = datetime.now()
            if timeout is None:
                timeout = int(self._config_model.usb_switch_timeout)
                time.sleep(timeout)
            if not isinstance(timeout, int):
                raise AttributeError(r"Timeout value is not correctly set. It should be configured in  "
                                     r"either XML file or the input parameter list of function.")
            self.__driver.connect_usb_to_host()
            return True
        except Exception as ex:
            self._log.error(r'switch_flash_disk Usb_To_Host_Failure')
            raise

    def disconnect_usb(self,timeout):
        """
        Dis-Connect USB drive From Both Host and the system under test.

        :exception RSC2_Error: Throws Error.
        """
        try:
            self.__driver.disconnect_usb()
            now = datetime.now()
            if timeout is None:
                timeout = self.__config_model.poweroff_timeout
                time.sleep(timeout)
            if not isinstance(timeout, int):
                raise AttributeError(r"Timeout value is not correctly set. It should be configured in  "
                                     r"either XML file or the input parameter list of function.")
            self.__driver.disconnect_usb()
            return True
        except Exception as ex:
            self._log.error(r'Disconnect Pendrive Failed To Happen')
            raise
            
    def set_clear_cmos(self,timeout=""):
        """
        Clears the current configured data with factory setting 
        
        :exception RSC2_Error: Throws Error.
        Not implemented as yet
        """
        pass

    def read_s4_pin(self):
        """
        Read the state of the S4 pin
        
        :return: True if S4 pin is indicating SUT is in S4, None otherwise.
        """
        raise NotImplementedError

    def read_s3_pin(self):
        # type: () -> None
        """
        Read the state of the S3 pin
        
        :return: True if S3 pin is indicating SUT is in S3,None otherwise.
        """
        raise NotImplementedError
    
    def read_postcode(self):
        """
        Reads Platform Postcode via LPC bus interface via GPIO
        
        :return: postcode or None
        """
        raise NotImplementedError

    def program_jumper(self):
        # type: () -> None
        """
        Programs ControlBox Jumper to perform actions on the Platform
        
        :return: True Or None
        """
        raise NotImplementedError

    def get_power_state(self):
        """
        :return Actuall state of the platform, combines function of get dc power and ac power
        :exception Banino_Error: Banino Library Throws Error.
        """
        # raise NotImplementedError
        return self.__driver.get_power_state()

    def get_platform_volt(self):
        # type: () -> bool
        """
        :return actual dc volt of the platform index[0] True index[1] dc_volt
        :exception redfish error: Redfish driver throws error
        """
        raise NotImplementedError

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
        # type: () -> bool
        """
        :return actual dc volt of the platform index[0] True index[1] dc_volt
        :exception redfish error: Redfish driver throws error
        """
        raise NotImplementedError

    def platform_health_status(self):
        """
        :return actual dc volt of the platform index[0] True index[1] dc_volt
        :exception redfish error: Redfish driver throws error
        """
        raise NotImplementedError

    def get_bmc_mac(self):
        """
        :return BMC Mac address of the platform index[0] True index[1] mac id
        :exception redfish error: Redfish driver throws error
        """
        raise NotImplementedError
