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

import io
import json
import time
from datetime import datetime

import dtaf_core.lib.os_lib as os_lib
from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.exceptions import OsStateTransitionException, DriverIOError
from dtaf_core.lib.exceptions import TimeoutException, InvalidParameterError, \
    OsBootTimeoutException, OsCommandException
from dtaf_core.lib.os_lib import OsCommandResult
from dtaf_core.lib.private.serial_transport import TransportTimeout, TransportError, Message
from dtaf_core.providers.sut_os_provider import SutOsProvider
from dtaf_core.drivers.internal.powershell_driver import PowershellDriver


class PowershellSutOsProvider(SutOsProvider):
    """
    Base Class that communicates with UEFI shell.
    """

    def __init__(self, cfg_opts, log):
        """
        Create a new UEFIProvider object.

        :param cfg_opts: xml.etree.ElementTree.Element of configuration options for execution environment
        :param log: Logger object to use for output messages
        """
        super(PowershellSutOsProvider, self).__init__(cfg_opts, log)
        self.drv_opts = ConfigurationHelper.get_driver_config(provider=cfg_opts, driver_name="powershell")

    def __enter__(self):
        return super(PowershellSutOsProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(PowershellSutOsProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def reboot(self, timeout):
        """
        Reboot the SUT using its operating system.

        :raises OsBootTimeoutException: If reboot timeout expires.
        :raises OsStateTransitionException: If SUT did not reboot properly.
        :param timeout: Time in seconds to allow entry menu detection. If None, will return immediately after rebooting.
        :return: None
        """
        self.execute_async(self.os_consts.Commands.RESTART, self.os_shutdown_delay)
        # result = self.execute_async(self.os_consts.Commands.RESTART, self.os_shutdown_delay)
        # For some reason, if this command fails, it doesn't always return a non-zero value.
        # So, make sure stderr is empty as well (indicating no error messages). We also validate
        # after this that the SUT actually rebooted (OS not up anymore).
        # if result.return_code != RET_SUCCESS:
        #     raise OsStateTransitionException("Could not restart the SUT!")
        # self._log.info("'{}' has been sent to OS.".format(self.os_consts.Commands.RESTART))
        time.sleep(self.os_shutdown_delay)  # TODO: Find a better way to deal with this
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

    def wait_for_os(self, timeout):
        _start = datetime.now()
        while (datetime.now()-_start).seconds < timeout and not self.is_alive():
            time.sleep(5)
        return self.is_alive()

    def is_alive(self):
        # type: () -> bool
        """
        Check if the OS is alive and responsive.

        :return: True if OS is alive, False otherwise.
        """
        try:
            data = self.execute("dir", 15)
            if data.return_code == 0:
                return True
            else:
                return False
        except TimeoutException as timeout_ex:
            return False
        except Exception as ex:
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
        if not isinstance(cmd, str) or (not isinstance(timeout, int) and timeout is not None):
            raise OsCommandException("Command execution failed! Error")
        if (timeout is not None and timeout <= 0) or cmd == "":
            raise OsCommandException("Command execution failed! Error")

        try:
            with DriverFactory.create(self.drv_opts, self._log) as drv: #type: PowershellDriver
                ret = drv.remote_execute(cmd=cmd, timeout=timeout)
                return OsCommandResult(0, io.StringIO(ret), io.StringIO(""))
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
            with DriverFactory.create(self.drv_opts, self._log) as drv: #type: PowershellDriver
                drv.remote_execute_async(cmd=cmd)
                return OsCommandResult(0, io.StringIO("command({}) executed".format(cmd)), io.StringIO(""))
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
            with DriverFactory.create(self.drv_opts, self._log) as drv: #type: PowershellDriver
                drv.copy_local_to_remote(src_file=source_path, dest_file=destination_path)
        except DriverIOError as ex:
            raise OsCommandException("copy local to remote failed! Error: {}".format(ex))
        except Exception as ex:
            raise OsCommandException("copy local to remote failed! Error: {}".format(ex))

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
            with DriverFactory.create(self.drv_opts, self._log) as drv: #type: PowershellDriver
                drv.copy_remote_to_local(src_file=source_path, dest_file=destination_path)
        except DriverIOError as ex:
            raise OsCommandException("copy local to remote failed! Error: {}".format(ex))
        except Exception as ex:
            raise OsCommandException("copy local to remote failed! Error: {}".format(ex))

    def check_if_path_exists(self, path, directory=False):
        # type: (str, bool) -> bool
        """
        Check if path exists on the SUT.

        :param path: String with path to check.
        :param directory: Set to True if 'path' is expected to be a directory, False otherwise.
        :return: True if path exists, False otherwise.
        """
        try:
            with DriverFactory.create(self.drv_opts, self._log) as drv: #type: PowershellDriver
                command = "dir %s" % path
                ret = drv.remote_execute(cmd=command, timeout=None)
                if ret.startswith("Can"):
                    return False
                return True
        except DriverIOError as ex:
            return False
        except Exception as ex:
            raise OsCommandException("unexpected issue: {}".format(ex))
