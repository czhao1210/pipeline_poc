"""
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
"""

from dtaf_core.providers.ac_power import AcPowerControlProvider
from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.drivers.internal.rasp_driver import RaspDriver
from dtaf_core.lib.exceptions import DriverIOError
from dtaf_core.lib.configuration import ConfigurationHelper
class RaspAcProvider(AcPowerControlProvider):
    def __init__(self, cfg_opts, log):
        super().__init__(cfg_opts, log)

    def ac_power_on(self, timeout=None):
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"rasp")
        try:
            with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as drv:    #type: RaspDriver
                return drv.ac_power_on()
        except Exception as ex:
            self._log.error(ex)
            raise DriverIOError(ex)

    def ac_power_off(self, timeout=None):
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"rasp")
        try:
            with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as drv:    #type: RaspDriver
                return drv.ac_power_off()
        except Exception as ex:
            raise DriverIOError(ex)

    def get_ac_power_state(self):
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"rasp")
        try:
            with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as drv:    #type: RaspDriver
                return drv.get_ac_power()
        except Exception as ex:
            raise DriverIOError(ex)

    def set_username_password(self, channel=None, username=None, password=None):
        raise NotImplementedError

    def reset_username_password(self, channel=None, master_passkey=None):
        raise NotImplementedError