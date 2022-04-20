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
from dtaf_core.drivers.internal.simics_driver import SimicsDriver
from dtaf_core.drivers.internal.console.console import Channel
from dtaf_core.providers.dc_power import DcPowerControlProvider
from dtaf_core.lib.configuration import ConfigurationHelper
import re

class SimicsDcProvider(DcPowerControlProvider):
    def __init__(self, cfg_opts, log):
        super(SimicsDcProvider, self).__init__(cfg_opts, log)
        self._driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"simics")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(SimicsDcProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def dc_power_on(self, timeout=None):
        """
        Simics DC Power On
        dependencies:
            self._config_model.poweron_timeout
            ConfigurationHelper.get_driver_config
            DriverFactory.create
            SimicDriver.is_simics_running
            SimicsDriver.SimicsChannel.execute_until
            SimicsDriver.register
            SimicsDriver.unregister
        equivalent classes:
            Valid:
                timeout:    (None, float)
                self._config_model.poweron_timeout: (float)
                ConfigurationHelper.get_driver_config:
                DriverFactory.create: (SimicsDriver)
                SimicDriver.is_simics_running: (True, False)
                SimicsDriver.SimicsChannel.execute_until: (string, None)
                SimicsDriver.register: None
                SimicsDriver.unregister: None
            Invalid:
                timeout:    (negative value, string)
                self._config_model.poweron_timeout: (string, negative value)
                ConfigurationHelper.get_driver_config:
                DriverFactory.create: (None, exception)
                SimicDriver.is_simics_running: (Non-boolean, Exception)
                SimicsDriver.SimicsChannel.execute_until: (Non-string, Exception)
                SimicsDriver.register: Exception
                SimicsDriver.unregister: Exception
        """
        if timeout is None:
            timeout = self._config_model.poweron_timeout
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"simics")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:  # type: SimicsDriver
            sw.register("dc_power")
            if sw.is_simics_running():
                simics = sw.SimicsChannel #type: Channel
                ret = simics.execute_until(cmd="power-button-press\r\n",
                                           until_pat="PWRBTNB\W+state\W+:\W+(\d+)",
                                           timeout=timeout)
            sw.unregister("dc_power")
        return ret is not None

    def dc_power_off(self, timeout=None):
        """
        Simics DC Power Off
        """
        if timeout is None:
            timeout = self._config_model.poweron_timeout
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"simics")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:  # type: SimicsDriver
            sw.register("dc_power")
            if sw.is_simics_running():
                simics = sw.SimicsChannel #type: Channel
                ret = simics.execute_until(cmd="power-button-press time = {}\r\n".format(timeout),
                                           until_pat="PWRBTNB\W+state\W+:\W+(\d+)",
                                           timeout=timeout)
            sw.unregister("dc_power")
        return True

    def get_dc_power_state(self):
        """
        Simics DC Power state
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"simics")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:  # type: SimicsDriver
            sw.register("dc_power")
            if sw.is_simics_running():
                simics = sw.SimicsChannel #type: Channel
                pat = re.compile("PWRBTNB\W+state\W+:\W+(\d+)")
                for r in range(0, 3):
                    ret = simics.execute_until(cmd="$system.mb.power_supply.status\r\n",
                                               until_pat="PWRBTNB\W+state\W+:\W+(\d+)",
                                               timeout=5)
                    if ret:
                        m = pat.search(ret)
                        if m:
                            sw.unregister("dc_power")
                            return m.groups()[0] == "1"
            sw.unregister("dc_power")
        return False

    def dc_power_reset(self):
        """
        Simics DC Power Reset
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"simics")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:  # type: SimicsDriver
            sw.register("dc_power")
            if sw.is_simics_running():
                simics = sw.SimicsChannel #type: Channel
                ret = simics.execute_until(cmd="reset-button-press\r\n",
                                           until_pat="running>",
                                           timeout=5)
            sw.unregister("dc_power")
        return True

    def close(self):
        pass
