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
import subprocess
import os
from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.drivers.internal.pi_driver import PiDriver
from dtaf_core.providers.physical_control import PhysicalControlProvider
from dtaf_core.lib.configuration import ConfigurationHelper

class PiPhysicalControlProvider(PhysicalControlProvider, PiDriver):
     """
     This class is used to provide interfaces for the Physical controlling on PI Control box.
     """
     def __init__(self,cfg_opts,log):
          super(PiPhysicalControlProvider, self).__init__(cfg_opts,log)
          
     def __enter__(self):
          return super(PiPhysicalControlProvider, self).__enter__()
        
     def __exit__(self, exc_type, exc_val, exc_tb):
          super(PiPhysicalControlProvider, self).__exit__(exc_type, exc_val, exc_tb)

     def connect_usb_to_sut(self, timeout=None, image=None, username=None, password=None):
          """
          Connect shared USB drive to the system under test.
          :exception Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
          """
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"pi")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                if sw.connect_usb_to_sut():
                    return True
            except Exception as ex:
                self._log.error("pi dc power on error:{}".format(ex))
                raise

     def connect_usb_to_host(self, timeout=None):
          """
          Connect shared USB drive to the lab host.
          :exception Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
          """
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"pi")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                if sw.connect_usb_to_host():
                    return True
            except Exception as ex:
                self._log.error("pi dc power on error:{}".format(ex))
                raise

     def disconnect_usb(self, timeout=None):
          """
          Dis-connect Shared USB drive From SUT.
          :exception Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
          """
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"pi")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                if sw.disconnect_usb():
                    return True
            except Exception as ex:
                self._log.error("pi dc power on error:{}".format(ex))
                raise

     def set_clear_cmos(self, timeout=None):
          """
          Clears the current configured data with factory setting
          :exception Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
          """
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"pi")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                if sw.set_clear_cmos():
                    return True
            except Exception as ex:
                self._log.error("pi dc power on error:{}".format(ex))
                raise
               
     def read_postcode(self):
          # type: () -> hex
          """
          Get the current POST code from the SUT.

          :return: Current POST code of the platform
          """
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"pi")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
               try:
                 ret=sw.read_postcode()
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
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"pi")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
               try:
                 if sw.read_s3_pin():
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
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"pi")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
               try:
                 if sw.read_s4_pin():
                      return True
               except Exception:
                 self._log.error("Read s3 pin volt Failed")
                 raise

     def get_power_state(self):
         """
         :return Actuall state of the platform, combines function of get dc power and ac power
         :exception Banino_Error: Banino Library Throws Error.
         """
         driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                            driver_name=r"pi")
         with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
             try:
                 if sw.get_dc_power_state() == True:
                     flag = "S0"
                 elif sw.get_ac_power_state() != True:
                     flag = "G3"
                 else:
                     flag = "S5"
                 return flag
             except Exception:
                 self._log.error("Program Jumper pin Failed")
                 raise

     def program_jumper(self,state,gpio_pin_number,timeout=None):
          """
          program_jumper controls the gpio pins of raspberry pi
          :param state=set or unset this makes the gpio pin high or low to cmmunicate with the relay
          gpio_pin_number which pins that needs to be programmed 
          :return: True
          :exception Raspberry_Pi_Error: Raspberry Pi Gpio Library Throws Error.
          """
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"pi")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
               try:
                 if sw.program_jumper(state,gpio_pin_number,timeout):
                      return True
               except Exception:
                 self._log.error("Program Jumper pin Failed")
                 raise

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