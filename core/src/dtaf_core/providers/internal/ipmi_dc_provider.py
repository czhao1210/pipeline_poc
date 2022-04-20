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
from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.drivers.internal.ipmi_driver import IpmiDriver
from dtaf_core.providers.dc_power import DcPowerControlProvider

class IpmiDcProvider(DcPowerControlProvider,IpmiDriver):
     def __init__(self,cfg_opts,log):
          super(IpmiDcProvider, self).__init__(cfg_opts,log)

     def __enter__(self):
          return super(IpmiDcProvider, self).__enter__()

     def __exit__(self, exc_type, exc_val, exc_tb):
          super(IpmiDcProvider, self).__exit__(exc_type, exc_val, exc_tb)

     def dc_power_on(self,timeout=None):
          """
          :send DC_POWER_ON command to Turn the platform on loads up the post code.
          :return: True or None
          :exception
          Error: BMC Ipmi Error.
          """
          if timeout is None:
               timeout = self._config_model.poweron_timeout
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,driver_name=r"ipmi")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
               try:
                    if sw.dc_power_on(timeout):
                         return True
                    else:
                         return False
               except Exception as ex:
                    self._log.error("BMC IPMI DC power On error:{}".format(ex))
                    raise

     def dc_power_off(self,timeout=None):
          """
          :send DC_POWER_OFF command to  To Turn The Relay Connect The Front Panle .
          :return: True or None
          :exception
            IPMI_Error: BMC IPMI Library Throws Error.
          """
          if timeout is None:
               timeout = self._config_model.poweroff_timeout
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,driver_name=r"ipmi")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
               try:
                    if sw.dc_power_off(timeout):
                         return True
                    else:
                         return False
               except Exception as ex:
                    self._log.error("BMC IPMI DC power Off error:{}".format(ex))
                    raise

     def get_dc_power_state(self):
          """
          Detect Dc power state on the SUT
          :return True if dc power is detected or None if not detected. 
          :exception IPMI_Error: IPMI Library Throws Error.
          """
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,driver_name=r"ipmi")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
               try:
                    if (sw.get_dc_power_state() == True):
                         return True
                    else:
                         return False
               except Exception as ex:
                    self._log.error("BMC IPMI DC power State Detection error:{}".format(ex))
                    raise

     def dc_power_reset(self):
          """
          Reboots The platform.
          :exception IPMI_Error: IPMI Library Throws Error.
          """
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,driver_name=r"ipmi")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
               try:
                    if sw.dc_power_reset():
                        return True
               except Exception as ex:
                    self._log.error("BMC IPMI Platform Reboot error:{}".format(ex))
                    raise

     #Cleanup required from here

     def get_sensor_data(self):
          """
          Get platform sensor data using ipmitool
          :return Sensor data
          """
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"ipmi")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
               sensor_data = sw.execute("sensor").split(b'\n')
               return sensor_data

     def get_bmc_lan(self):
          """
          Get BMC info to read IP address
          :return: BMC IP address
          """
          # channel 3 is dedicated BMC lan port
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"ipmi")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
               try:
                    bmc_ip = ""
                    bmc_lan = sw.execute("lan print 3").split(b'\n')
                    for each in bmc_lan:
                         each = each.split(b':')
                         if (b'IP Address' == each[0].strip()):
                              bmc_ip_addr = each[1].strip()
                              bmc_ip = bmc_ip_addr.decode('UTF-8')
               except RuntimeError as e:
                    self._log.exception(e)
               return bmc_ip

     def get_bmc_version(self):
          """
          Get BMC version
          :return: BMC version
          """
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"ipmi")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
               try:
                    version = sw.execute("bmc info").split(b'\n')
                    if ('Firmware Revision' not in version):
                         raise RuntimeError("Failed to discover a BMC firmware version in the BMC response")
                    version = version.split(b'\n')[2]
                    return version.split(b':')[1]
               except RuntimeError as e:
                    self._log.exception(e)

     def get_device_id(self):
          """
          Get BMC device ID
          :return Device ID
          """
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"ipmi")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
               try:
                    device_id = sw.execute("bmc info").split(b'\n')
                    if ('Device ID' not in device_id):
                         raise RuntimeError("Failed to discover a BMC Device ID in the BMC response")
                    device_id = device_id.split(b'\n')[0]
                    return device_id.split(b':')[1]
               except RuntimeError as e:
                    self._log.exception(e)

     def ipmi_cmd(self, cmd):
          """
          Execute any ipmi command
          """
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"ipmi")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
               # ipmi_cmd_data = sw.execute_ipmitool_command(cmd).split(b'\n')
               ipmi_cmd_data = sw.execute(cmd).split(b'\n')
               return ipmi_cmd_data
