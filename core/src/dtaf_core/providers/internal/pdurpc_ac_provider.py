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
from dtaf_core.lib.exceptions import DriverIOError
from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.ac_power import AcPowerControlProvider
from dtaf_core.drivers.internal.pdurpc_driver import PdurpcDriver

class PdurpcAcProvider(AcPowerControlProvider, PdurpcDriver):
    """
    This class is used to provide interfaces for the ac power controlling on PI Control box.
    """

    def __init__(self, cfg_opts, log):
        super(PdurpcAcProvider, self).__init__(cfg_opts, log)

    def __enter__(self):
        return super(PdurpcAcProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(PdurpcAcProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def ac_power_on(self, timeout=None):
        # type: (int) -> bool
        """
        AC Power On

        :param timeout: timeout in second. ac power is expected to be on within timeout.
               channel: says which socket on the pdu to be
               performed the functionality of ac power on.
        :return:    True / None
        :raise pduPIError:  Hardware Error from pi driver
        :raise TypeError: incorrect type of timeout is input
        """
        if timeout is None:
            timeout = self._config_model.poweron_timeout
        timeout = int(timeout)

        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"pdurpc")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as s_w:
            try:
                if(s_w.ac_power_on(timeout)== True):
                    return True
            except Exception as ex:
                self._log.error("PDU RPC ac power on error:{}".format(ex))
                raise DriverIOError(ex)

    def ac_power_off(self, timeout=None):
        # type: (int) -> bool
        """
        AC Power Off

        :param timeout: timeout in second. ac power is expected to be on within timeout.
               channel: says which socket on the pdu to be
                performed the functionality of ac power off
        :return:    True / None
        :raise PDUPIError:  Hardware Error from pi driver
        :raise TypeError: incorrect type of timeout is input
        """
        if timeout is None:
            timeout = self._config_model.poweroff_timeout
        timeout = int(timeout)
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"pdurpc")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as s_w:
            try:
                if(s_w.ac_power_off(timeout) == True):
                    return True
            except Exception as ex:
                self._log.error("PDU RPC ac power off error:{}".format(ex))
                raise DriverIOError(ex)

    def get_ac_power_state(self, timeout=None):
        """
        AC Power Detection
        :param channel: says which socket on the pdu to be performed
        the functionality of ac power Detection
        :return:    True / None
        :raise PDUPIError:  Hardware Error from pi driver
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"pdurpc")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as s_w:
            try:
                if(s_w.get_ac_power_state()== True):
                    return True
            except Exception as ex:
                self._log.error("PDU RPC ac power state error:{}".format(ex))
                raise DriverIOError(ex)

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