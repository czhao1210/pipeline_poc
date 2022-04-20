#!/usr/bin/env python
"""
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
from dtaf_core.providers.physical_control import PhysicalControlProvider
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.drivers.internal.banino_driver import BaninoDriver
from dtaf_core.drivers.driver_factory import DriverFactory

class BaninoPhysicalControlProvider(PhysicalControlProvider, BaninoDriver):
     def __init__(self, log, cfg_opts):
        super(BaninoPhysicalControlProvider, self).__init__(cfg_opts,log)

     def __enter__(self):
        return super(BaninoPhysicalControlProvider, self).__enter__()

     def __exit__(self, exc_type, exc_val, exc_tb):
        super(BaninoPhysicalControlProvider, self).__exit__(exc_type, exc_val, exc_tb)
         
     def connect_usb_to_sut(self,timeout=None, image=None, username=None, password=None):
        """
        Connect shared USB drive to the system under test.

        :exception Banino_Error: Banino Library Throws Error.
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,driver_name=r"banino")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
             try:
                if sw.connect_usb_to_sut():
                    return True
             except Exception as ex:
                self._log.error("Banino USB Switch To Sut Error:{}".format(ex))
                raise

     def connect_usb_to_host(self,timeout=None):
        """
        Connect shared USB drive to the lab host.
        :exception Banino_Error: Banino Library Throws Error.
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,driver_name=r"banino")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
             try:
                if sw.connect_usb_to_host():
                     return True
             except Exception as ex:
                self._log.error("Banino USB Switch To Host Error:{}".format(ex))
                raise

     def disconnect_usb(self,timeout=None):
        """
        Dis-Connect USB drive From Both Host and the system under test.
        :exception Banino_Error: Throws Error.
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,driver_name=r"banino")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
             try:
                if sw.disconnect_usb():
                     return True
             except Exception as ex:
                self._log.error("Banino USB Disconnect Error:{}".format(ex))
                raise
            
     def set_clear_cmos(self,timeout=None):
        """
        Clears the current configured data with factory setting 
        :exception Banino_Error: Banino Gpio Library Throws Error.
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,driver_name=r"banino")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
             try:
                if sw.set_clear_cmos():
                     return True
             except Exception as ex:
                self._log.error("Banino Clear_Cmos Error:{}".format(ex))
                raise
               
     def read_postcode(self):
          # type: () -> hex
          """
          Get the current POST code from the SUT.

          :return: Current POST code of the platform
          """
          raise NotImplementedError

     def read_s3_pin(self):
          # type: () -> None
          """
          Read the state of the S3 pin
          :return: True if S3 pin is indicating SUT is in S3, False otherwise.
          """
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,driver_name=r"banino")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
             try:
                if sw.read_s3_pin():
                     return True
             except Exception as ex:
                self._log.error("Banino Clear_Cmos Error:{}".format(ex))
                raise

     def read_s4_pin(self):
          # type: () -> None
          """
          Read the state of the S4 pin
          :return: True if S4 pin is indicating SUT is in S4, False otherwise.
          """
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,driver_name=r"banino")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
             try:
                if sw.read_s4_pin():
                     return True
             except Exception as ex:
                self._log.error("Banino Clear_Cmos Error:{}".format(ex))
                raise

     def get_power_state(self):
         """
         Read the state of the platform
         :return: Acutal state value instead of bool, hence S0 or S5 or G3.
         """
         driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"banino")
         with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
             try:
                 sx=sw.get_sx_power_state()
                 if sx == "S1":
                     return "S1"
                 else:
                     return sx
             except Exception as ex:
                 self._log.error("Error Occured During Banino State Detection {0}".format(ex))
                 raise

     def program_jumper(self,state,gpio_pin_number,timeout=None):
          """
          program_jumper controls the gpio pins of raspberry pi
          :param state=set or unset this makes the gpio pin high or low to cmmunicate with the relay
          gpio_pin_number which pins that needs to be programmed 
          :return: True
          :exception Banino_Error: Library Throws Error.
          """
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                             driver_name=r"banino")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
              try:
                  if sw.program_jumper(state, gpio_pin_number, timeout):
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

     def update_configuration(self, update_cfg_opts, update_log):
         super(BaninoPhysicalControlProvider, self).update_configuration(update_cfg_opts=update_cfg_opts, update_log=update_log)
         self.__init__(cfg_opts=update_cfg_opts, log=update_log)

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