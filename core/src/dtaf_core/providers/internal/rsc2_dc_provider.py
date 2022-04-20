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
from dtaf_core.providers.dc_power import DcPowerControlProvider
from dtaf_core.drivers.internal.rsc2_driver import RscDriverException
from dtaf_core.drivers.internal.rsc2_driver import Rsc2Driver
from dtaf_core.lib.exceptions import RSC2Error


class Rsc2DcProvider(DcPowerControlProvider):

    def __init__(self, cfg_opts, log):
        super(Rsc2DcProvider, self).__init__(cfg_opts, log)
        self.__driver = DriverFactory.create(
            cfg_opts=ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"rsc2"),
            logger=self._log) # type: Rsc2Driver

    def __enter__(self):
        return super(Rsc2DcProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(Rsc2DcProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def dc_power_on(self, timeout=None):
        try:
            if timeout is None:
                timeout = int(self._config_model.poweron_timeout)
            if not isinstance(timeout, int):
                raise TypeError('Timeout is not an integer !')
            # if not self.__driver.read_power_led():
            if self.__driver.read_amber_status_led():
                self.__driver.press_power_button(power_button_down=0)
            now = datetime.now()
            while not self.__driver.read_power_led() and (datetime.now() - now).seconds < timeout:
                sleep(0.5)
            return self.__driver.read_power_led()
        except RscDriverException as ex:
            raise RSC2Error(ex)

    def dc_power_off(self, timeout=None):
        try:
            if timeout is None:
                timeout = int(self._config_model.poweroff_timeout)
            if not isinstance(timeout, int):
                raise TypeError('Timeout is not an integer !')
            if self.__driver.read_power_led():
                print(f"Pressing and holding power button for -->{self._config_model.power_off_button_down}")
                self.__driver.press_power_button(power_button_down=self._config_model.power_off_button_down)
            now = datetime.now()
            while not self.__driver.read_power_led() and (datetime.now() - now).seconds < timeout:
                sleep(0.5)
            return not self.__driver.read_power_led()
        except RscDriverException as ex:
            raise RSC2Error(ex)

    def dc_power_reset(self):
        return self.__driver.press_reset_button()

    def get_dc_power_state(self):
        return self.__driver.read_power_led()
