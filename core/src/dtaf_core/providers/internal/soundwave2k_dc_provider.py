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
from dtaf_core.lib.exceptions import DriverIOError
from dtaf_core.providers import dc_power
from xml.etree.ElementTree import Element

class Soundwave2kDcProvider(dc_power.DcPowerControlProvider):
    def __enter__(self):
        return super(Soundwave2kDcProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(Soundwave2kDcProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def __init__(self, cfg_opts, log):
        self.__main_port = None
        super(Soundwave2kDcProvider, self).__init__(cfg_opts, log)

    def dc_power_on(self, timeout=None):
        # type: (float) -> bool
        """
        API to turn On Cold Power

        :param timeout: wait dc power state change until timeout
        :return: True / False
        :raise SoundWaveError:  Hardware Error from soundwave driver
        :raise TypeError: incorrect type of timeout
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
                if not sw.press_power_button():
                    self._log.error(r"press power button fail")
                    raise DriverIOError(r"press power button fail")
                if not sw.release_power_button():
                    self._log.error(r"release power button fail")
                    raise DriverIOError(r"release power button fail")
                self._log.debug(r"hard power on success")
            except Exception as ex:
                raise DriverIOError(ex)
            finally:
                sw.close()
            # wait for power state changed
            prev_time = datetime.now()
            target_power_state = PowerState.S0
            while (datetime.now() - prev_time).seconds < timeout:
                cur_power_state = sw.get_power_state()
                if cur_power_state == target_power_state:
                    self._log.debug("wait for power state {0} successfully...".format(target_power_state))
                    return True
                sleep(0.1)
        return False

    def dc_power_off(self, timeout=None):
        # type: (int) -> bool
        """
        API to turn off Cold Power

        :param timeout: wait for power state change until timeout
        :return: True / False
        :raise SoundWaveError:  any hardware internal Issue in SoundWave
        :raise TypeError: incorrect type of timeout
        """
        if timeout is None:
            timeout = self._config_model.poweroff_timeout
        driver_cfg = None
        if isinstance(self._cfg, Element):
            driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                               driver_name=r"soundwave2k")
        elif isinstance(self._cfg, dict):
            driver_cfg = self._cfg["driver"]["soundwave2k"]
        try:
            with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
                try:
                    if not sw.press_power_button():
                        self._log.error(r"press power button fail")
                        raise DriverIOError(r"press power button fail")
                    if not sw.release_power_button():
                        self._log.error(r"release power button fail")
                        raise DriverIOError(r"release power button fail")
                    self._log.debug(r"hard power off success")
                finally:
                    sw.close()
                # wait for power state changed
                prev_time = datetime.now()
                target_power_state = r"S5"
                while (datetime.now() - prev_time).seconds < timeout:
                    cur_power_state = sw.get_power_state()
                    if cur_power_state == target_power_state:
                        self._log.debug("wait for power state {0} successfully...".format(target_power_state))
                        return True
                    sleep(0.1)
        except Exception as ex:
            raise DriverIOError(ex)
        return False

    def dc_power_reset(self):
        """
        API to reset DC Power

        :return:
        :raise SoundWaveError:  any hardware internal Issue in SoundWave
        """
        driver_cfg = None
        if isinstance(self._cfg, Element):
            driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                               driver_name=r"soundwave2k")
        elif isinstance(self._cfg, dict):
            driver_cfg = self._cfg["driver"]["soundwave2k"]
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                if not sw.press_reset_button():
                    self._log.error(r"press reset button fail")
                    raise DriverIOError(r"press reset button fail")
                sleep(1)
                if not sw.release_reset_button():
                    self._log.error(r"release reset button fail")
                    raise DriverIOError(r"release reset button fail")
                self._log.debug(r"reset sut success")
                return True
            finally:
                sw.close()

    def get_dc_power_state(self):
        # type: () -> str
        """
        get power state by reading PIN's voltage on SUT by control box.
        This API shields platform and control box difference.
        according to the platform setting in Config module,
        which signals' voltage need to be got are different support.
        Power states dependent on platform power schematic.

        :return:
        S0/S3/S4/S5/Unknown
        :raise SoundWaveError:  Hardware Error from soundwave driver
        """
        driver_cfg = None
        if isinstance(self._cfg, Element):
            driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                               driver_name=r"soundwave2k")
        elif isinstance(self._cfg, dict):
            driver_cfg = self._cfg["driver"]["soundwave2k"]
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw_driver:
            try:
                low_voltage = self._config_model.driver_cfg.low_main_power_voltage
            except Exception as ex:
                self._log.debug(ex)
                low_voltage = 0.45

            try:
                high_voltage = self._config_model.driver_cfg.high_main_power_voltage
            except Exception as ex:
                self._log.debug(ex)
                high_voltage = 2.85

            try:
                high_memory_voltage = self._config_model.driver_cfg.high_memory_voltage
            except Exception as ex:
                self._log.debug(ex)
                high_memory_voltage = 2.2

            try:
                low_memory_voltage = self._config_model.driver_cfg.low_memory_voltage
            except Exception as ex:
                self._log.debug(ex)
                low_memory_voltage = 0.3

            signal_list = Soundwave2kDriver.S3_ENABLED_SIGNAL_LIST if self._config_model.driver_cfg.enable_s3_detect else Soundwave2kDriver.S3_DISABLED_SIGNAL_LIST

            result_list = sw_driver.get_voltages(signal_list)
            if not result_list or len(result_list) != len(signal_list):
                self._log.error(r"result_list is null or have error length {0}".format(result_list))
                self._log.debug(r"get_power_state return STATE_Unknown")
                raise DriverIOError(r"result_list is null or have error length {0}".format(result_list))

            if self._config_model.driver_cfg.enable_s3_detect:
                if result_list[0] >= high_voltage \
                        and result_list[2] >= high_memory_voltage \
                        and result_list[1] >= high_voltage:
                    self._log.debug(r"get_power_state return POWER_STATE_S0")
                    return PowerState.S0
                elif result_list[0] < low_voltage and result_list[2] >= high_memory_voltage \
                        and result_list[1] >= high_voltage:
                    self._log.debug(r"get_power_state return POWER_STATE_S3")
                    return PowerState.S3
                elif result_list[0] < low_voltage and result_list[2] < low_memory_voltage \
                        and result_list[1] >= high_voltage:
                    self._log.debug(r"get_power_state return POWER_STATE_S5")
                    return PowerState.S5
                elif result_list[0] < low_voltage and result_list[2] < low_memory_voltage \
                        and result_list[1] < low_voltage:
                    self._log.debug(r"get_power_state return POWER_STATE_G3")
                    return PowerState.G3
                else:
                    self._log.debug(r"get_power_state return STATE_Unknown")
                    return PowerState.Unknown
            else:
                if result_list[0] >= high_voltage and result_list[1] >= high_voltage:
                    self._log.debug(r"get_power_state return POWER_STATE_S0")
                    return PowerState.S0
                elif result_list[0] < low_voltage and result_list[1] >= high_voltage:
                    self._log.debug(r"get_power_state return POWER_STATE_S5")
                    return PowerState.S5
                elif result_list[0] < low_voltage and result_list[1] < low_voltage:
                    self._log.debug(r"get_power_state return POWER_STATE_G3")
                    return PowerState.G3
                else:
                    self._log.debug(r"get_power_state return STATE_Unknown")
                    return PowerState.Unknown
