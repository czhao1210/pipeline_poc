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
from datetime import datetime
from time import sleep

from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.drivers.internal.soundwave2k_driver import Soundwave2kDriver
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.dtaf_constants import PowerState
from dtaf_core.lib.exceptions import DriverIOError, SoundWaveError
from dtaf_core.providers.ac_power import AcPowerControlProvider
from xml.etree.ElementTree import Element, tostring
import xmltodict


class Soundwave2kAcProvider(AcPowerControlProvider):
    """
    This class is used to provide interfaces for the dc power controlling on SoundWave Control box.
    """

    def __enter__(self):
        return super(Soundwave2kAcProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(Soundwave2kAcProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def __init__(self, cfg_opts, log):
        self.__main_port = None
        super(Soundwave2kAcProvider, self).__init__(cfg_opts, log)

    def ac_power_on(self, timeout=None):
        # type: (int) -> bool
        """
        AC Power On

        :param timeout: timeout in second. ac power is expected to be on within timeout.
        :return:    True / False
        :raise SoundWaveError:  Hardware Error from soundwave driver
        :raise TypeError: incorrect type of timeout is input
        """
        if timeout is None:
            timeout = self._config_model.poweron_timeout
        driver_cfg = None
        if isinstance(self._cfg, Element):
            driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                               driver_name=r"soundwave2k")
        elif isinstance(self._cfg, dict):
            driver_cfg = self._cfg["driver"]
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                if not sw.ac_power_on() or not sw.ac2_power_on():
                    self._log.error("ac power on fail")
                    return False
                now = datetime.now()

                while sw.get_power_state() != PowerState.S0 and (datetime.now() - now).seconds < timeout:
                    sleep(0.5)
                ac_power_result = PowerState.S0 == sw.get_power_state()
                self._log.debug(r"ac power on: {}".format(sw.get_power_state()))
                return ac_power_result
            except Exception as ex:
                self._log.error("ac power on error:{}".format(ex))
                raise SoundWaveError(ex)
            finally:
                sw.close()

    def ac_power_off(self, timeout=None):
        # type: (int) -> bool
        """
        Turn off AC Power

        :param timeout: specify timeout for AC Power controlling.
        :return: True / False
        :raise SoundWaveError:  Hardware Error from soundwave driver
        :raise TypeError: incorrect type of timeout is input
        """
        if timeout is None:
            timeout = self._config_model.poweroff_timeout

        driver_cfg = None
        if isinstance(self._cfg, Element):
            driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                               driver_name=r"soundwave2k")
        elif isinstance(self._cfg, dict):
            driver_cfg = self._cfg["driver"]
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                if not sw.ac_power_off() or not sw.ac2_power_off():
                    self._log.error(r"ac_power_off fail")
                    return False
                now = datetime.now()
                while sw.get_power_state() != PowerState.G3 and (datetime.now() - now).seconds < timeout:
                    sleep(5)
                ac_power_result = PowerState.G3 == sw.get_power_state()
                self._log.debug(r"ac power off: {}".format(ac_power_result))
                return ac_power_result
            except Exception as ex:
                self._log.error("ac_power_off error:{}".format(ex))
                raise SoundWaveError(ex)
            finally:
                sw.close()

    def get_ac_power_state(self):
        # type: () -> str
        """
        get power state by reading SLPS3#, SLPS4#, SLPS5#, SLPDSW signal's voltage on SUT by control box.
        This API shields platform and control box difference.
        according to the platform setting in Config module,
        which signals' voltage need to be got are different support.
        Power states dependent on platform power schematic.

        :return:
        On      -   AC On
        Off     -   AC Off
        Unknown -   Unknown State
        :raise SoundWaveError:  Hardware Error from soundwave driver
        """

        driver_cfg = None
        if isinstance(self._cfg, Element):
            driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                               driver_name=r"soundwave2k")
        elif isinstance(self._cfg, dict):
            driver_cfg = self._cfg["driver"]
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw_driver: #type: Soundwave2kDriver
            try:
                state = sw_driver.get_power_state()
                if state == PowerState.Unknown:
                    raise SoundWaveError("Unknown State")
                elif state == PowerState.G3:
                    return False
                else:
                    return True
            except Exception as ex:
                raise SoundWaveError(ex)

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

        :param channel which power socket on the PDU needs to be controlled
               masterkey which has super user access to override the existing username and password
        :return:
            True     -   if the reset of Username and Password was reset
            None     -   Unable to Do the restting of the username and password
        :raise PDUPIError:  Hardware Error from pi driver
        """
        raise NotImplementedError
