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

from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.drivers.internal.pi_driver import PiDriver
from dtaf_core.lib.exceptions import RPiError
from dtaf_core.providers.dc_power import DcPowerControlProvider
from dtaf_core.lib.configuration import ConfigurationHelper

class PiDcProvider(DcPowerControlProvider, PiDriver):
    """
    This class is used to provide interfaces for the dc power controlling on PI Control box.
    """
    def __init__(self, cfg_opts, log):
        self.__main_port = None
        super(PiDcProvider, self).__init__(cfg_opts, log)
        
    def __enter__(self):
        return super(PiDcProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(PiDcProvider, self).__exit__(exc_type, exc_val, exc_tb)

    
    def dc_power_on(self, timeout=None):
        # type: (int) -> bool
        """
        DC Power On

        :param timeout: timeout in second. ac power is expected to be on within timeout.
        :return:    True / None
        :raise SoundWaveError:  Hardware Error from soundwave driver
        :raise TypeError: incorrect type of timeout is input
        """
        if timeout is None:
            timeout = self._config_model.poweron_timeout
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                               driver_name=r"pi")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                if sw.dc_power_on(timeout):
                    return True
                else:
                    return False
            except Exception as ex:
                self._log.error("pi dc power on error:{}".format(ex))
                raise RPiError(ex)


    def dc_power_off(self, timeout=None):
        # type: (int) -> bool
        """
        DC Power On

        :param timeout: timeout in second. ac power is expected to be on within timeout.
        :return:    True / None
        :raise SoundWaveError:  Hardware Error from soundwave driver
        :raise TypeError: incorrect type of timeout is input
        """
        if timeout is None:
            timeout = self._config_model.poweroff_timeout
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                               driver_name=r"pi")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                if sw.dc_power_off(timeout):
                    return True
                else:
                    return False
            except Exception as ex:
                self._log.error("pi dc power off error:{}".format(ex))
                raise RPiError(ex)

    def get_dc_power_state(self):
        """
        DC Power On

        :param timeout: timeout in second. ac power is expected to be on within timeout.
        :return:    True / None
        :raise SoundWaveError:  Hardware Error from soundwave driver
        :raise TypeError: incorrect type of timeout is input
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"pi")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                if sw.get_dc_power_state():
                    return True
                else:
                    return False
            except Exception as ex:
                self._log.error("pi dc power on error:{}".format(ex))
                raise RPiError(ex)

    def dc_power_reset(self):
        """
        :send DC_Reset command to Gpio To Turn The Relay to go High which physcialy interact with Front Panel Gpio.
        :return: True or None
        :exception
        FlaskError: Raspberry Pi Flask Error.
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"pi")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                if sw.dc_power_reset():
                    return True
                else:
                    return False
            except Exception as ex:
                self._log.error("pi dc power on error:{}".format(ex))
                raise RPiError(ex)
