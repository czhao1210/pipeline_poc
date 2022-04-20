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
import os

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
from dtaf_core.providers.internal.simics_bios_bootmenu_provider import SimicsBiosBootmenuProvider
from dtaf_core.providers.internal.simics_bios_setupmenu_provider import SimicsBiosSetupmenuProvider
import mock


class Debugging(object):
    def __init__(self):
        self._accfg = ET.fromstring(
            """
            <ac>
                <driver>
                    <simics>
                        <mode>
                            <real-time>True</real-time>
                        </mode>
                        <serial_port>2122</serial_port>
                        <host>
                            <name>10.148.205.212</name>
                            <port>22</port>
                            <username>xxxxxx</username>
                            <password>xxxxxx</password>
                        </host>
                        <service_port>2123</service_port>
                        <app>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww35.3/simics</app>
                        <project>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww35.3</project>
                        <script>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww35.3/targets/birchstream/birchstream-ap.simics</script>
                    </simics>
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
                    <simics>
                        <mode>
                            <real-time>True</real-time>
                        </mode>
                        <serial_port>2122</serial_port>
                        <host>
                            <name>10.148.205.212</name>
                            <port>22</port>
                            <username>xxxxxx</username>
                            <password>xxxxxx</password>
                        </host>
                        <service_port>2123</service_port>
                        <app>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww35.3/simics</app>
                        <project>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww35.3</project>
                        <script>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww35.3/targets/birchstream/birchstream-ap.simics</script>
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
                        <mode>
                            <real-time>True</real-time>
                        </mode>
                        <serial_port>2122</serial_port>
                        <host>
                            <name>10.148.205.212</name>
                            <port>22</port>
                            <username>xxxxxx</username>
                            <password>xxxxxx</password>
                        </host>
                        <service_port>2123</service_port>
                        <app>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww35.3/simics</app>
                        <project>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww35.3</project>
                        <script>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww35.3/targets/birchstream/birchstream-ap.simics</script>
                    </simics>
                </driver>
                <efishell_entry select_item="UEFI Internal Shell"/>
            </bios_bootmenu>
            """
        )
        self._setupcfg = ET.fromstring(
            """
            <bios_setupmenu>
                <driver>
                    <simics>
                        <mode>
                            <real-time>True</real-time>
                        </mode>
                        <serial_port>2122</serial_port>
                        <host>
                            <name>10.148.205.212</name>
                            <port>22</port>

                            <username>xxxxxx</username>
                            <password>xxxxxx</password>
                        </host>
                        <service_port>2123</service_port>
                        <app>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww35.3/simics</app>
                        <project>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww35.3</project>
                        <script>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww35.3/targets/birchstream/birchstream-ap.simics</script>
                    </simics>
                </driver>
                <efishell_entry select_item="Launch EFI Shell">
                    <path>
                        <node>Setup Menu</node>
                        <node>Boot Manager</node>
                    </path>
                </efishell_entry>
                <continue select_item="Continue"/>
                <reset press_key="\\33R\\33r\\33R" parse="False"/>
            </bios_setupmenu>
            """
        )
        self._eficfg = ET.fromstring(
            """
            <uefi_shell>
                <some></some>
                <driver>
                    <simics>
                        <mode>
                            <real-time>True</real-time>
                        </mode>
                        <serial_port>2122</serial_port>
                        <host>
                            <name>10.148.205.212</name>
                            <port>22</port>
                            <username>xxxxxx</username>
                            <password>xxxxxx</password>
                        </host>
                        <service_port>2123</service_port>
                        <app>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww35.3/simics</app>
                        <project>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww35.3</project>
                        <script>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww35.3/targets/birchstream/birchstream-ap.simics</script>
                    </simics>
                </driver>
            </uefi_shell>
            """
        )

    def initiate_providers(self):
        self._efi = ProviderFactory.create(cfg_opts=self._eficfg, logger=mock.MagicMock())  # type:UefiShellProvider
        self._dc = ProviderFactory.create(cfg_opts=self._dccfg, logger=mock.MagicMock())  # type:DcPowerControlProvider
        self._ac = ProviderFactory.create(cfg_opts=self._accfg, logger=mock.MagicMock())  # type:AcPowerControlProvider
        self._boot = ProviderFactory.create(cfg_opts=self._bootcfg,
                                            logger=mock.MagicMock())  # type:SimicsBiosBootmenuProvider
        self._setup = ProviderFactory.create(cfg_opts=self._setupcfg,
                                             logger=mock.MagicMock())  # type:SimicsBiosSetupmenuProvider

    def deinitiate_providers(self):
        self._efi.close()
        self._dc.close()
        self._ac.close()
        self._boot.close()
        self._setup.close()

    def debug_simics(self):

        self.initiate_providers()
        assert self._ac.ac_power_off()
        assert not self._ac.get_ac_power_state()
        assert self._ac.ac_power_on(timeout=30)
        assert self._ac.get_ac_power_state()
        time.sleep(10)
        self._dc.dc_power_reset()
        # configure timeout
        for i in range(0, 60):
            self._boot.press(input_key="F2")
            time.sleep(0.3)
        self._setup.wait_for_bios_setup_menu(timeout=600)
        self._setup.select(item_name="Boot Maintenance Manager", item_type=None, use_regex=False, timeout=10)
        self._setup.enter_selected_item(ignore=False, timeout=5)
        self._setup.select(item_name="Set Time Out Value", item_type=None, use_regex=False, timeout=10)
        self._setup.enter_selected_item(ignore=False, timeout=5)
        self._setup.select(item_name="Auto Boot Time-out", item_type=None, use_regex=False, timeout=10)
        self._setup.enter_selected_item(ignore=False, timeout=5)
        self._setup.input_text("10")
        self._setup.enter_selected_item(ignore=False, timeout=5)
        self._setup.select(item_name="Commit Changes and Exit", item_type=None, use_regex=False, timeout=10)
        self._setup.enter_selected_item(ignore=False, timeout=5)
        # verify
        self._setup.enter_selected_item(ignore=False, timeout=5)
        self._setup.select(item_name="Set Time Out Value", item_type=None, use_regex=False, timeout=10)
        ret = self._setup.get_selected_item()
        print(ret)

        self._dc.dc_power_reset()
        if self._boot.wait_for_entry_menu(timeout=600):
            for i in range(0, 2):
                self._boot.press(input_key="F7")
                time.sleep(0.3)
        self._boot.wait_for_bios_boot_menu(timeout=120)
        self._boot.select(item_name="UEFI Internal Shell", item_type="", timeout=3, use_regex=False)
        self._boot.enter_selected_item(ignore_output=True, timeout=5)
        assert self._efi.wait_for_uefi(60)
        assert self._efi.in_uefi()
        assert self._efi.execute("fs1:", timeout=60)
        self._ac.ac_power_off()
        self.deinitiate_providers()

    def debug_provider_life_cycle_active(self):
        with ProviderFactory.create(self._accfg, mock.MagicMock()) as a:  # type: AcPowerControlProvider
            with ProviderFactory.create(self._dccfg, mock.MagicMock()) as d:  # type: DcPowerControlProvider
                with ProviderFactory.create(self._bootcfg, mock.MagicMock()) as b:  # type: BiosBootMenuProvider
                    with ProviderFactory.create(self._eficfg, mock.MagicMock()) as u:  # type: UefiShellProvider
                        assert a.ac_power_off()
                        assert not a.get_ac_power_state()
                        assert a.ac_power_on(timeout=30)
                        assert a.get_ac_power_state()
                        d.dc_power_reset()
                        for i in range(0, 60):
                            b.press(input_key="F7")
                            time.sleep(0.3)
                        # if b.wait_for_entry_menu(timeout=600):
                        b.wait_for_bios_boot_menu(timeout=120)
                        b.select(item_name="UEFI Internal Shell", item_type="", timeout=3, use_regex=False)
                        b.enter_selected_item(ignore_output=True, timeout=5)
                        assert u.wait_for_uefi(120)
                        ret = u.in_uefi()
                        smbiosview_ret = u.execute("smbiosview -t 17", timeout=60)
                        assert smbiosview_ret
                        print("*************************output of smbiosview***************************")
                        print("****************************************************")
                        pci_ret = u.execute("pci", timeout=60)
                        assert pci_ret
                        print("*************************output of pci***************************")
                        print("****************************************************")
                        drivers_ret = u.execute("drivers", timeout=60)
                        assert drivers_ret
                        print("*************************output of drivers***************************")
                        print("****************************************************")
                        a.ac_power_off()
                        strip_str = '[25;08H[25;08H'
                        with open(os.path.join(data_path, 'auto_output.txt'), 'w+') as file:
                            file.write(smbiosview_ret.rstrip(strip_str))
                            file.write(pci_ret.rstrip(strip_str))
                            file.write(drivers_ret.rstrip(strip_str))
                        is_same_output = compare(os.path.join(data_path, 'auto_output.txt'),
                                                 os.path.join(data_path, 'biosmenu_uefi_example.txt'))
                        assert is_same_output[0], is_same_output[1]
                        from dtaf_core.lib.private.cl_utils.adapter.private.pyte_interface.gernal_pyte_api import \
                            GernalPYTE
                        with open(os.path.join(data_path, 'auto_output.txt'), 'r') as file:
                            with open(os.path.join(data_path, 'auto_output_for_read.txt'), 'w') as file1:
                                while True:
                                    data = file.readline()
                                    if data:
                                        data = data.strip('\n')
                                        pyte = GernalPYTE(90, 1)
                                        pyte.feed(data)
                                        res = "".join(pyte.get_screen_display())
                                        file1.write(res + '\n')
                                    else:
                                        break
                                file1.write(time.strftime("%Y-%m-%d, %H:%M:%S"))

    def debug_provider_life_cycle_lazy(self):
        with ProviderFactory.create(self._accfg, mock.MagicMock()) as a:  # type: AcPowerControlProvider
            assert a.ac_power_off()
            assert not a.get_ac_power_state()
            assert a.ac_power_on(timeout=30)
            sleep(10)
            assert a.get_ac_power_state()
            with ProviderFactory.create(self._dccfg, mock.MagicMock()) as d:  # type: DcPowerControlProvider
                time.sleep(10)
                d.dc_power_reset()
                with ProviderFactory.create(self._bootcfg, mock.MagicMock()) as b:  # type: BiosBootMenuProvider
                    for i in range(0, 60):
                        b.press(input_key="F7")
                        time.sleep(0.3)
                    # if b.wait_for_entry_menu(timeout=600):
                    #     for i in range(0, 2):
                    #         b.press(input_key="F7")
                    #         time.sleep(0.3)
                    b.wait_for_bios_boot_menu(timeout=120)
                    b.select(item_name="UEFI Internal Shell", item_type="", timeout=3, use_regex=False)
                    b.enter_selected_item(ignore_output=True, timeout=5)
                    with ProviderFactory.create(self._eficfg, mock.MagicMock()) as u:  # type: UefiShellProvider
                        assert u.wait_for_uefi(60)
                        assert u.in_uefi()
                        assert u.execute("fs1:", timeout=60)
                    a.ac_power_off()

    def debug_efi(self):
        self._ac.ac_power_on(30)
        time.sleep(30)
        # if self._boot.wait_for_entry_menu(timeout=600):
        for i in range(0, 60):
            time.sleep(0.3)
            self._boot.press(input_key="F7")
        self._boot.wait_for_bios_boot_menu(timeout=120)
        self._boot.select(item_name="UEFI Internal Shell", item_type="", timeout=3, use_regex=False)
        self._boot.press_key(input_key="\r")
        self._efi.wait_for_uefi(60)
        if self._efi.in_uefi():
            self._efi.execute("fs1:", timeout=60)
        self._ac.ac_power_off()

    def debug_simics_setupmenu(self):
        with ProviderFactory.create(cfg_opts=self._dccfg,
                                    logger=mock.MagicMock()) as dc:  # type: DcPowerControlProvider
            with ProviderFactory.create(cfg_opts=self._bootcfg,
                                        logger=mock.MagicMock()) as boot:  # type: SimicsBiosBootmenuProvider
                with ProviderFactory.create(cfg_opts=self._setupcfg,
                                            logger=mock.MagicMock()) as setup:  # type: SimicsBiosSetupmenuProvider
                    time.sleep(10)
                    assert dc.dc_power_reset()
                    for i in range(0, 60):
                        setup.press(input_key="F2")
                        time.sleep(0.3)
                    setup.wait_for_bios_setup_menu(timeout=600)
                    setup.select(item_name="Boot Maintenance Manager", item_type=None, use_regex=False, timeout=10)
                    setup.enter_selected_item(ignore=False, timeout=5)
                    setup.select(item_name="Set Time Out Value", item_type=None, use_regex=False, timeout=10)
                    setup.enter_selected_item(ignore=False, timeout=5)
                    setup.select(item_name="Auto Boot Time-out", item_type=None, use_regex=False, timeout=10)
                    setup.enter_selected_item(ignore=False, timeout=5)
                    setup.input_text("10")
                    setup.press(input_key="ENTER")
                    setup.select(item_name="Commit Changes and Exit", item_type=None, use_regex=False, timeout=10)
                    setup.enter_selected_item(ignore=False, timeout=5)
                    # verify
                    setup.enter_selected_item(ignore=False, timeout=5)
                    setup.select(item_name="Auto Boot Time-out", item_type=None, use_regex=False, timeout=10)
                    ret = setup.get_selected_item()  # type:
                    print(ret)
                    dc.dc_power_reset()
                    if boot.wait_for_entry_menu(timeout=60):
                        boot.press(input_key="F7")
                    boot.wait_for_bios_boot_menu(timeout=120)
                    boot.select(item_name="UEFI Internal Shell", item_type="", timeout=3, use_regex=False)
                    boot.enter_selected_item(ignore_output=True, timeout=5)
                    with ProviderFactory.create(self._eficfg, mock.MagicMock()) as uefi:  # type: UefiShellProvider
                        assert uefi.wait_for_uefi(60)
                        assert uefi.in_uefi()
                        assert uefi.execute("fs1:", timeout=60)


