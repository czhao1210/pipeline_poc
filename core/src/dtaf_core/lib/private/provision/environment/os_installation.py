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

import re
import os
import platform
import subprocess
import sys

import six

if six.PY2:
    from pathlib import Path
if six.PY3:
    from pathlib2 import Path

from src.lib.content_configuration import ContentConfiguration
from src.environment.environment_constants import OsInstallConstants
from src.environment.os_prerequisites import OsPreRequisitesLib
from src.lib import content_exceptions
from src.lib.dtaf_content_constants import InventoryConstants


class OsInstallation:
    """
    This class implementation has os installation methods for rhel.
    """

    def __init__(self, log, cfg_opts):
        self._log = log
        self._cfg_opts = cfg_opts

        self._common_content_configuration = ContentConfiguration(self._log)

        self.os_pkg_path = self._common_content_configuration.get_os_pkg_path()
        self.sft_pkg_path = self._common_content_configuration.get_sft_pkg_path()

    def get_environment_path(self, required_dir_name, mode="offline"):
        config_file_path = Path(os.path.dirname(os.path.realpath(__file__))).parent
        config_file_src_path = None
        self._log.info("Path from framework till source: '{}'".format(config_file_path))
        for root, dirs, files in os.walk(str(config_file_path)):
            for name in dirs:
                if name.startswith("environment"):
                    config_file_src_path = os.path.join(root, name)
                    for root, dirs, files in os.walk(str(config_file_src_path)):
                        for name in dirs:
                            if name.startswith(required_dir_name):
                                config_file_src_path = os.path.join(root, name)
                                for root, dirs, files in os.walk(str(config_file_src_path)):
                                    for name in files:
                                        if mode in name:
                                            config_file_src_path = os.path.join(root, name)

        if not config_file_src_path.endswith(".py"):
            self._log.error("Unable to find the execution file under the path : {}, please check provided directory "
                            "name is accurate...".format(config_file_src_path))
            raise RuntimeError

        print("Path of the execution file: '{}'".format(config_file_src_path))
        return config_file_src_path

    @staticmethod
    def get_sut_inventory_file_path():
        """
        Function to get the sut_inventory file from Inventory directory.
        """
        if not os.path.exists(InventoryConstants.SUT_INVENTORY_FILE_NAME):
            raise content_exceptions.TestNAError("sut inventory config file does not exists...")

        return InventoryConstants.SUT_INVENTORY_FILE_NAME

    def rhel_os_installation(self):
        """
        Function to install the OS
        """
        ret_value = False
        exec_file_path = self.get_environment_path(OsInstallConstants.DIR_NAME_RHEL_OS)

        cmd = "python " + exec_file_path + " --LOCAL_OS_PACKAGE_LOCATION {} --LOCAL_SOFTWARE_PACKAGE_LOCATION " \
                                           "{}".format(self.os_pkg_path, self.sft_pkg_path)
        cmd_res = os.system(cmd)
        if cmd_res == 0:
            ret_value = True
        return ret_value

    def windows_os_installation(self):
        """
        Function to install the Windows OS
        """
        ret_value = False
        exec_file_path = self.get_environment_path(OsInstallConstants.DIR_NAME_WIN_OS)

        cmd = "python " + exec_file_path + " --LOCAL_OS_PACKAGE_LOCATION {}".format(self.os_pkg_path)

        cmd_res = os.system(cmd)
        if cmd_res == 0:
            ret_value = True
        return ret_value
