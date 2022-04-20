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
import time

from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.drivers.internal.simics_driver import SimicsDriver
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.ac_power import AcPowerControlProvider


class SimicsAcProvider(AcPowerControlProvider):
    def __init__(self, cfg_opts, log):
        super(SimicsAcProvider, self).__init__(cfg_opts, log)
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"simics")
        self.__driver = DriverFactory.create(cfg_opts=driver_cfg, logger=self._log)  # type: SimicsDriver
        self.__driver.register(r"ac_power")

    def __enter__(self):
        return super(SimicsAcProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(SimicsAcProvider, self).__exit__(exc_type, exc_val, exc_tb)
        self.__driver.shutdown_simics()

    def ac_power_on(self, timeout=0):
        """
        Simics AC Power On
        """
        self.__driver.register(r"ac_power")
        if not self.__driver.is_simics_running():
            self.__driver.start()
            self.__driver.launch_simics(time_out=timeout * 0.8)
            import re
            until_pat = r"AC_PRESENT\W+state\W+:\W+(\d+)"
            pat = re.compile(until_pat)
            for r in range(0, 2):
                ret = self.__driver.SimicsChannel.execute_until(cmd="$system.mb.power_supply.status\r\n",
                                                                until_pat=until_pat,
                                                                timeout=max(5, timeout * 0.1))
                if ret:
                    m = pat.search(str(ret))
                    if m:
                        return m.groups()[0] == "1"
        else:
            return True

    def ac_power_off(self, timeout=None):
        """
        Simics AC Power Off
        """
        if self.__driver.is_simics_running():
            ret = self.__driver.shutdown_simics()
            self.__driver.stop()
            self.__driver.unregister(r"ac_power")
            return ret
        return True

    def get_ac_power_state(self):
        """
        Simics AC Power state
        """
        return self.__driver.is_simics_running()

    def reset_username_password(self):
        raise NotImplementedError

    def set_username_password(self):
        raise NotImplementedError

    def close(self):
        pass
