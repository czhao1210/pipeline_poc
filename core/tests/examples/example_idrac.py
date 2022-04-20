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
import pytest
from time import sleep
from dtaf_core.lib.os_lib import OsCommandResult
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.provider_factory import ProviderFactory
from xml.etree import ElementTree as ET
import time
from dtaf_core.providers.bios_provider import BiosProvider
from dtaf_core.providers.ac_power import AcPowerControlProvider
from dtaf_core.providers.dc_power import DcPowerControlProvider
from dtaf_core.providers.physical_control import PhysicalControlProvider
from dtaf_core.providers.uefi_shell import UefiShellProvider
from dtaf_core.providers.bios_menu import BiosBootMenuProvider
from dtaf_core.providers.internal.base_bios_bootmenu_provider import BaseBiosBootmenuProvider


class _Log(object):
    @classmethod
    def debug(cls, msg):
        print(msg)

    @classmethod
    def info(cls, msg):
        print(msg)

    @classmethod
    def warning(cls, msg):
        print(msg)

    @classmethod
    def error(cls, msg):
        print(msg)

    @classmethod
    def critical(cls, msg):
        print(msg)

    warn = warning
    fatal = critical


log = _Log()



class Debugging(object):
    def __init__(self):
        self._dccfg = ET.fromstring(
            """
            <dc>
					   <driver>
						    <redfish>
                                <bmc_type>idrac</bmc_type>
                                <ip>192.168.1.113</ip>
                                <username>root</username>
                                <password>calvin</password>
                            </redfish>
						</driver>
                <timeout>
                    <power_on>5</power_on>
                    <power_off>20</power_off>
                </timeout>
            </dc>
            """
        )
        self._phycfg = ET.fromstring(
            """
            <physical_control>
					   <driver>
						    <redfish>
                                <bmc_type>idrac</bmc_type>
                                <ip>192.168.1.113</ip>
                                <username>root</username>
                                <password>calvin</password>
                            </redfish>
						</driver>
                   <timeout>
                        <usbswitch>4</usbswitch>
                        <clearcmos>3</clearcmos>
                   </timeout>
            </physical_control>
            """
        )
        self._bioscfg = ET.fromstring(
            """
            <bios>
					   <driver>
						    <redfish>
                                <bmc_type>idrac</bmc_type>
                                <ip>192.168.1.113</ip>
                                <username>root</username>
                                <password>calvin</password>
                            </redfish>
						</driver>
            </bios>
            """
        )

    def initiate_providers(self):
        # self._efi = ProviderFactory.create(self._eficfg, log)  # type:# UefiShellProvider
        self._dc = ProviderFactory.create(self._dccfg, log)  # type:DcPowerControlProvider
        self._phy = ProviderFactory.create(self._phycfg, log) # type: PhysicalControlProvider
        self._bios = ProviderFactory.create(self._bioscfg, log) # type: BiosProvider
        # self._ac = ProviderFactory.create(self._accfg, log)  # type:AcPowerControlProvider
        # self._boot = ProviderFactory.create(self._bootcfg, log)  # type:BaseBiosBootmenuProvider

    def deinitiate_providers(self):
        pass
        # self._efi.close()
        # self._ac.close()
        # self._boot.close()

    def debug_idrac(self):

        self.initiate_providers()
        print(self._dc.get_dc_power_state())
        print(self._phy.read_postcode())
        print(self._bios.get_boot_device())
        # assert self._dc.dc_power_off()
        # assert not self._dc.get_dc_power_state()
        # assert self._dc.dc_power_on()
        # assert self._dc.get_dc_power_state()
        self.deinitiate_providers()

d = Debugging()
for i in range(0, 1):
    d.debug_idrac()
