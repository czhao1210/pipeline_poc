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
import six
import time
from datetime import datetime
from dtaf_core.drivers.internal.soundwave2k_driver import Soundwave2kDriver
from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.physical_control import PhysicalControlProvider
from xml.etree import ElementTree as ET


class Soundwave2kPhysicalControlProvider(PhysicalControlProvider):
     def __init__(self,cfg_opts,log):
          self.__main_port = None
          super(Soundwave2kPhysicalControlProvider, self).__init__(cfg_opts,log)

     def __enter__(self):
          return super(Soundwave2kPhysicalControlProvider, self).__enter__()

     def __exit__(self, exc_type, exc_val, exc_tb):
          super(Soundwave2kPhysicalControlProvider, self).__exit__(exc_type, exc_val, exc_tb)

     def connect_usb_to_sut(self,timeout=None, image=None, username=None, password=None):
        """
        API to  Connect shared USB drive to the system under test.

        :param timeout: wait dc power state change until timeout
        :return: True / False
        :raise SoundWaveError:  Hardware Error from soundwave driver
        :raise TypeError: incorrect type of timeout
        """
        if timeout is None:
            timeout = int(self._config_model.usbswitch_timeout)
            time.sleep(timeout)
        driver_cfg = None
        if isinstance(self._cfg, ET.Element):
            driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                               driver_name=r"soundwave2k")
        elif isinstance(self._cfg, dict):
            driver_cfg = self._cfg["driver"]
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
             try:
                  sw.usb_to_port_b()
                  return True
             except Exception:
                  self._log.error(r'switch flash disk to sut error end')
                  raise
             finally:
                  sw.close()

     def connect_usb_to_host(self,timeout=None):
        """
        Connect shared USB drive to the lab host.
        :param timeout: wait dc power state change until timeout
        :return: True / False
        :raise SoundWaveError:  Hardware Error from soundwave driver
        :raise TypeError: incorrect type of timeout
        """
        if timeout is None:
            timeout = int(self._config_model.usbswitch_timeout)
            time.sleep(timeout)
        driver_cfg = None
        if isinstance(self._cfg, ET.Element):
            driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                               driver_name=r"soundwave2k")
        elif isinstance(self._cfg, dict):
            driver_cfg = self._cfg["driver"]['soundwave2k']
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
             try:
                  sw.usb_to_port_a()
                  return True
             except Exception:
                  self._log.error(r'switch flash disk to host error end')
                  raise
             finally:
                  sw.close()

     def disconnect_usb(self, timeout=None):
        """
        Dis-connect Shared USB drive From SUT.
        :param timeout: wait dc power state change until timeout
        :return: True / False
        :raise SoundWaveError:  Hardware Error from soundwave driver
        :raise TypeError: incorrect type of timeout
        """
        if timeout is None:
            timeout = int(self._config_model.usbswitch_timeout)
            time.sleep(timeout)
        driver_cfg = None
        if isinstance(self._cfg, ET.Element):
            driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                               driver_name=r"soundwave2k")
        elif isinstance(self._cfg, dict):
            driver_cfg = self._cfg["driver"]['soundwave2k']
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
             try:
                  sw.usb_to_open()
                  return True
             except Exception:
                  self._log.error(r'switch flash disk to host error end')
                  raise
             finally:
                  sw.close()

     def set_clear_cmos(self,timeout=None,fp_port=None):
        """
        Clears the current configured data with factory setting 
        :param timeout: wait dc power state change until timeout,fp_port which port it is
        :return: True / False
        :raise SoundWaveError:  Hardware Error from soundwave driver
        :raise TypeError: incorrect type of timeout
        """
        if timeout:
            timeout=int(timeout)
        else:
            timeout=3
        driver_cfg = None
        if isinstance(self._cfg, ET.Element):
            driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                               driver_name=r"soundwave2k")
        elif isinstance(self._cfg, dict):
            driver_cfg = self._cfg["driver"]['soundwave2k']
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
             try:
                 if fp_port is None:
                     fp_p= int(self._config_model.clearcmosportnumber)
                 else:
                     fp_p=2
                 cr = sw.ctr_fp_two_ways_switch(int(fp_p),0)
                 if cr == False:
                     self._log.error(r' CMOS_CLEAR on switch error')
                 time.sleep(int(timeout))
                 cr = sw.ctr_fp_two_ways_switch(int(fp_p),1)
                 if cr == False:
                     self._log.error(r' CMOS_CLEAR off switch error')
                 self._log.debug(r'cmos clear sucessfully')
                 return True
             except Exception:
                 self._log.error(r'cmos_clear error end')
                 raise
             finally:
                 sw.close()

     def read_s4_pin(self):
        # type: () -> None
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
        # type: () -> None
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
         raise NotImplementedError

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
