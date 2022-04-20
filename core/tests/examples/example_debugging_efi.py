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
                    <simics>
                        <serial_port>2122</serial_port>
                        <service_port>2121</service_port>
                        <app>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww26.2/simics</app>
                        <project>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww26.2</project>
                        <script>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww26.2/targets/birchstream/birchstream-ap.simics</script>
                    </simics>
                </driver>
                <timeout>
                    <power_on>5</power_on>
                    <power_off>20</power_off>
                </timeout>
            </dc>
            """
        )
        self._bootcfg = ET.fromstring(
            """
            <bios_bootmenu>
                <driver>
                    <simics>
                        <serial_port>2122</serial_port>
                        <service_port>2121</service_port>
                        <host></host>
                        <app>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww26.2/simics</app>
                        <project>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww26.2</project>
                        <script>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww26.2/targets/birchstream/birchstream-ap.simics</script>
                    </simics>
                </driver>
                <efishell_entry select_item="UEFI Internal Shell"/>
            </bios_bootmenu>
            """
        )
        self._eficfg = ET.fromstring(
            """
            <uefi_shell>
                <driver>
                    <simics>
                        <serial_port>2122</serial_port>
                        <service_port>2121</service_port>
                        <app>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww26.2/simics</app>
                        <project>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww26.2</project>
                        <script>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww26.2/targets/birchstream/birchstream-ap.simics</script>
                    </simics>
                </driver>
            </uefi_shell>
            """
        )
        self.initiate_providers()

    def initiate_providers(self):
        self._dc = ProviderFactory.create(self._dccfg, log)  # type:DcPowerControlProvider
        self._boot = ProviderFactory.create(self._bootcfg, log)  # type:BaseBiosBootmenuProvider
        self._efi = ProviderFactory.create(self._eficfg, log)  # type:UefiShellProvider

    def debug_simics(self):
        self._dc.dc_power_reset()
        if self._boot.wait_for_entry_menu(timeout=600):
            for i in range(0,5):
                time.sleep(1)
                self._boot.press(input_key="F7")
            self._boot.wait_for_bios_boot_menu(timeout=120)
            self._boot.select(item_name="UEFI Internal Shell", item_type="", timeout=3, use_regex=False)
            self._boot.press(input_key="\r")
            self._efi.wait_for_uefi(60)
            if self._efi.in_uefi():
                self._efi.execute("fs1:", timeout=60)


    def debug_efi(self):
        self._ac.ac_power_off()
        time.sleep(30)
        self._ac.ac_power_on(30)
        time.sleep(30)
        if self._boot.wait_for_entry_menu(timeout=600):
            for i in range(0,5):
                time.sleep(1)
                self._boot.press(input_key="F7")
            self._boot.wait_for_bios_boot_menu(timeout=120)
            self._boot.select(item_name="UEFI Internal Shell", item_type="", timeout=3, use_regex=False)
            self._boot.press(input_key="\r")
            self._efi.wait_for_uefi(60)
            if self._efi.in_uefi():
                self._efi.execute("fs1:", timeout=60)
        pass


Debugging().debug_simics()
