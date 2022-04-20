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
from abc import ABCMeta, abstractmethod
from six import add_metaclass
from dtaf_core.providers.base_provider import BaseProvider


@add_metaclass(ABCMeta)
class PhysicalControlProvider(BaseProvider):  # TODO: Bring in BaseProvider class
    """
    An interface allowing for physical control of the platform and power (i.e RaspberryPi,RSC2 and Similar Hardware Tools).
    """
    DEFAULT_CONFIG_PATH = "suts/sut/providers/physical_control"

    def __init__(self, cfg_opts, log):
        super(PhysicalControlProvider, self).__init__(cfg_opts, log)

    @abstractmethod
    def set_clear_cmos(self, timeout=None):
        # type: (float) -> None
        """
        Set the CLEAR_CMOS jumper to the specified state.
        
        :param state: If True, will set CLEAR_CMOS jumper to On. If False, will set CLEAR_CMOS jumper to Off.
        :return: True
        """
        raise NotImplementedError

    @abstractmethod
    def connect_usb_to_sut(self, timeout=None,image=None, username=None, password=None):
        # type: () -> None
        """
        Connect shared USB drive to the system under test.

        :return: True
        """
        raise NotImplementedError

    @abstractmethod
    def connect_usb_to_host(self, timeout=None):
        # type: () -> bool
        """
        Connect shared USB drive to the lab host.

        :return: True
        """
        raise NotImplementedError

    @abstractmethod
    def read_s3_pin(self):
        # type: () -> None
        """
        Read the state of the S3 pin
        
        :return: True if S3 pin is indicating SUT is in S3,None otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def read_s4_pin(self):
        # type: () -> None
        """
        Read the state of the S4 pin
        
        :return: True if S4 pin is indicating SUT is in S4, None otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def disconnect_usb(self, timeout=None):
        # type: () -> bool
        """
        Disconnect shared USB drive from both the SUT and host.
        
        :return: True otherwise None
        """
        raise NotImplementedError

    @abstractmethod
    def read_postcode(self):
        # type: () -> None
        """
        Reads Platform Postcode via LPC bus interface via GPIO
        
        :return: postcode or None
        """
        raise NotImplementedError

    @abstractmethod
    def program_jumper(self, state=None, gpio_pin_number=None, timeout=None):
        # type: () -> bool
        """
        Programs ControlBox Jumper to perform actions on the Platform
        
        :return: True Or None
        """
        raise NotImplementedError

    @abstractmethod
    def get_power_state(self):
        # type: () -> None
        """
        :return Actuall state of the platform, combines function of get dc power and ac power
        :exception Banino_Error: Banino Library Throws Error.
        """
        raise NotImplementedError

    @abstractmethod
    def get_platform_volt(self):
        # type: () -> bool
        """
        :return actual dc volt of the platform index[0] True index[1] dc_volt
        :exception redfish error: Redfish driver throws error
        """
        raise NotImplementedError

    def get_voltages(self, namelist):
        # type: () -> bool
        """
        Below voltages of power rail will be read.
        'A P12V PSU SCALED', 'P105 PCH AUX', 'P12V AUX',
        'P1V8 PCH', 'P3V3', 'P3VBAT',
        'PSU1 Input Voltage', 'PVCCIN CPU1',
        'PVCCIN CPU2', 'PVCCIO CPU1', 'PVCCIO CPU2',
        'PVDQ ABC CPU1', 'PVDQ ABC CPU2', 'PVDQ DEF CPU1',
        'PVDQ DEF CPU2', 'PVNN PCH AUX'
        :param namelist: a list of the power name to query
        :return a list of power voltages in format of tuple (name, voltage value)
        :exception DriverIoError
        """
        raise NotImplementedError

    @abstractmethod
    def enable_usb_ports(self,*port):
        # type: () -> bool
        """
        :return actual dc volt of the platform index[0] True index[1] dc_volt
        :exception redfish error: Redfish driver throws error
        """
        raise NotImplementedError

    @abstractmethod
    def disable_usb_ports(self,*port):
        # type: () -> bool
        """
        :return actual dc volt of the platform index[0] True index[1] dc_volt
        :exception redfish error: Redfish driver throws error
        """
        raise NotImplementedError

    @abstractmethod
    def get_system_id(self):
        # type: () -> bool
        """
        :return actual dc volt of the platform index[0] True index[1] dc_volt
        :exception redfish error: Redfish driver throws error
        """
        raise NotImplementedError

    @abstractmethod
    def platform_health_status(self):
        """
        :return actual dc volt of the platform index[0] True index[1] dc_volt
        :exception redfish error: Redfish driver throws error
        """
        raise NotImplementedError

    @abstractmethod
    def get_bmc_mac(self):
        """
        :return BMC Mac address of the platform index[0] True index[1] mac id
        :exception redfish error: Redfish driver throws error
        """
        raise NotImplementedError