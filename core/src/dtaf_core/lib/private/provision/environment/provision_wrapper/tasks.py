#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
INTEL CONFIDENTIAL
Copyright 2020 Intel Corporation All Rights Reserved.

The source code contained or described herein and all documents related to the source code
("Material") are owned by Intel Corporation or its suppliers or licensors. Title to the Material remains
with Intel Corporation or its suppliers and licensors. The Material contains trade secrets and
proprietary and confidential information of Intel or its suppliers and licensors. The Material is
protected by worldwide copyright and trade secret laws and treaty provisions. No part of the
Material may be used, copied, reproduced, modified, published, uploaded, posted, transmitted,
distributed, or disclosed in any way without Intel's prior express written permission.

No license under any patent, copyright, trade secret or other intellectual property right is granted to
or conferred upon you by disclosure or delivery of the Materials, either expressly, by implication,
inducement, estoppel or otherwise. Any license under such intellectual property rights must be
express and approved by Intel in writing.
"""
import os
import sys
from utils import get_config_params, serialize, get_pkg, get_project_pkg


class Task:
    """
    Superclass with tasks definitions: OS/FW installation.
    """
    def __init__(self, task: str, input_parameters: dict) -> None:
        self.input_parameters = input_parameters
        self.task = task
        self.output_command = {}

    def create(self) -> None:
        """ Task handling dispatcher. """
        if self.task == 'windows_installation':
            event = WindowsInstallation(self.task, self.input_parameters)
        elif self.task == 'linux_rhel_installation':
            event = LinuxRHELInstallation(self.task, self.input_parameters)
        elif self.task == 'linux_centos_installation':
            event = LinuxCentOSInstallation(self.task, self.input_parameters)
        elif self.task == 'esxi_installation':
            event = ESXIInstallation(self.task, self.input_parameters)
        elif self.task == 'ifwi_flashing':
            event = IFWIFlashing(self.task, self.input_parameters)
        elif self.task == 'bmc_banino_flashing':
            event = BMCBaninoFlashing(self.task, self.input_parameters)
        elif self.task == 'bmc_redfish_flashing':
            event = BMCRedfishFlashing(self.task, self.input_parameters)
        elif self.task == 'cpld_flashing':
            event = CPLDFlashing(self.task, self.input_parameters)
        else:
            print('ERROR: Unsupported task: {}'.format(self.task))
            sys.exit(5)

        oneliner = event.oneliner()
        config_params = get_config_params(self.task, self.input_parameters)
        self.output_command = 'python {script} {oneliner} {config_params}'.format(script=event.SCRIPT_NAME,
                                                                                  oneliner=oneliner,
                                                                                  config_params=config_params)


class WindowsInstallation(Task):
    """
    Windows OS installation handler.
    """
    SCRIPT_NAME = os.path.join('windows', 'paiv_win_os_online_installation.py')

    def oneliner(self) -> str:
        """ One-lined provisioning script arguments. """
        params = {
            'atf_path_os_pkg': get_pkg(pkg_type='win_os', input_parameters=self.input_parameters)
        }
        return serialize(params)


class LinuxRHELInstallation(Task):
    """
    Linux/RHEL installation handler.
    """
    SCRIPT_NAME = os.path.join('linux_rhel', 'paiv_rhel_os_online_installation.py')

    def oneliner(self) -> str:
        """ One-lined provisioning script arguments. """
        params = {
            'atf_path_os_pkg': get_pkg(pkg_type='os', input_parameters=self.input_parameters),
            'atf_path_sft_pkg': get_pkg(pkg_type='sft', input_parameters=self.input_parameters)
        }
        return serialize(params)


class LinuxCentOSInstallation(Task):
    """
    Linux/CentOS installation handler.
    """
    SCRIPT_NAME = os.path.join('linux_centos', 'paiv_cent_os_online_installation.py')

    def oneliner(self) -> str:
        """ One-lined provisioning script arguments. """
        params = {
            'atf_path_os_pkg': get_pkg(pkg_type='os', input_parameters=self.input_parameters),
            'atf_path_sft_pkg': get_pkg(pkg_type='sft', input_parameters=self.input_parameters)
        }
        return serialize(params)


class ESXIInstallation(Task):
    """
    ESXi installation handler.
    """
    SCRIPT_NAME = os.path.join('esxi', 'paiv_esxi_os_online_installation.py')

    def oneliner(self) -> str:
        """ One-lined provisioning script arguments. """
        params = {
            'atf_path_os_pkg': get_pkg(pkg_type='os', input_parameters=self.input_parameters),
            'atf_path_sft_pkg': get_pkg(pkg_type='sft', input_parameters=self.input_parameters)
        }
        return serialize(params)


class IFWIFlashing(Task):
    """
    IFWI flashing handler.
    """
    SCRIPT_NAME = os.path.join('ifwi_flashing', 'paiv_ifwi_flashing_online.py')

    def oneliner(self) -> str:
        """ One-lined provisioning script arguments. """
        params = {
            'atf_path_ifwi_pkg': get_project_pkg(project='IFWI', input_parameters=self.input_parameters)
        }
        return serialize(params)


class BMCBaninoFlashing(Task):
    """
    BMC/Banino flashing handler.
    """
    SCRIPT_NAME = os.path.join('bmc_flashing', 'paiv_bmc_flashing_banino_online.py')

    def oneliner(self) -> str:
        """ One-lined provisioning script arguments. """
        params = {
            'atf_path_bmc_pkg': get_project_pkg(project='BMC', input_parameters=self.input_parameters)
        }
        return serialize(params)


class BMCRedfishFlashing(Task):
    """
    BMC/Redfish flashing handler.
    """
    SCRIPT_NAME = os.path.join('bmc_flashing', 'paiv_bmc_flashing_redfish_online.py')

    def oneliner(self) -> str:
        """ One-lined provisioning script arguments. """
        params = {
            'atf_path_bmc_red_pkg': get_project_pkg(project='BMC', input_parameters=self.input_parameters)
        }
        return serialize(params)


class CPLDFlashing(Task):
    """
    CPLD flashing handler.
    """
    SCRIPT_NAME = os.path.join('cpld_flashing', 'paiv_cpld_flashing_online.py')

    def oneliner(self) -> str:
        """ One-lined provisioning script arguments. """
        params = {
            'atf_path_cpld_main_pkg': get_project_pkg(project='PLD_Main', input_parameters=self.input_parameters),
            'atf_path_cpld_secondary_pkg': get_project_pkg(project='PLD_Secondary',
                                                           input_parameters=self.input_parameters)
        }
        return serialize(params)
