#!/usr/bin/env python
"""
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
"""
import datetime
import re
import time
from typing import Optional, Callable, Any, Iterable, Mapping

from dtaf_core.drivers.internal.pdu.raritan import RaritanPowerstate, RaritanPoweroff, RaritanPoweron
from dtaf_core.drivers.base_driver import BaseDriver
from dtaf_core.lib.exceptions import DriverIOError

class PduDriver(BaseDriver):
    """
    pdu driver
    """

    def __init__(self, cfg_opts, log):
        super(PduDriver, self).__init__(cfg_opts, log)
        self._log = log
        self.__groups = self._driver_cfg_model.groups

    def __enter__(self):
        return super(PduDriver, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(PduDriver, self).__exit__(exc_type, exc_val, exc_tb)


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
                None        : Fail to send power off command
        :raise DriverIOError: if command execution failed in driver
        :raise TimeoutException: fail to respond before timeout
        """
        if "raritan" == self._driver_cfg_model.brand or not self._driver_cfg_model.brand:
            tasks = list()
            for g in self.__groups:
                tasks.append(RaritanPoweroff(g, timeout))
            for t in tasks:
                t.wait_result()
            return not self.get_ac_power_state(timeout)
        else:
            raise NotImplementedError

    def ac_power_on(self, timeout=None):
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
                None        : Fail to send power off command
        :raise DriverIOError: if command execution failed in driver
        :raise TimeoutException: fail to respond before timeout
        """
        if "raritan" == self._driver_cfg_model.brand or not self._driver_cfg_model.brand:
            tasks = list()
            for g in self.__groups:
                tasks.append(RaritanPoweron(g, timeout))
            for t in tasks:
                t.wait_result()
            return self.get_ac_power_state(timeout)
        else:
            raise NotImplementedError

    def get_ac_power_state(self, timeout):
        # type: (None) -> bool
        """
        Get AC power Detection of SUT.
        :param: username needs to be given for the pdu secure login identification purpose
                password for verification of the username exists
                channel which power socket on the PDU needs to be controlled
        :return:
            True    -    AC POWER Detected
            NONE     -   AC POWER NOT Detected

        :raise DriverIOError: if command execution failed in driver
        """
        if "raritan" == self._driver_cfg_model.brand or not self._driver_cfg_model.brand:
            tasks = list()
            for g in self.__groups:
                t = 6
                if timeout is None and isinstance(g.powerstate_timeout,int) and g.powerstate_timeout > 0:
                    t = g.powerstate_timeout
                elif isinstance(timeout,int) and timeout > 0:
                    t = timeout
                tasks.append(RaritanPowerstate(g, t))
            on = 0
            off = 0
            for t in tasks:
                ret = t.wait_result()
                for o, s in ret:
                    if s == "On":
                        on += 1
                    elif s.lower() == "off":
                        off += 1
            if on > 0 and off == 0:
                return True
            elif on == 0 and off > 0:
                return False
            raise DriverIOError("failed to get power state from PDU")
        else:
            raise NotImplementedError
