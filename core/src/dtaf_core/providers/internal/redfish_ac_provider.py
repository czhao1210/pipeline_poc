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
from dtaf_core.providers.ac_power import AcPowerControlProvider
from dtaf_core.lib.configuration import ConfigurationHelper

class RedfishAcProvider(AcPowerControlProvider,RedfishDriver):
     def __init__(self,cfg_opts,log):
          super(RedfishAcProvider, self).__init__(cfg_opts, log)

     def __enter__(self):
          return super(RedfishAcProvider, self).__enter__()

     def __exit__(self, exc_type, exc_val, exc_tb):
          super(RedfishAcProvider, self).__exit__(exc_type, exc_val, exc_tb)

     def ac_power_on(self,timeout=None):
          """
          :send DC_POWER_ON command To Turn The Platform dc power to ON/S0 State.
          :return: True or None
          :exception
            Bmc Redfish_Error: Bmc Redfish Library Throws Error.
          """
          if timeout is None:
             timeout = self._config_model.poweron_timeout
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,driver_name=r"redfish")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
               try:
                    if sw.ac_power_on(timeout):
                        return True
               except Exception as ex:
                    self._log.error("BMC Redfish AC power On error:{}".format(ex))
                    raise

     def ac_power_off(self,timeout=None):
          """
          :send DC_POWER_OFF command To Turn The Platform dc power to OFF/S5 State.
          :return: True or None
          :exception
            Bmc Redfish_Error: Bmc Redfish Library Throws Error.
          """
          if timeout is None:
             timeout = self._config_model.poweroff_timeout
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,driver_name=r"redfish")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
               try:
                    if sw.ac_power_off(timeout):
                         return True
               except Exception as ex:
                    self._log.error("BMC Redfish AC power Off error:{}".format(ex))
                    raise
     
     def get_ac_power_state(self):
          """
          Detect The Current State and return.
          :exception Bmc Redfish_Error: Bmc Redfish Library Throws Error.
          """
          driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,driver_name=r"redfish")
          with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
               try:
                    if(sw.get_ac_power_state() == True):
                         return True
                    else:
                         return False
               except Exception as ex:
                    self._log.error("BMC Redfish AC power Off error:{}".format(ex))
                    return False

     def set_username_password(self):
          # type: (None) -> None
          """
          For Security Reason socket are controlled with username and Password
          :param: username needs to be given for the pdu secure login identification purpose
                  password for verfication of the username exists
                  channel which power socket on the PDU needs to be controlled
          :return:
              True    -   Password was set successfully.
              None    -   password failed to get set
          :raise DriverIOError: if command execution failed in driver
          :raise TimeoutException: fail to respond before timeout
          """
          raise NotImplementedError

     def reset_username_password(self):
          # type: (None) -> None
          """
          Reset Forgotten UserName and Password for PDU sockets

          Incase the user forgets username and password to override it from the API level

          :param channel which power socket on the PDU needs to be controlled
                 masterkey which has super user access to override the existing username and password
          :return:
              True     -   if the reset of Username and Password was reset
              None     -   Unable to Do the restting of the username and password
          :raise PDUPIError:  Hardware Error from pi driver
          """
          raise NotImplementedError