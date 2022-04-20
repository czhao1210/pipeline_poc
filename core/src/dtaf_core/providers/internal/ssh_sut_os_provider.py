#!/usr/bin/env python
"""
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
"""
import logging
import socket
import time
import traceback

import fabric
import paramiko
import six

if six.PY2:
    from pathlib import Path
if six.PY3:
    from pathlib2 import Path
import re
from datetime import datetime
from dtaf_core.lib.dtaf_constants import OperatingSystems
from dtaf_core.lib.exceptions import OsCommandTimeoutException, OsCommandException, OsBootTimeoutException
from dtaf_core.lib.os_lib import OsCommandResult, LinuxDistributions
from dtaf_core.providers.sut_os_provider import SutOsProvider
from invoke.exceptions import CommandTimedOut
from numbers import Number
from paramiko.ssh_exception import NoValidConnectionsError, SSHException
from xml.etree import ElementTree
import json


class SshSutOsProvider(SutOsProvider):
    """
    Executes provided commands on a remote SUT over SSH.

    Linux:
     - The 'screen' utility must be installed to support asynchronous command execution (Check the documentation for
       the distribution in use to see how to install it).
     - SSH must be enabled on the SUT (Check the documentation for the distribution in use to see how to set this up).
    Windows:
     - Asynchronous execution of commands requires that the adminuser is logged in autologin recommended.
     - To use this provider with Windows, you must install Microsoft's OpenSSH implementation on the server first. See
       https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse for instructions
       for enabling OpenSSH on Windows (10, Server 2019, and later).
     - The default shell for Windows is 'cmd', keep this in mind when writing test content and libraries.
       'PowerShell' is not yet supported by this provider.
    """

    OS_POLL_INTERVAL = 10.0
    DIR_MANIP_TIMEOUT = 1.0
    NET_TIMEOUT_COMP = 3.0
    ASYNC_TRIGGER_TIMEOUT = 0.5

    # Unit test hook
    # Pytest's sys.stdin object is a misbehaving non-stream object. This breaks the stdin mirroring inherent in
    # Invoke. When running with Pytest, this must be set to False in order to disable stdin mirroring, which ignores
    # the misbehaving object entirely. For now, at least, we do not use this functionality.
    # As the _ indicates, this is NOT a public-facing part of the API, and should not be used by general developers.
    # If pytest ever supports stdin mirroring better, this will be removed!
    _PYTEST_HOOK = None

    def __init__(self, cfg_opts, log):
        # type: (ElementTree.Element, logging.Logger) -> None
        super(SshSutOsProvider, self).__init__(cfg_opts, log)
        self._load_config()
        self.__async_session_type = 'tmux' if self.os_type == OperatingSystems.LINUX and self.os_subtype == LinuxDistributions.RHEL and float(
            self.os_version) >= 8.5 else 'screen'

    def _load_config(self):
        self._ip = self._config_model.driver_cfg.ip
        self._port = self._config_model.driver_cfg.port
        self._retry_cnt = self._config_model.driver_cfg.retry_cnt
        self._user = self._config_model.driver_cfg.user
        self._password = self._config_model.driver_cfg.password
        self._jump_host = self._config_model.driver_cfg.jump_host
        self._jump_user = self._config_model.driver_cfg.jump_user
        self._jump_auth = self._config_model.driver_cfg.jump_auth

        self._server_path = self._config_model.driver_cfg.server_path
        self._enable = self._config_model.driver_cfg.enable

    def __enter__(self):
        return super(SshSutOsProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return super(SshSutOsProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def _get_jump_host(self):
        jump_host = None
        if self._jump_host is not None:
            jump_host = fabric.Connection(self._jump_host, user=self._jump_user)
            if isinstance(self._jump_auth, paramiko.pkey.PKey):
                jump_host.connect_kwargs.pkey = self._jump_auth
            elif self._jump_auth is not None:
                jump_host.connect_kwargs.password = self._jump_auth
        return jump_host

    def _set_sut_auth(self, target):
        if isinstance(self._password, paramiko.pkey.PKey):
            target.connect_kwargs.pkey = self._password
        elif self._password is not None:
            target.connect_kwargs.password = self._password

    def is_alive(self):
        ret = self._ip.split("|")
        for i in range(0, len(ret)):
            alive = False
            try:
                # Attempt to establish an SSH connection to the OS
                with fabric.Connection(ret[i], user=self._user, gateway=self._get_jump_host(),
                                       port=self._port) as target:
                    self._set_sut_auth(target)
                    target.open()
                    result = target.run('echo alive', hide=True, warn=True, timeout=15,
                                        in_stream=self._PYTEST_HOOK)
                    target.close()
                if not result.stdout and not result.stderr:
                    self._log.debug("SUT is alive, but couldn't get any message from it {0}".format(ret[i]))
                    alive = False
                else:
                    self._log.debug(
                        "SSH connection successfully established and closed. OS is alive.{0}".format(ret[i]))
                    alive = True
            except NoValidConnectionsError:
                # This means that the OS is up, but not allowing connections on port 22. Usually, this just means that the
                # OS isn't fully up, and just needs a bit more time.
                self._log.debug(
                    "SUT is alive, but couldn't connect to port 22. SUT may still be booting, or sshd is down {0}".format(
                        ret[i]))
            except SSHException as e:
                # Logs specific error in case SUT never comes back alive to assist with debug.
                self._log.debug("Unable to connect to SUT. Message: " + str(e))
            except socket.error as e:
                # Logs specific socket error in case SUT never comes back alive to assist with debug.
                message = e if six.PY2 else e.strerror  # Paramiko uses TimeoutErrors in Python3
                self._log.debug(
                    "OS is not alive. Got socket error code {0}  ".format(ret[i]) + str(e.errno) + ", " + str(message))
            return alive and True

    def _execute_script(self, cmd, timeout):
        exec_result = self._execute_cmd("ps aux | grep server_run.py", timeout, cwd=self._server_path)
        if 'python3 server_run.py' not in exec_result.stdout:
            exec_result = self._execute_cmd('nohup python3 server_run.py > server_run.log 2&>1 &', timeout,
                                            cwd=self._server_path)
            if exec_result.return_code:
                raise OsCommandException("Command execution failed! Error: {}".format(str(exec_result.stderr)))

        exec_result = self._execute_cmd("python3 server_get.py --execute '%s'" % cmd, timeout,
                                        cwd=self._server_path)
        if exec_result.return_code:
            raise OsCommandException("Command execution failed! Error: {}".format(str(exec_result.stderr)))
        pid = re.findall('=======\n([\s\S]*)\n=======', exec_result.stdout)[0]

        start_time = datetime.now()
        while (datetime.now() - start_time).seconds > timeout:
            try:
                exec_result_status = self._execute_cmd("python3 server_get.py --status %s" % pid, timeout,
                                                       cwd=self._server_path)
                status = re.findall('=======\n([\s\S]*)\n=======', exec_result_status.stdout)[0]
                if status == '1':
                    break
                time.sleep(1)
            except Exception:
                time.sleep(1)

        exec_result_result = self._execute_cmd("python3 server_get.py --result %s" % pid, timeout,
                                               cwd=self._server_path)
        result = re.findall('=======\n([\s\S]*)\n=======', exec_result_result.stdout)[0]
        result = json.loads(result)
        return_code = result["return_code"]
        stdout = result["stdout"]
        stderr = result["stderr"]
        return OsCommandResult(return_code, stdout, stderr)

    def _execute_cmd(self, cmd, timeout, cwd):
        ret = self._ip.split("|")
        ex_out = None
        for i in range(0, len(ret)):
            try:
                with fabric.Connection(ret[i], user=self._user, gateway=self._get_jump_host(),
                                       port=self._port) as target:
                    self._set_sut_auth(target)
                    with target.cd(cwd):
                        self._log.debug("Executing command {}".format(cmd))
                        exec_result = target.run(cmd, hide=True, warn=True, timeout=timeout,
                                                 in_stream=self._PYTEST_HOOK)  # See comment above for details
                    target.close()
                return OsCommandResult(exec_result.exited, exec_result.stdout, exec_result.stderr)
            except OsCommandException as e_cmd:
                ex_out = e_cmd
                self._log.error("SSH Communicating ip is Down {0}".format(ret[i]))
            except OsCommandTimeoutException as e_cmd_timeout:
                ex_out = e_cmd_timeout
                self._log.error("SSH Communicating ip is Down {0}".format(ret[i]))
            except Exception as e:
                ex_out = e
                self._log.error("SSH Communicating ip is Down {0}".format(ret[i]))
        raise ex_out

    def execute(self, cmd, timeout, cwd=None):
        retries = 0
        while retries <= int(self._retry_cnt):
            retries += 1
            # Check timeout value
            if timeout is None or not isinstance(timeout, Number):
                raise ValueError("Timeout must be supplied as a valid numeric value in seconds!")
            timeout = timeout + self.NET_TIMEOUT_COMP  # Compensate for slow SSH connections
            if retries > 1:
                timeout = timeout * 2
            # Set desired working directory
            if cwd is None:
                cwd = "."

            # Execute command with Fabric
            try:
                if self._enable:
                    return self._execute_script(cmd, timeout)
                else:
                    return self._execute_cmd(cmd, timeout, cwd)
            except CommandTimedOut:
                if retries == self._retry_cnt:
                    raise OsCommandTimeoutException("Command {} timed out!".format(cmd))
                else:
                    continue
            except Exception as e:
                if retries == self._retry_cnt:
                    self._log.exception(traceback.format_exc())
                    raise OsCommandException("Command execution failed! Error: {}".format(str(e)))
                else:
                    continue

    def _execute_async_screen(self, cmd, cwd=None, ps_name="dtaf_fabric", log_enable=False, log_name="/root/screenlog"):
        """
        Execute an OS command in the background so that test can progress without waiting for the command to finish

        :param cmd: Unix/Linux style bash command
        :param cwd: Change working directory if needed
        :param ps_name: str type to be passed to the screen command, session will appear with this name to the
         "screen -ls" command. ps_name not tested in Windows and windows method left at original hard-coded name.
        :param log_enable: Set to 'True' if screen log is needed.
        :param log_name: Specify the name of the log file.
        :return return the path of the log file if 'log_enable' set to True, void otherwise.
        """
        # Per Fabric's documentation, use screen to run in the background
        if log_enable:
            self.execute("rm -f {}".format(log_name), self.ASYNC_TRIGGER_TIMEOUT)
            result = self.execute("screen -L -Logfile {} -dmS {} bash -c '{}'".format(log_name, ps_name, cmd),
                                  self.ASYNC_TRIGGER_TIMEOUT, cwd)
            if result.cmd_failed():
                raise OsCommandException(
                    "Unable to launch background process! Ensure screen is installed on the SUT.")
            return log_name
        else:
            result = self.execute("screen -dmS {} bash -c '{}'".format(ps_name, cmd), self.ASYNC_TRIGGER_TIMEOUT,
                                  cwd)
            if result.cmd_failed():
                raise OsCommandException(
                    "Unable to launch background process! Ensure screen is installed on the SUT.")

    def _kill_async_session_screen(self, cwd=None, ps_name="dtaf_fabric"):
        """
        Kills the SCREEN sessions that was created by method 'execute_async'.
        :param cwd: Change working directory if needed.
        :param ps_name: str type to be passed to the screen command, session will appear with this name to the
         "screen -ls" command.
        """
        session_check = self.execute("screen -ls | grep {}".format(ps_name), self.ASYNC_TRIGGER_TIMEOUT, cwd)
        if session_check.cmd_failed():
            self._log.warning("screen session {} not found!".format(ps_name))
            return
        result = self.execute("screen -X -S {} kill".format(ps_name), self.ASYNC_TRIGGER_TIMEOUT, cwd)
        if result.cmd_failed():
            self._log.error(result.stdout)
            raise OsCommandException("Unable to terminate screen session {}!".format(ps_name))

    def _execute_async_tmux(self, cmd, cwd=None, ps_name="dtaf_fabric", log_enable=False, log_name="/root/screenlog"):
        if log_enable:
            self.execute("rm -f {}".format(log_name), self.ASYNC_TRIGGER_TIMEOUT)
            result = self.execute("tmux new-session -d -s {}".format(ps_name),
                                  self.ASYNC_TRIGGER_TIMEOUT, cwd)
            if result.cmd_failed():
                raise OsCommandException(
                    "Unable to launch background process! Ensure tmux is installed on the SUT.")
            else:
                self.execute(f"tmux attach -t {ps_name}", self.ASYNC_TRIGGER_TIMEOUT, cwd)
                self.execute(cmd, self.ASYNC_TRIGGER_TIMEOUT, cwd)
                self.execute("tmux capture-pane -S -.", self.ASYNC_TRIGGER_TIMEOUT, cwd)
                self.execute(f"tmux save-buffer {log_name}", self.ASYNC_TRIGGER_TIMEOUT, cwd)
                self.execute(f"tmux kill-session -t {ps_name}", self.ASYNC_TRIGGER_TIMEOUT, cwd)

            return log_name
        else:
            result = self.execute("tmux new-session -d -s {} '{}'".format(ps_name, cmd),
                                  self.ASYNC_TRIGGER_TIMEOUT,
                                  cwd)
            if result.cmd_failed():
                raise OsCommandException(
                    "Unable to launch background process! Ensure screen is installed on the SUT.")

    def _kill_async_session_tmux(self, cwd=None, ps_name="dtaf_fabric"):
        session_check = self.execute("tmux ls | grep {}".format(ps_name), self.ASYNC_TRIGGER_TIMEOUT, cwd)
        if session_check.cmd_failed():
            self._log.warning("tmux session {} not found!".format(ps_name))
            return
        result = self.execute("tmux kill-session -t {}".format(ps_name), self.ASYNC_TRIGGER_TIMEOUT, cwd)
        if result.cmd_failed():
            self._log.error(result.stdout)
            raise OsCommandException("Unable to terminate tmux session {}!".format(ps_name))

    def wait_for_os(self, timeout):
        start = time.time()
        if timeout is None or not isinstance(timeout, Number):
            raise ValueError("Timeout must be supplied as a valid numeric value in seconds!")
        self._log.debug("Waiting for boot, up to {} seconds.".format(timeout))
        booted = False
        start_time = time.time()
        while not booted and time.time() - start_time < timeout:
            time.sleep(self.OS_POLL_INTERVAL)
            booted = self.is_alive()
            self._log.debug("SUT is " + ("alive!" if booted else "still not booted."))
        if not booted:
            raise OsBootTimeoutException("SUT failed to boot within {} seconds!".format(timeout))
        end = time.time()
        total_time_taken = (abs(start - end))
        total_time_taken = ("{:05.2f}".format(total_time_taken))
        self._log.info("Enter Into OS It Took {0} Seconds".format(total_time_taken))

    def copy_local_file_to_sut(self, source_path, destination_path):
        if self.os_type == OperatingSystems.WINDOWS:
            # fabric understands posix style, so transform the destination path (remote)  to posix format
            # also prepend destination path with '/' to treat it as absolute path
            destination_path = "/" + Path(destination_path).as_posix()
        ret = self._ip.split("|")
        for i in range(0, len(ret)):
            try:
                with fabric.Connection(ret[i], user=self._user, gateway=self._get_jump_host(),
                                       port=self._port) as target:
                    self._set_sut_auth(target)
                    target.put(source_path, destination_path)
                    target.close()
            except CommandTimedOut:
                raise OsCommandTimeoutException("Command timed out!")
            except Exception as e:
                self._log.exception(traceback.format_exc())
                raise OsCommandException("Command execution failed! Error: {}".format(str(e)))

    def copy_file_from_sut_to_local(self, source_path, destination_path):
        if self.os_type == OperatingSystems.WINDOWS:
            # fabric understands posix style, so transform the source path (remote)  to posix format
            # also prepend source path with '/' to treat it as absolute path
            source_path = "/" + Path(source_path).as_posix()
        ret = self._ip.split("|")
        for i in range(0, len(ret)):
            try:
                with fabric.Connection(ret[i], user=self._user, gateway=self._get_jump_host(),
                                       port=self._port) as target:
                    self._set_sut_auth(target)
                    target.get(source_path, destination_path)
                    self._log.debug("Copying (sut-local) file from {} to {}".format(source_path, destination_path))
                    target.close()
            except CommandTimedOut:
                raise OsCommandTimeoutException("Command timed out!")
            except Exception as e:
                self._log.exception(traceback.format_exc())
                raise OsCommandException("Command execution failed! Error: {}".format(str(e)))

    def check_if_path_exists(self, path, directory=False):
        if self.os_type == OperatingSystems.LINUX:
            test = '-d' if directory else '-f'
            return self.execute("test " + test + " " + path, self.DIR_MANIP_TIMEOUT).return_code == 0
        elif self.os_type == OperatingSystems.WINDOWS:
            result = self.execute("powershell Test-Path '" + path + "'", self.DIR_MANIP_TIMEOUT)
            return result.stdout.strip() == "True"
        else:
            raise NotImplementedError("This function does not yet support OS " + str(self.os_type) + "!")

    def update_configuration(self, update_cfg_opts, update_log):
        super(SshSutOsProvider, self).update_configuration(update_cfg_opts=update_cfg_opts,
                                                           update_log=update_log)
        self.__init__(update_cfg_opts, update_log)

    def execute_async(self, cmd, cwd=None, ps_name="dtaf_fabric", log_enable=False, log_name="/root/screenlog"):
        if self.os_type == OperatingSystems.LINUX:
            if self.__async_session_type == 'screen':
                return self._execute_async_screen(cmd, cwd=cwd, ps_name=ps_name, log_enable=log_enable,
                                                  log_name=log_name)
            else:
                return self._execute_async_tmux(cmd, cwd=cwd, ps_name=ps_name, log_enable=log_enable,
                                                log_name=log_name)

        elif self.os_type == OperatingSystems.WINDOWS:
            # Remove task if it already exists
            try:
                self.execute("powershell Unregister-ScheduledTask -TaskName 'dtaf_fabric' -Confirm False "
                             "-ErrorAction SilentlyContinue", self.ASYNC_TRIGGER_TIMEOUT)
            except OsCommandTimeoutException:
                raise OsCommandException("Unable to execute command on sut! Verify Administrator is logged in.")
            # Create task
            task = "\"" + "cmd.exe /C start "
            if cwd:
                task += "/d '" + cwd + "' "
            task += "/wait " + cmd + "\""
            schtask_create = r"schtasks /create /SC ONCE /TN dtaf_fabric /TR {} /ST 00:00 /F".format(task)
            schtask = self.execute(schtask_create, self.ASYNC_TRIGGER_TIMEOUT)
            if schtask.cmd_failed():
                raise OsCommandException("Unable to create scheduled task!")

            # Run task
            schtaskrun = self.execute("schtasks /run /TN dtaf_fabric", self.ASYNC_TRIGGER_TIMEOUT)
            if schtaskrun.cmd_failed():
                raise OsCommandException("Unable to run scheduled task!")
        else:
            raise RuntimeError("execute_async is not yet implemented for OS {}".format(self.os_type))

    def kill_async_session(self, cwd=None, ps_name="dtaf_fabric"):
        if self.os_type == OperatingSystems.LINUX:
            if self.__async_session_type == 'screen':
                return self._kill_async_session_screen(cwd=cwd, ps_name=ps_name)
            else:
                return self._kill_async_session_tmux(cwd=cwd, ps_name=ps_name)
        else:
            raise NotImplementedError("This function does not yet support OS " + str(self.os_type) + "!")
