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
from dtaf_core.drivers.internal.pdupi_driver import PdupiDriver
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.exceptions import RPiError
from dtaf_core.providers.dc_power import DcPowerControlProvider
from dtaf_core.providers.provider_factory import ProviderFactory

class PdupiDcProvider(DcPowerControlProvider, PdupiDriver):
    """
    This class is used to provide interfaces for the ac power controlling on PI Control box.
    """

    def __init__(self, cfg_opts, log):
        super(PdupiDcProvider, self).__init__(cfg_opts, log)

    def __enter__(self):
        return super(PdupiDcProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(PdupiDcProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def dc_power_on(self,timeout=None,channel=None):
        # type: (int) -> bool
        """
        DC Power On

        :param timeout: timeout in second. dc power is expected to be on within timeout.
               channel: says which socket on the pdu to be performed the functionality of ac power on.
        :return:    True / None
        :raise pduPIError:  Hardware Error from pi driver
        :raise TypeError: incorrect type of timeout is input
        """
        if timeout is None:
            timeout = self._config_model.poweron_timeout
        timeout = int(timeout)

        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"pdupi")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                if sw.dc_power_on(channel,timeout):
                    return True
                else:
                    return False
            except Exception as ex:
                self._log.error("pudpi dc power on error:{}".format(ex))
                raise RPiError(ex)

    def dc_power_off(self,timeout=None,channel=None):
        # type: (int) -> bool
        """
        AC Power Off

        :param timeout: timeout in second. ac power is expected to be on within timeout.
               channel: says which socket on the pdu to be performed the functionality of ac power off
        :return:    True / None
        :raise PDUPIError:  Hardware Error from pi driver
        :raise TypeError: incorrect type of timeout is input
        """
        if timeout is None:
            timeout = self._config_model.poweroff_timeout
        timeout = int(timeout)
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"pdupi")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                if sw.dc_power_off(channel,timeout):
                    return True
                else:
                    return False
            except Exception as ex:
                self._log.error("pdu dc power off error:{}".format(ex))
                raise RPiError(ex)

    def get_dc_power_state(self, channel=None):
        """
        DC Power Detection

        :param channel: says which socket on the pdu to be performed the functionality of ac power Detection
        :return:    True / None
        :raise PDUPIError:  Hardware Error from pi driver
        """
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                           driver_name=r"pdupi")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                if sw.get_dc_power_state(channel):
                    return True
                else:
                    return False
            except Exception as ex:
                self._log.error("pdu dc power state detection error:{}".format(ex))
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
                if(sw.dc_power_reset()):
                    return True
                else:
                    return False
            except Exception as ex:
                self._log.error("pi dc power on error:{}".format(ex))
                raise RPiError(ex)
