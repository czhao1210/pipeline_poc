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
import sys,os
import time
import raritan
from raritan import rpc
from raritan.rpc import pdumodel, firmware
from dtaf_core.drivers.base_driver import BaseDriver

class PdurpcDriver(BaseDriver):
    def __init__(self, cfg_opts, log):
        super(PdurpcDriver, self).__init__(cfg_opts, log)
        self._log = log
        self.username = self._driver_cfg_model.username
        self.password = self._driver_cfg_model.password
        self.outlet = self._driver_cfg_model.outlets
        self.ip = self._driver_cfg_model.ip

    def __enter__(self):
        return super(PdurpcDriver, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(PdurpcDriver, self).__exit__(exc_type, exc_val, exc_tb)

    def ac_power_on(self, timeout=None):
        # type: (int) -> bool
        """
        This API changes SUT from G3 to S0/S5. API will not check
        the initial state of SUT. It just sends signal.
        :param: username needs to be given for the pdu secure login identification purpose
                password for verfication of the username exists
                channel which power socket on the PDU needs to be controlled
                operation turn off or turn on universal standard 0 is off 1 is on.
                timeout  :second, the max time spend for executing AC_power_off to
                 SUT enter into G3, it should more than 0. If it is None,
                  API will refer to configuration for the default value.
        :return:
                True        : AC power supply has been connected.
                False        : Fail to send power on command
        :raise DriverIOError: if command execution failed in driver
        """
        #print(self.outlet)
        agent = rpc.Agent("https", self.ip, self.username, self.password)
        pdu = pdumodel.Pdu("/model/pdu/0", agent)
        firmware_proxy = firmware.Firmware("/firmware", agent)
        outlets = pdu.getOutlets()
        settings = outlets[(self.outlet)].getSettings()
        for i in range(len(self.outlet)):
            ret = outlets[(self.outlet[i])].setPowerState(pdumodel.Outlet.PowerState.PS_ON)
            ret = (outlets[self.outlet].getState())
            ret = str(ret)
            if (ret.find(str("PS_OFF")) != -1):
                self._log.error("AC POWER On Didn't Happen")
                return False
            elif (ret.find(str("PS_ON")) != -1):
                self._log.info("AC POWER On Successful for this outlet {0}".format(self.outlet[i]))
            else:
                return False
        return True

    def ac_power_off(self, timeout=None):
        # type: (int) -> bool
        """
        This API will change SUT from S5/S0 to G3.
        It will check if the entrance state is S5 and if the final state is G3.
        :param: username needs to be given for the pdu secure login identification purpose
                password for verfication of the username exists
                channel which power socket on the PDU needs to be controlled
                operation turn off or turn on universal standard 0 is off 1 is on.
                timeout  :second, the max time spend for executing AC_power_off to
                 SUT enter into G3, it should more than 0. If it is None,
                 API will refer to configuration for the default value.
        :return:
                True        : AC power supply has been removed.
                False        : Fail to send power off command
        :raise DriverIOError: if command execution failed in driver
        :raise TimeoutException: fail to respond before timeout
        """
        agent = Agent("https", self.ip, self.username, self.password)
        pdu = pdumodel.Pdu("/model/pdu/0", agent)
        firmware_proxy = firmware.Firmware("/firmware", agent)
        outlets = pdu.getOutlets()
        settings = outlets[(self.outlet)].getSettings()
        for i in range(len(self.outlet)):
            ret = outlets[(self.outlet[i])].setPowerState(pdumodel.Outlet.PowerState.PS_ON)
            ret = (outlets[self.outlet].getState())
            ret = str(ret)
            if (ret.find(str("PS_OFF")) != -1):
                self._log.info("AC POWER OFF Successful for this outlet {0}".format(self.outlet[i]))
            elif (ret.find(str("PS_ON")) != -1):
                self._log.error("AC POWER OFF Didn't Happen {0}".format(self.outlet[i]))
                return False
            else:
                return False
        return True

    def get_ac_power_state(self, timeout=None):
        # type: (None) -> bool
        """
        Get AC power Detection of SUT.
        :param: username needs to be given for the pdu secure login identification purpose
                password for verfication of the username exists
                channel which power socket on the PDU needs to be controlled
        :return:
            True    -    AC POWER Detected
            False     -   AC POWER NOT Detected

        :raise DriverIOError: if command execution failed in driver
        """
        agent = Agent("https", self.ip, self.username, self.password)
        pdu = pdumodel.Pdu("/model/pdu/0", agent)
        firmware_proxy = firmware.Firmware("/firmware", agent)
        outlets = pdu.getOutlets()
        settings = outlets[(self.outlet)].getSettings()
        for i in range(len(self.outlet)):
            ret = (outlets[self.outlet].getState())
            ret = str(ret)
            if (ret.find(str("PS_OFF")) != -1):
                self._log.error("AC POWER Not Detected for this outlet {0}".format(self.outlet[i]))
                if ((i+1) == len(self.outlet)):
                    return False
            elif (ret.find(str("PS_ON")) != -1):
                self._log.info("AC POWER Detectect for this outlet {0}".format(self.outlet[i]))
                if ((i+1) == len(self.outlet)):
                    return True
            else:
                return False