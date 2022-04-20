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
"""
SUT OS Provider
"""

import json
import sys
import time
import io

from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.drivers.internal.socket_driver import SocketDriver
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.exceptions import OsStateTransitionException, DriverIOError
from dtaf_core.lib.exceptions import TimeoutException, InvalidParameterError, \
    OsBootTimeoutException, OsCommandException
from dtaf_core.lib.os_lib import OsCommandResult
from dtaf_core.lib.private.globals.return_code import RET_SUCCESS, TYPE_ENTEROS, \
    RET_TEST_FAIL, TYPE_RESPONSE, TYPE_EXECUTE, TYPE_EXECUTE_ASYNC, TYPE_READ, TYPE_WRITE, TYPE_OPEN_FOR_WRITE, \
    TYPE_OPEN_FOR_READ, TYPE_CLOSE
from dtaf_core.providers.sut_os_provider import SutOsProvider
import base64


class SocketSutOsProvider(SutOsProvider):
    """
    Base Class that communicates with UEFI shell.
    """

    def __init__(self, cfg_opts, log):
        """
        Create a new UEFIProvider object.

        :param cfg_opts: xml.etree.ElementTree.Element of configuration options for execution environment
        :param log: Logger object to use for output messages
        """
        super(SocketSutOsProvider, self).__init__(cfg_opts, log)
        self._logger = log
        self.buffer_name = 'sut_buffer'
        self.buffer_size = 4 * 1024 * 1024
        if 'socket' == self._config_model.driver_cfg.name:
            self.drv_opts = ConfigurationHelper.get_driver_config(provider=cfg_opts, driver_name='socket')
        else:
            raise InvalidParameterError('Driver {com, sol, socket} lost for SutOsProvider')

        self.socket = DriverFactory.create(self.drv_opts, log)  # type: SocketDriver

    def __enter__(self):
        return super(SocketSutOsProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(SocketSutOsProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def reboot(self, timeout):
        """
        Reboot the SUT using its operating system.

        :raises OsBootTimeoutException: If reboot timeout expires.
        :raises OsStateTransitionException: If SUT did not reboot properly.
        :param timeout: Time in seconds to allow entry menu detection. If None, will return immediately after rebooting.
        :return: None
        """
        try:
            self.execute_async(self.os_consts.Commands.RESTART, self.os_shutdown_delay)
            self.socket.close()
        except Exception as ex:
            print(ex)
        # result = self.execute_async(self.os_consts.Commands.RESTART, self.os_shutdown_delay)
        # For some reason, if this command fails, it doesn't always return a non-zero value.
        # So, make sure stderr is empty as well (indicating no error messages). We also validate
        # after this that the SUT actually rebooted (OS not up anymore).
        # if result.return_code != RET_SUCCESS:
        #     raise OsStateTransitionException("Could not restart the SUT!")
        # self._log.info("'{}' has been sent to OS.".format(self.os_consts.Commands.RESTART))
        # time.sleep(self.os_shutdown_delay)  # TODO: Find a better way to deal with this
        time.sleep(self.os_shutdown_delay)
        if self.is_alive():
            raise OsStateTransitionException("Could not restart the SUT! Was still alive after command was sent!")
        else:
            self.wait_for_os(timeout)

    def shutdown(self, timeout):
        # type: (float) -> None
        """
        Change system state to S5 using the SUT's operating system.

        :raises OsStateTransitionException: If SUT did not shut down properly.
        :param timeout: Time in seconds to allow SUT to enter into S5 power state.
        :return: None
        """
        self.execute_async(self.os_consts.Commands.SHUTDOWN, self.os_shutdown_delay)
        # For some reason, if this command fails, it doesn't always return a non-zero value.
        # So, make sure stderr is empty as well (indicating no error messages). We also validate
        # after this that the SUT actually rebooted (OS not up anymore).
        self._log.info("'{}' has been sent to OS.".format(self.os_consts.Commands.SHUTDOWN))
        time.sleep(self.os_shutdown_delay)  # TODO: Find a better way to deal with this

        if self.is_alive():
            raise OsStateTransitionException("Could not shut down the SUT! Was still alive after command was sent!")

    def wait_for_os(self, timeout, flag=r'START_UP'):
        """
        Wait (for up to 'timeout' seconds) for SUT to enter the configured OS.

        :param flag:
        :raises ValueError: If timeout is None or not a number.
        :raises OsBootTimeoutException: If SUT fails to reach the OS before 'timeout' elapses.
        :param timeout: Maximum time to wait for the OS, in seconds.
        :return: None/data
        """
        start = time.time()
        self.socket.close()
        self.socket.open()
        json_msg = self.socket.receive(timeout)
        print(json_msg)
        message = json.loads(json_msg)
        enter_os_system, enter_os_state = message[TYPE_ENTEROS]
        os_type = '{}'.format(enter_os_system)
        if os_type.lower() not in ("windows", "linux"):
            raise OsBootTimeoutException("SUT failed to boot within {} seconds!".format(timeout))
        else:
            new_os_type = os_type.lower()[0].upper() + os_type.lower()[1:]
            if self.verify == 'true' and self.os_type.lower() != new_os_type.lower():
                raise OsCommandException('Verify Error')
            self.os_type = new_os_type
        end = time.time()
        total_time_taken = (abs(start - end))
        total_time_taken = ("{:05.2f}".format(total_time_taken))
        self._log.info("Enterd Into OS It Took {0} Seconds".format(total_time_taken))

    def is_alive(self):
        # type: () -> bool
        """
        Check if the OS is alive and responsive.

        :return: True if OS is alive, False otherwise.
        """

        try:
            start = time.time()
            data = self.execute("dir", 5)
            if data.return_code == 0:
                end = time.time()
                total_time_taken = (abs(start - end))
                total_time_taken = ("{:05.2f}".format(total_time_taken))
                self._log.debug("OS is Alive {0} Seconds".format(total_time_taken))
                return True
            else:
                return False
        except TimeoutException:
            return False
        except Exception:
            return False

    def execute(self, cmd, timeout, cwd=None):
        # type: (str, int) -> OsCommandResult
        """
        Send a command to the SUTs active OS to execute.

        After execution is done, this method will return an OsCommandResult object, which contains the command exit code
        and output.

        :raises ValueError: If timeout is None or not a number.
        :raises OsCommandTimeoutException: If command fails to complete before the timeout elapses.
        :raises OsCommandException: If command fails to complete for a non-timeout reason.
                                    Note: This is not raised if the command fails, only if it fails to complete for some
                                    other reason, for example, if the environment has a problem or if the SUT's OS
                                    unexpectedly dies.
        :param cmd: String with the command to execute.
        :param timeout: Timeout in seconds to allow for the command to complete. Must be greater than 0.
        :param cwd: If provided, absolute path to desired working directory for the command.
        :return: OsCommandResult instance with the command execution results.
        """
        if not isinstance(cmd, str) or not isinstance(timeout, int):
            raise OsCommandException("Command execution failed! Error")
        if timeout <= 0 or cmd == "":
            raise OsCommandException("Command execution failed! Error")

        try:
            cmd_dict = dict({TYPE_EXECUTE: [cmd, timeout]})
            json_str = json.dumps(cmd_dict)
            self.socket.send(json_str)
            ret = RET_SUCCESS
            json_msg = self.socket.receive(timeout)
            print("json_msg={}".format(json_msg))
            message = json.loads(json_msg)
            launch_code, exit_code, output = message[TYPE_RESPONSE]
            if not launch_code == 0:
                ret = RET_TEST_FAIL

            ret = OsCommandResult(exit_code, io.StringIO(output), io.StringIO(""))
            return ret
        except DriverIOError as ex:
            print(ex)
            raise OsCommandException("Command execution failed! Error: {}".format(ex))
        except TimeoutError as ex:
            print(ex)
            raise OsCommandException("Command execution failed! Error: {}".format(ex))
        except Exception as ex:
            print(ex)
            raise OsCommandException("Command execution failed! Error: {}".format(ex))

    def execute_async(self, cmd, cwd=None):
        # type: # (str, int) -> OsCommandResult
        """
        Send a command to the SUTs active OS to execute.

        After execution is done, this method will return an OsCommandResult object, which contains the command exit code
        and output.

        :raises ValueError: If timeout is None or not a number.
        :raises OsCommandTimeoutException: If command fails to complete before the timeout elapses.
        :raises OsCommandException: If command fails to complete for a non-timeout reason.
                                    Note: This is not raised if the command fails, only if it fails to complete for some
                                    other reason, for example, if the environment has a problem or if the SUT's OS
                                    unexpectedly dies.
        :param cmd: String with the command to execute.
        :param cwd: If provided, absolute path to desired working directory for the command.
        :return: OsCommandResult instance with the command execution results.
        """
        if not isinstance(cmd, str):
            raise OsCommandException("Command execution failed! Error")

        try:
            cmd_dict = dict({TYPE_EXECUTE_ASYNC: [cmd, 10]})
            json_str = json.dumps(cmd_dict)
            self.socket.send(json_str)
            ret = OsCommandResult(0, io.StringIO('Command executed'), io.StringIO(""))
            return ret
        except DriverIOError as ex:
            raise OsCommandException("Command execution failed! Error: {}".format(ex))
        except Exception as ex:
            raise OsCommandException("Command execution failed! Error: {}".format(ex))

    def copy_local_file_to_sut(self, source_path, destination_path):
        # type: (str, str) -> None
        """
        Copy local file to path on the SUT (note that in local execution this is equivalent to executing cp).

        :param source_path: Path to the source file to copy (on the machine the script is running on).
        :param destination_path: Path to the destination path to copy into (on the SUT regardless of where
                                 the script is running on).
        :return: None
        """
        try:
            with open(source_path, "rb") as fd:
                cmd_dict = dict({TYPE_OPEN_FOR_WRITE: [destination_path, 0]})
                json_str = json.dumps(cmd_dict)
                self.socket.send(json_str)
                ret = RET_SUCCESS
                json_msg = self.socket.receive(10)
                print("json_msg={}".format(json_msg))
                message = json.loads(json_msg)
                launch_code, exit_code, output = message[TYPE_RESPONSE]
                if launch_code == 0:
                    data = fd.read(102400)
                    while data:
                        msg = base64.b64encode(data).decode('utf-8')
                        msg_dict = dict({TYPE_WRITE: [msg, 0]})
                        json_str = json.dumps(msg_dict)
                        self.socket.send(json_str)
                        data = fd.read(102400)
                    cmd_dict = dict({TYPE_CLOSE: ["", 0]})
                    json_str = json.dumps(cmd_dict)
                    self.socket.send(json_str)
                    json_msg = self.socket.receive(10)
                    message = json.loads(json_msg)
                    launch_code, exit_code, output = message[TYPE_RESPONSE]
                    if launch_code == 0:
                        ret = OsCommandResult(0, sys.stdout, sys.stderr)
                        ret.stdout.write('Filed Copied')
                        return ret
                raise DriverIOError("Fail to copy file")
        except DriverIOError as ex:
            raise OsCommandException("Command execution failed! Error: {}".format(ex))
        except Exception as ex:
            raise OsCommandException("Command execution failed! Error: {}".format(ex))

    def copy_file_from_sut_to_local(self, source_path, destination_path):
        # type: (str, str) -> None
        """
        Copy file from SUT to local system (note that in local execution this is equivalent to executing cp).

        :param source_path: Path to the source path on SUT (on the SUT regardless of where
                            the script is running on).
        :param destination_path: Path to the destination file to copy (on the machine the script is running on).
        :return: None
        """

        try:
            with open(destination_path, "wb+") as fd:
                cmd_dict = dict({TYPE_OPEN_FOR_READ: [source_path, 0]})
                json_str = json.dumps(cmd_dict)
                self.socket.send(json_str)
                ret = RET_SUCCESS
                json_msg = self.socket.receive(10)
                print("json_msg={}".format(json_msg))
                message = json.loads(json_msg)
                launch_code, exit_code, output = message[TYPE_RESPONSE]
                if launch_code == 0:
                    # send command to read data from the file
                    msg_dict = dict({TYPE_READ: [source_path, 0]})
                    json_str = json.dumps(msg_dict)
                    self.socket.send(json_str)
                    # receive data
                    json_msg = self.socket.receive(10)
                    print("json_msg={}".format(json_msg))
                    message = json.loads(json_msg)
                    launch_code, exit_code, output = message[TYPE_RESPONSE]
                    if launch_code == 0:
                        data = base64.b64encode(output.encode("utf-8"))
                        while data:
                            fd.write(data)
                            # send command to read data from the file
                            msg_dict = dict({TYPE_READ: [source_path, 0]})
                            json_str = json.dumps(msg_dict)
                            self.socket.send(json_str)
                            # receive data
                            json_msg = self.socket.receive(10)
                            print("json_msg={}".format(json_msg))
                            message = json.loads(json_msg)
                            launch_code, exit_code, output = message[TYPE_RESPONSE]
                            if launch_code == 0:
                                data = base64.b64encode(output.encode("utf-8"))
                            else:
                                raise DriverIOError("Fail to Receive Data")
                    cmd_dict = dict({TYPE_CLOSE: ["", 0]})
                    json_str = json.dumps(cmd_dict)
                    self.socket.send(json_str)
                    json_msg = self.socket.receive(10)
                    message = json.loads(json_msg)
                    launch_code, exit_code, output = message[TYPE_RESPONSE]
                    if launch_code == 0:
                        ret = OsCommandResult(0, sys.stdout, sys.stderr)
                        ret.stdout.write('Filed Copied')
                        return ret
                raise DriverIOError("Fail to copy file")
        except DriverIOError as ex:
            raise OsCommandException("Command execution failed! Error: {}".format(ex))
        except Exception as ex:
            raise OsCommandException("Command execution failed! Error: {}".format(ex))

    def check_if_path_exists(self, path, directory=False):
        # type: (str, bool) -> bool
        """
        Check if path exists on the SUT.

        :param path: String with path to check.
        :param directory: Set to True if 'path' is expected to be a directory, False otherwise.
        :return: True if path exists, False otherwise.
        """
        ret = self.execute('dir {}'.format(path), 10)
        if ret.return_code:
            return ret
        else:
            lines = ret.stdout.readlines()
            file_1 = False
            dir_0 = False
            for line in lines:
                if line.find("File Not Found") != -1:
                    ret.return_code = -1
                    return ret
                if line.find(r"1 File(s)") != -1:
                    file_1 = True
                if line.find(r"0 Dir(s)") != -1:
                    dir_0 = True
            if (file_1 and dir_0) or directory:
                return ret
            ret.return_code = -1
            return ret
