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
import platform
import re
import time
import subprocess
import telnetlib

from collections import namedtuple
ReturnData = namedtuple('ReturnData','return_code, return_value')

from dtaf_core.lib.dtaf_constants import OperatingSystems
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.private.globals.return_code import (
    RET_SUCCESS,
    RET_TEST_FAIL,
    RET_ENV_FAIL,
    RET_INVALID_INPUT
)
from dtaf_core.providers.simics_provider import SimicsProvider
from dtaf_core.drivers.driver_factory import DriverFactory


class ComSimicsProvider(SimicsProvider):

    def __init__(self, cfg_opts, log):
        super(ComSimicsProvider, self).__init__(cfg_opts, log)
        if platform.system() != OperatingSystems.WINDOWS:
            raise RuntimeError("simics instance can only run on Windows hosts!")
        self._logger = log
        self.buffer_name = 'simics_buffer'
        self.buffer_size = 4 * 1024 * 1024
        self.drv_opts = ConfigurationHelper.get_driver_config(provider=cfg_opts, driver_name='com')
        self.serial = DriverFactory.create(self.drv_opts, log)
        self.serial.register(self.buffer_name, self.buffer_size)

        self._com_port = self._config_model.driver_cfg.port
        self._telnet_port = self._config_model.telnet_port
        self._serial_log = self._config_model.serial_log
        self._workspace = self._config_model.workspace
        self._simics_path = self._config_model.simics_path
        self._proc, self._client = None, None

    def __enter__(self):
        return super(ComSimicsProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(ComSimicsProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def _get_simics_process(self):
        try:
            check_list = [
                'simics-common.exe',
                'simics command line',
                'simics console',
                'simics-common',
            ]
            cmd = 'tasklist'
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ids = []
            out, err = p.communicate()
            for line in out.splitlines():
                self._log.debug(line)
                for x in check_list:
                    if x in line:
                        linx = line[len(x):].strip()
                        pat = re.search('\d+', linx)
                        if not pat:
                            continue
                        try:
                            ids.append((x, int(linx[:pat.regs[0][1]], 10)))
                        except Exception as ex:
                            self._log.error('error ex list {0}'.format(ex))
            self._log.debug('process list {0}'.format(ids))
            return True, ids
        except Exception as ex:
            self._log.error('ex {0}'.format(ex))
            return False, []

    def _launch_simics(self, configuration, simics_script):
        try:
            run_cmd_timeout = 30
            simics_end = b'simics>'
            mapping_cmd = [
                "alias serialCon        $system.serconsole.con -r",
                "alias platformCon      $system.console.con -r",
                "alias platformKbd      $system.mb.sb.kbd -r",
                "alias itp run-ivp-itp-remote",
                # ### ********* settings *************************************************************
                "rexec-limit 2000 20000000000",
                # ********* serial console settings **********************************************
                "$sercon_file = %s" % self._serial_log,
                "$consoleport = $system.mb.bmc.serial[0]",
                "$uart0_text_console = TRUE",
                "serialCon.capture-start $sercon_file -overwrite"
            ]
            serial_cmd = [
                "$consoledevice = $system.serconsole",
                "$realserialport = \"%s\"" % self._com_port,
                "$consoledevice.disconnect",
                "$consoledevice.switch-to-host-serial-console $realserialport",
                "connect $consoledevice.serial $consoleport"
            ]
            mapping_cmd += serial_cmd

            self._log.debug(
                "launch_simics: configuration {0} simics_script{1}".format(
                    configuration, simics_script))
            if not simics_script or not configuration or not isinstance(configuration, dict):
                self._log.error("return {0}".format(RET_INVALID_INPUT))
                return RET_INVALID_INPUT

            try:
                work_space = self._workspace.rstrip("\\") + "\\"
                proc_path = self._simics_path.rstrip("\\") + "\\simics-common.exe"
            except Exception as ex:
                self._log.error(ex)
                raise Exception(ex)

            self._log.debug("work_space = {0}, proc_path = {1}".format(work_space, proc_path))

            x_args = [
                proc_path,
                r'-no-gui',
                '-e',
                "telnet-frontend %d" % self._telnet_port,
                '-project',
                work_space
            ]

            self._proc = subprocess.Popen(args=x_args,
                                          shell=False,
                                          cwd=work_space,
                                          creationflags=subprocess.CREATE_NEW_CONSOLE
                                          )
            if not self._proc:
                self._log.error("self._proc not create {0}".format(RET_TEST_FAIL))
                return RET_TEST_FAIL

            self._log.debug("proc create ok {0}".format(self._proc))
            time.sleep(20)
            try:
                self._client = telnetlib.Telnet("localhost", self._telnet_port, timeout=120)
            except Exception as ex:
                self._log.error('create telnet client error... {0}'.format(ex))
                return RET_TEST_FAIL

            self._log.debug("write configuration")
            if configuration:
                for key, value in configuration.items():
                    ret = self._execute("%s=%s" % (str(key), str(value)), run_cmd_timeout, simics_end)
                    if ret.return_code != RET_SUCCESS:
                        self.shutdown_simics()
                        self._log.error("ret={0} {1}".format(ret.return_code, ret.return_value))
                        return ret.return_code
            self._log.debug("write configuration ok")

            self._log.debug("run-command-file")
            cmd = "run-command-file %s" % str(simics_script)
            ret = self._execute(cmd, run_cmd_timeout, simics_end)
            if ret.return_code != RET_SUCCESS:
                self.shutdown_simics()
                self._log.error("ret={0}".format(ret))
                return ret.return_code

            self._log.debug("run mapping_cmd")
            for cmd in mapping_cmd:
                self._log.debug("cmd {0}".format(cmd))
                ret = self._execute(cmd, run_cmd_timeout, simics_end)
                if ret.return_code != RET_SUCCESS:
                    self.shutdown_simics()
                    self._log.error("ret={0}".format(ret))
                    return ret.return_code

            self._log.debug("run")
            ret = self._execute("run", run_cmd_timeout, simics_end)
            if ret.return_code != RET_SUCCESS:
                self.shutdown_simics()
                self._log.error("ret={0}".format(ret))
                return ret.return_code
            return RET_SUCCESS
        except Exception as ex:
            self._log.error("launch_simics ex={0}".format(ex))
            self.shutdown_simics()
            return RET_ENV_FAIL

    def _execute(self, command_line, timeout, end_flag):
        try:
            self._log.debug("_execute {0} {1}".format(command_line, timeout))
            if not command_line or timeout is None or timeout < 0:
                self._log.error('invalid input')
                return ReturnData._make((RET_INVALID_INPUT, ""))

            if not self._proc:
                self._log.error('no proc available')
                return ReturnData._make((RET_ENV_FAIL, ""))

            if command_line[-1] != '\r':
                command_line += '\r'

            self._client.write((command_line.rstrip('\r') + '\r').encode("utf-8"))
            self._log.debug("run_simics_command write cmd ok {0}".format(command_line))
            recv_data = self._client.__read_until(end_flag, timeout)
            self._log.debug(recv_data)
            ret_code = RET_TEST_FAIL
            if recv_data and end_flag in recv_data:
                ret_code = RET_SUCCESS
            return ReturnData._make((ret_code, recv_data.decode("utf-8")))
        except Exception as ex:
            self._log.error("run_simics_command {0}".format(ex))
            return ReturnData._make((RET_ENV_FAIL, ""))

    def launch_simics(self, configuration, simics_script):
        self._log.debug('ENV TEST START')
        self._get_simics_process()
        self._log.debug('ENV TEST END')

        self._log.debug('Clean ENV')
        ret = self.shutdown_simics()
        if not ret == RET_SUCCESS:
            return ret
        self._log.debug('LAUNCH SIMICS')
        for i in range(3):
            self._log.debug('try start simics {0} '.format(i))
            ret = self._launch_simics(configuration, simics_script)
            if ret == RET_SUCCESS:
                break
            self.shutdown_simics()
            time.sleep(120)
        return ret

    def shutdown_simics(self):
        ret = RET_TEST_FAIL
        try:
            self._log.debug("shutdown_simics")
            if self._client:
                self._client.close()
                self._client = None
            if self._proc:
                self._proc.terminate()
                time.sleep(5)
                self._proc = None
            result, value = self._get_simics_process()
            if result and value:
                for name, id in value:
                    try:
                        cmd = 'taskkill /t /f /im {0}'.format(name)
                        self._log.debug(cmd)
                        child = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                        result, err = child.communicate()
                        self._log.debug("result: {0}".format(result))
                        if err:
                            self._log.debug('error: {0}'.format(err))
                            raise Exception(err)
                    except Exception as ex:
                        self._log.error('ex {0}'.format(ex))
            self._log.debug("shutdown_simics success")
            time.sleep(5)
            ret = RET_SUCCESS
        except Exception as ex:
            self._log.error('ex {0}'.format(ex))
        return ret

    def run_simics_command(self, command_line, timeout, end_pattern=None):
        try:
            running_end = b'running>'
            if self._client:
                self._client.close()
                self._client = None
            if not self._client:
                try:
                    self._client = telnetlib.Telnet("localhost", self._com_port, timeout=timeout)
                except Exception as ex:
                    self._log.error('ex {0}'.format(ex))
                    return RET_TEST_FAIL
            ret = self._execute(command_line, timeout, running_end)
            self._client.close()
            self._client = None
            return ret
        except Exception as ex:
            self._log.error('ex {0}'.format(ex))
            return ReturnData._make((RET_TEST_FAIL, str(ex)))

    def run_simics_test_script(self, configuration, simics_script, end_pattern_list, timeout):
        try:
            self._log.debug(
                "launch_simics: simics_script{0}".format(simics_script))
            if not simics_script or not configuration or not isinstance(configuration, dict):
                self._log.error("return {0}".format(RET_INVALID_INPUT))
                return ReturnData._make((RET_INVALID_INPUT, ""))

            work_space = self._workspace.rstrip("\\") + "\\"
            proc_path = self._simics_path.rstrip("\\") + "\\simics-common.exe"
            self._log.debug("work_space = {0}, proc_path = {1}".format(work_space, proc_path))

            x_args = [
                proc_path,
                r'-no-gui',
                '-e',
                "telnet-frontend %d" % self._telnet_port,
                '-project',
                work_space
            ]

            self._proc = subprocess.Popen(args=x_args,
                                          shell=False,
                                          cwd=work_space,
                                          creationflags=subprocess.CREATE_NEW_CONSOLE
                                          )
            print("self._proc {0}".format(self._proc))
            if not self._proc:
                self._log.error("self._proc not create {0}".format(RET_TEST_FAIL))
                return ReturnData._make((RET_TEST_FAIL, ""))
            time.sleep(20)
            print("write configuration")
            if configuration:
                for key, value in configuration.items():
                    ret = self.run_simics_command("%s=%s" % (str(key), str(value)), 10)
                    if ret.return_code != RET_SUCCESS:
                        self.shutdown_simics()
                        self._log.error("ret={0} {1}".format(ret.return_code, ret.result_value))
                        return ret.return_code
            self._log.debug("write configuration ok")

            self._log.debug("run-command-file")
            cmd = "run-command-file %s" % str(simics_script)
            ret = self.run_simics_command(cmd, 20)
            if ret.return_code != RET_SUCCESS:
                self.shutdown_simics()
                print("ret={0}".format(ret))
                return ret

            self._log.debug("run")
            ret = self.run_simics_command("run", 10)
            if ret.return_code != RET_SUCCESS:
                self.shutdown_simics()
                self._log.error("ret={0}".format(ret))
                return ret

            if not self._proc:
                self._log.error(RET_ENV_FAIL)
                return ReturnData._make((RET_ENV_FAIL, ""))
            if not self._client:
                self._client = telnetlib.Telnet("localhost", self._telnet_port, timeout=timeout)

            recv_data = self._client.expect(end_pattern_list, timeout)
            if recv_data:
                return ReturnData._make((RET_SUCCESS, recv_data))
            else:
                return ReturnData._make((RET_TEST_FAIL, ""))
        except Exception as ex:
            self._log.error(
                "launch_simics {0} ex={1}".format(RET_ENV_FAIL, ex))
            self.shutdown_simics()
            return ReturnData._make((RET_ENV_FAIL, ""))


