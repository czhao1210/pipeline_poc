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
import platform
import subprocess
import time
from xml.etree import ElementTree as ET

import pytest
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.dtaf_constants import OperatingSystems, Framework
from dtaf_core.lib.exceptions import OsCommandException
from dtaf_core.lib.exceptions import OsCommandTimeoutException
from dtaf_core.providers.provider_factory import ProviderFactory


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

    @classmethod
    def exception(cls, msg):
        print(msg)


log = _Log()


@pytest.mark.soundwave1
class TestSuites(object):

    def setup_class(self):
        tree = ET.ElementTree()
        tree.parse(r'tests/system/data/ssh_sut_os_configuration.xml')
        root = tree.getroot()
        sut = ConfigurationHelper.find_sut(root, {'ip': '10.13.168.111'})[0]
        acpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='ac')
        dcpwrcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='dc')
        self.sutcfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name='sut_os',
                                                              attrib={'error': 'false'})
        self.sutcfg_error = ConfigurationHelper.get_provider_config(sut=sut, provider_name='sut_os',
                                                                    attrib={'error': 'true'})
        self.acpower = ProviderFactory.create(acpwrcfg, log)
        self.dcpower = ProviderFactory.create(dcpwrcfg, log)
        self.obj = ProviderFactory.create(self.sutcfg, log)
        self.obj._PYTEST_HOOK = False

        self.sutcfg_execution = ConfigurationHelper.get_provider_config(sut=sut, provider_name='sut_os',
                                                                        attrib={'error': 'other'})
        self.execution_obj = ProviderFactory.create(self.sutcfg_execution, log)
        self.execution_obj._PYTEST_HOOK = False

        self.acpower.ac_power_off(10)
        time.sleep(10)
        self.acpower.ac_power_on(10)
        time.sleep(20)
        self.dcpower.dc_power_off(60)
        time.sleep(20)
        self.dcpower.dc_power_on(60)
        time.sleep(400)

    def test_python_script_execution_error(self):
        ret = self.execution_obj.execute('python /root/error_testcase.py', 5)
        assert ret.return_code == 1
        assert ret.stdout == 'stdout content\n'
        assert isinstance(ret.stderr, str) and len(ret.stderr) != 0

    def test_python_script_execution(self):
        ret = self.execution_obj.execute('python /root/testcase.py', 5)
        assert ret.return_code == 0
        assert ret.stdout == 'python script is success\n'
        assert ret.stderr == ''

    def test_shell_script_execution(self):
        ret = self.execution_obj.execute('/root/testcase.sh', 5)
        assert ret.return_code == 0
        assert ret.stdout == 'shell script is success\n'
        assert ret.stderr == ''

    def test_os_cmd_diffcfg(self):
        assert_val = False
        example_cmd = {OperatingSystems.LINUX: "ls /usr", OperatingSystems.WINDOWS: "dir C:\\"}
        self.obj.update_configuration(self.sutcfg_error, log)
        try:
            self.obj.execute(example_cmd[self.obj.os_type], 0.1)
        except OsCommandException as e:
            assert_val = True
        assert assert_val
        self.obj.update_configuration(self.sutcfg, log)
        result = self.obj.execute(example_cmd[self.obj.os_type], 0.1)
        assert result

    def test_os_cmd_with_cwd(self):
        test_dir = {OperatingSystems.LINUX: "/usr/bin", OperatingSystems.WINDOWS: "C:\\"}
        dir_cmd = {OperatingSystems.LINUX: "pwd", OperatingSystems.WINDOWS: "cd"}
        try:
            result = self.obj.execute(dir_cmd[self.obj.os_type], 1.0, cwd=test_dir[self.obj.os_type]).stdout.strip()
            assert result
        except KeyError:
            self.skipTest("os cmd test not supported on " + self.obj.os_type)

    def test_os_cmd_async(self):
        background_cmd = {
            OperatingSystems.LINUX: "sleep 25",
        }
        get_background_cmd = {
            OperatingSystems.LINUX: "ps aux | grep sleep"
        }
        try:
            self.obj.execute_async(background_cmd[self.obj.os_type])
            # Not using assertEqual directly here, as Windows may end up with a different method for checking this
            result = 2 == self.obj.execute(get_background_cmd[self.obj.os_type], 2.0).stdout.count(
                background_cmd[self.obj.os_type])
            assert result
        except KeyError:
            self.skipTest("Async execution not yet supported on " + self.obj.os_type)

    def test_cmd_timeout(self):
        sleep_cmd = {OperatingSystems.LINUX: "sleep 10", OperatingSystems.WINDOWS: "timeout 10"}
        try:
            ret = self.obj.execute(sleep_cmd[self.obj.os_type], -3)
        except OsCommandTimeoutException:
            return
        except KeyError:
            self.skipTest("cmd timeout test not supported on OS " + self.obj.os_type)

    def test_path_check_file(self):
        target_files = {
            OperatingSystems.LINUX: ("/usr/bin/ls", "/usr/bin/ls_fake"),
        }
        try:
            assert self.obj.check_if_path_exists(target_files[self.obj.os_type][0]) == True
            assert self.obj.check_if_path_exists(target_files[self.obj.os_type][1]) == False
        except KeyError:
            self.skipTest("Exec os " + str(self.obj.os_type) + " is not yet supported!")

    def test_path_check_dir(self):
        target_dirs = {
            OperatingSystems.LINUX: ("/usr/bin", "/usr/bin_fake"),
        }
        try:
            assert self.obj.check_if_path_exists(target_dirs[self.obj.os_type][0], True) == True
            assert self.obj.check_if_path_exists(target_dirs[self.obj.os_type][1], True) == False
        except KeyError:
            self.skipTest("Exec os " + str(self.obj.os_type) + " is not yet supported!")

    def test_file_copy(self):
        target_file_paths = {
            OperatingSystems.LINUX: "/tmp/" + os.path.split(Framework.CFG_FILE_PATH[platform.system()])[-1],

        }
        local_file_paths = {
            OperatingSystems.WINDOWS: os.path.join("C:\\Temp",
                                                   os.path.split(Framework.CFG_FILE_PATH[platform.system()])[-1])
        }
        cleanup_target_cmd = {
            OperatingSystems.LINUX: " ".join(["rm", target_file_paths[OperatingSystems.LINUX]]),
        }
        cleanup_local_cmd = {
            OperatingSystems.WINDOWS: ["del", local_file_paths[platform.system()]]
        }

        try:
            self.obj.copy_local_file_to_sut(Framework.CFG_FILE_PATH[platform.system()],
                                            target_file_paths[self.obj.os_type])
            assert self.obj.check_if_path_exists(target_file_paths[self.obj.os_type]) == True
            self.obj.copy_file_from_sut_to_local(target_file_paths[self.obj.os_type],
                                                 local_file_paths[platform.system()])
            assert os.path.isfile(local_file_paths[platform.system()]) == True

            self.obj.execute(cleanup_target_cmd[self.obj.os_type], 1.0)
            assert self.obj.check_if_path_exists(target_file_paths[self.obj.os_type]) == False

            subprocess.check_call(cleanup_local_cmd[platform.system()], shell=True)

        except KeyError:
            self.skipTest("Combination of exec OS {} and SUT OS {} is not yet supported!".format(platform.system(),
                                                                                                 self.obj.os_type))
        except AssertionError:
            self.obj.execute(cleanup_target_cmd[self.obj.os_type], 1.0)
            subprocess.run(cleanup_local_cmd[platform.system()])

    def test_reboot(self):
        self.acpower.ac_power_off(10)
        time.sleep(10)
        self.acpower.ac_power_on(10)
        time.sleep(20)
        self.dcpower.dc_power_off(60)
        time.sleep(20)
        self.dcpower.dc_power_on(60)
        time.sleep(400)
        self.obj.reboot(400.0)
        assert self.obj.is_alive() == True

    def test_shutdown(self):
        self.obj.shutdown(15.0)
        assert self.obj.is_alive() == False
