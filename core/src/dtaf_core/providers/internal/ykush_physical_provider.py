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
from dtaf_core.providers.base_provider import BaseProvider
from dtaf_core.providers.physical_control import PhysicalControlProvider
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.drivers.internal.ykush_driver import YkushDriver

class KushPhysicalControlProvider(PhysicalControlProvider, YkushDriver):
    def __init__(self, log, cfg_opts):
        super(KushPhysicalControlProvider, self).__init__(cfg_opts, log)

    def __enter__(self):
        return super(KushPhysicalControlProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(KushPhysicalControlProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def connect_usb_to_sut(self, timeout=None):
        """
        Connect shared USB drive to the system under test.

        :exception Banino_Error: Banino Library Throws Error.
        """
        raise NotImplementedError

    def connect_usb_to_host(self, timeout=None):
        """
        Connect shared USB drive to the lab host.
        :exception Banino_Error: Banino Library Throws Error.
        """
        raise NotImplementedError

    def disconnect_usb(self, timeout=None):
        """
        Dis-Connect USB drive From Both Host and the system under test.
        :exception Banino_Error: Throws Error.
        """
        raise NotImplementedError

    def set_clear_cmos(self, timeout=None):
        """
        Clears the current configured data with factory setting
        :exception Banino_Error: Banino Gpio Library Throws Error.
        """
        raise NotImplementedError

    def read_postcode(self):
        # type: () -> hex
        """
        Get the current POST code from the SUT.
        :return: Current POST code of the platform
        """
        raise NotImplementedError

    def read_s3_pin(self):
        # type: () -> None
        """
        Read the state of the S3 pin
        :return: True if S3 pin is indicating SUT is in S3, False otherwise.
        """
        raise NotImplementedError

    def read_s4_pin(self):
        # type: () -> None
        """
        Read the state of the S4 pin
        :return: True if S4 pin is indicating SUT is in S4, False otherwise.
        """
        raise NotImplementedError

    def program_jumper(self, state, gpio_pin_number, timeout=None):
        """
        program_jumper controls the gpio pins of raspberry pi
        :param state=set or unset this makes the gpio pin high or low to cmmunicate with the relay
        gpio_pin_number which pins that needs to be programmed
        :return: True
        :exception Banino_Error: Library Throws Error.
        """
        raise NotImplementedError

    def get_power_state(self):
        """
        :return Actuall state of the platform, combines function of get dc power and ac power
        :exception Banino_Error: Banino Library Throws Error.
        """
        raise NotImplementedError

    def get_platform_volt(self):
        # type: () -> bool
        """
        :return actual dc volt of the platform index[0] True index[1] dc_volt
        :exception redfish error: Redfish driver throws error
        """
        raise NotImplementedError

    def enable_usb_ports(self,*port):
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"ykushr")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                ret = sw.enable_usb_power()
                return ret
            except Exception:
                self._log.error("Couldn't Enable USB Ports To Initialize Dediprog")
                raise

    def disable_usb_ports(self,*port):
        driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg, driver_name=r"ykushr")
        with DriverFactory.create(cfg_opts=driver_cfg, logger=self._log) as sw:
            try:
                ret = sw.disable_usb_power()
                return ret
            except Exception:
                self._log.error("Couldn't Disable USB Ports To Remove Dediprog")
                raise

    def get_system_id(self):
        # type: () -> bool
        """
        :return actual dc volt of the platform index[0] True index[1] dc_volt
        :exception redfish error: Redfish driver throws error
        """
        raise NotImplementedError

    def platform_health_status(self):
        """
        :return actual dc volt of the platform index[0] True index[1] dc_volt
        :exception redfish error: Redfish driver throws error
        """
        raise NotImplementedError

    def get_bmc_mac(self):
        """
        :return BMC Mac address of the platform index[0] True index[1] mac id
        :exception redfish error: Redfish driver throws error
        """
        raise NotImplementedError