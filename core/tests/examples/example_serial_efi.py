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
from dtaf_core.providers.log import LogProvider


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
        self._accfg = ET.fromstring(
            """
                <ac>
                    <driver>
                        <soundwave2k enable_s3_detect="False">
                            <baudrate>115200</baudrate>
                            <serial type="1"></serial>
                            <port>COM101</port>
                            <voltagethreholds>
                                <main_power>
                                    <low>0.8</low>
                                    <high>2.85</high>
                                </main_power>
                                <dsw>
                                    <low>0.8</low>
                                    <high>2.85</high>
                                </dsw>
                                <memory>
                                    <low>0.3</low>
                                    <high>2.2</high>
                                </memory>

                            </voltagethreholds>
                        </soundwave2k>
                    </driver>
                    <timeout>
                        <power_on>5</power_on>
                        <power_off>20</power_off>
                    </timeout>
                </ac>
            """
        )
        self._dccfg = ET.fromstring(
            """
            <dc>
                <driver>
                    <soundwave2k enable_s3_detect="False">
                        <baudrate>115200</baudrate>
                        <serial type="1"></serial>
                        <port>COM101</port>
                        <voltagethreholds>

                            <main_power>
                                <low>0.8</low>
                                <high>2.85</high>
                            </main_power>
                            <dsw>
                                <low>0.8</low>
                                <high>2.85</high>
                            </dsw>
                            <memory>
                                <low>0.3</low>
                                <high>2.2</high>
                            </memory>

                        </voltagethreholds>
                    </soundwave2k>
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
                    <com>
                        <baudrate>115200</baudrate>
                        <port>COM100</port>
                        <timeout>5</timeout>
                    </com>
                </driver>
                <efishell_entry select_item="UEFI Internal Shell"/>
            </bios_bootmenu>
            """
        )
        self._eficfg = ET.fromstring(
            """
            <uefi_shell>
                <driver>
                    <com>
                        <port>COM100</port>
                        <baudrate>115200</baudrate>
                        <timeout>5</timeout>
                    </com>
                </driver>
            </uefi_shell>
            """
        )
        self._logcfg = ET.fromstring(""" 
                <log id="1">
                    <runwith/>
                    <logpath>logs</logpath>
                    <driver>
                        <com>
                            <baudrate>115200</baudrate>
                            <port>COM100</port>
                            <timeout>5</timeout>
                        </com>
                    </driver>
                </log>
        """)
        self.initiate_providers()

    def initiate_providers(self):
        self._ac = ProviderFactory.create(self._accfg, log)  # type:AcPowerControlProvider
        #self._dc = ProviderFactory.create(self._dccfg, log)  # type:DcPowerControlProvider
        #self._efi = ProviderFactory.create(self._eficfg, log)  # type:UefiShellProvider
        self._boot = ProviderFactory.create(self._bootcfg, log) # type:BaseBiosBootmenuProvider

    def debug_log(self):
        for i in range(0, 3):
            with ProviderFactory.create(self._logcfg, log) as l:  # type:LogProvider
                from datetime import datetime
                import os
                l.redirect(os.path.join("logs",datetime.now().strftime("%Y%m%d%H%M%S")))
                self.debug_efi()
                time.sleep(20*i+10)

    def debug_efi(self):
        self._ac.ac_power_off()
        time.sleep(30)
        self._ac.ac_power_on(30)
        time.sleep(30)
        b = self._boot
        if b.wait_for_entry_menu(timeout=600):
            for i in range(0,5):
                time.sleep(1)
                b.press(input_key="F7")
            b.wait_for_bios_boot_menu(timeout=120)
            b.select(item_name="UEFI Internal Shell", item_type="", timeout=3, use_regex=False)
            # self._boot.press(input_key="\r")
            # self._efi.wait_for_uefi(60)
            # if self._efi.in_uefi():
            #     self._efi.execute("fs1:", timeout=60)
        pass


Debugging().debug_log()
