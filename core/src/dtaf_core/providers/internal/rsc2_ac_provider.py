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
from time import sleep
from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.exceptions import DriverIOError, RSC2Error
from dtaf_core.providers.ac_power import AcPowerControlProvider

class Rsc2AcProvider(AcPowerControlProvider):

    def __init__(self, cfg_opts, log):
        super(Rsc2AcProvider, self).__init__(cfg_opts, log)
        self.__driver = DriverFactory.create(
            cfg_opts=ConfigurationHelper.get_driver_config(provider=cfg_opts, driver_name=r"rsc2"),
            logger=log)
        pass

    def __enter__(self):
        return super(Rsc2AcProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(Rsc2AcProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def ac_power_off(self, timeout=None):
        try:
            self.__driver.remove_power()
            now = datetime.now()
            if timeout is None:
                timeout = int(self._config_model.poweroff_timeout)
            if not isinstance(timeout, int):
                raise TypeError('timeout is not an integer !')
            while self.__driver.ac_connected() and (datetime.now() - now).seconds < timeout:
                sleep(0.5)
            return not self.__driver.ac_connected()
        except Exception as ex:
            raise RSC2Error(ex)

    def get_ac_power_state(self):
        try:
            return self.__driver.ac_connected()
        except Exception as ex:
            raise RSC2Error(ex)

    def ac_power_on(self, timeout=None):
        try:
            if timeout is None:
                timeout = int(self._config_model.poweron_timeout)
            if not isinstance(timeout, int):
                raise TypeError('timeout is not an integer !')
            self.__driver.connect_power()
            now = datetime.now()
            while not self.__driver.ac_connected() and (datetime.now() - now).seconds < timeout:
                sleep(0.5)
            return self.__driver.ac_connected()
        except Exception as ex:
            raise RSC2Error(ex)

    def set_username_password(self,channel=None,username=None,password=None):
        """
        To set Platform socket username and password for security purpose
        :param: username needs to be given for the pdu secure login identification purpose
                password for verfication of the username exists
                channel which power socket on the PDU needs to be controlled
        :return:
            True    -   Password was set successfully.
            None    -   password failed to get set
        :raise PDUPIError: if command execution failed in driver
        """
        raise NotImplementedError
                 
    def reset_username_password(self,channel=None,masterkey=None):
        """
        Incase the user forgets username and password to override it from the API level

        :param channel: which power socket on the PDU needs to be controlled
               masterkey: which has super user access to override the existing username and password
        :return:
            True     -   if the reset of Username and Password was reset
            None     -   Unable to Do the restting of the username and password
        :raise PDUPIError:  Hardware Error from pi driver
        """
        raise NotImplementedError
