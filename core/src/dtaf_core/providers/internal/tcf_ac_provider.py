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
from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.ac_power import AcPowerControlProvider


class TcfAcProvider(AcPowerControlProvider):

    def __init__(self, cfg_opts, log):
        super(TcfAcProvider, self).__init__(cfg_opts, log)
        self.__driver = DriverFactory.create(
            cfg_opts=ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name="tcf"),
            logger=self._log
        )
        # TODO: extract specific power rail for DC - not rolled out in Qpool yet
        #self.ac_power_rail = "main_power_bmc"
        self.ac_power_rail = "AC" 	# FIXME: hack for nuc-77t

    def __enter__(self):
        return super(TcfAcProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(TcfAcProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def ac_power_on(self, timeout=None):
        self.__driver.get_target().power.on(component=self.ac_power_rail)

    def ac_power_off(self, timeout=None):
        self.__driver.get_target().power.off(component=self.ac_power_rail)

    def ac_power_reset(self):
        self.__driver.get_target().power.cycle(component=self.ac_power_rail)

    def get_ac_power_state(self):
        # TCF reports power on if all rails are powered
        # This works for DC power, but may prove troublesome for AC power
        return self.__driver.get_target().power.get()

    def set_username_password(self,channel=None,username=None,password=None):
        # type: (None) -> str
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
        
    def reset_username_password(self,channel=None,master_passkey=None):
        # type: (None) -> str
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