test_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

data_path = os.path.join(test_path, 'system', 'data')


def compare(f1, f2):
    with open(f1, 'r') as file1:
        with open(f2, 'r') as file2:
            line = 1
            while True:
                data1 = file1.readline()
                data2 = file2.readline()
                if line == 1:
                    line += 1
                    continue
                if data1 == data2:
                    if data1 and data2:
                        line += 1
                        continue
                    else:
                        return True, None
                else:
                    if data1.startswith('Table Address:') or data1.startswith('Inter Checksum:') or data1.startswith(
                            'Index=') or data1.startswith('EPS Checksum:'):
                        line += 1
                        continue
                    else:
                        break
    return False, f"error_line----{line}"


d = Debugging()
import random

func = [d.debug_provider_life_cycle_active, d.debug_simics, d.debug_provider_life_cycle_lazy, d.debug_simics_setupmenu]
result = {
    d.debug_provider_life_cycle_active.__name__: 0,
    d.debug_simics.__name__: 0,
    d.debug_provider_life_cycle_lazy.__name__: 0,
    d.debug_simics_setupmenu.__name__: 0,
}
for i in range(0, 1):
    # f = func[random.randint(0,2)]
    f = func[0]
    print("cycle {}:({})".format(i, f.__name__))
    f()
    result[f.__name__] += 1
    for k, v in result.items():
        print("{}:{}".format(k, v))
