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
import time
import logging
import dtaf_core.lib.os_lib as os_lib

from abc import ABCMeta, abstractmethod
from xml.etree import ElementTree
from six import add_metaclass
from dtaf_core.lib.os_lib import OsCommandResult
from dtaf_core.lib.exceptions import UnsupportedOsException, OsStateTransitionException
from dtaf_core.providers.base_provider import BaseProvider
from dtaf_core.lib.dtaf_constants import OperatingSystems
import datetime


@add_metaclass(ABCMeta)
class SutOsProvider(BaseProvider):
    """
    Provider for executing OS commands on an SUT.

    This class cannot be used directly, instead, this interface is applied to the subclasses, with a different subclass
    communication (SOL, Serial) This makes the dependency on specific hardware setups easier to identify.
    """

    # Constants for SutOsProvider
    SUPPORTED_OS_LIST = [OperatingSystems.WINDOWS, OperatingSystems.LINUX, OperatingSystems.ESXI]
    DEFAULT_CONFIG_PATH = "suts/sut/providers/sut_os"

    def __init__(self, cfg_opts, log):
        # type: (ElementTree.Element, logging.Logger) -> None
        """
        Create a new SutOsProvider object

        :param log: Logger object to use for debug and info messages
        :param cfg_opts: xml.etree.ElementTree.Element of configuration options for execution environment.
        """
        super(SutOsProvider, self).__init__(cfg_opts, log)
        self.os_shutdown_delay = self._config_model.shutdown_delay
        self.os_type = self._config_model.os_type
        self.os_subtype = self._config_model.os_subtype
        self.os_version = self._config_model.os_version
        self.os_kernel = self._config_model.os_kernel

        self.verify = self._config_model.verify

        # Confirm that this class supports the OS in use
        if self.os_type not in self.SUPPORTED_OS_LIST:
            raise UnsupportedOsException("OS {} not supported by SutOsProvider.".format(self.os_type))

        # Pull in OS-specific constants from os_constants based on the OS type (Linux, Windows, etc) and subtype
        # (RHEL, SLES, Fedora, etc. for Linux, Server 2016 or Server 2019 for Windows, etc.)
        try:
            self.os_consts = getattr(os_lib, self.os_type).get_subtype_cls(self.os_subtype, strict=False)
        except AttributeError:
            raise UnsupportedOsException(
                "OS {} not supported by SutOsProvider due to missing constant class.".format(self.os_type))

    def __enter__(self):
        return super(SutOsProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(SutOsProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def reboot(self, timeout):
        # type: (float) -> None
        """
        Reboot the SUT using its operating system.

        :raises OsBootTimeoutException: If reboot timeout expires.
        :raises OsStateTransitionException: If SUT did not reboot properly.
        :param timeout: Time in seconds to allow entry menu detection. If None, will return immediately after rebooting.
        :return: None
        """
        result = self.execute(self.os_consts.Commands.RESTART, self.os_shutdown_delay)
        # For some reason, if this command fails, it doesn't always return a non-zero value.
        # So, make sure stderr is empty as well (indicating no error messages). We also validate
        # after this that the SUT actually rebooted (OS not up anymore).
        try:
            if result.cmd_failed() or result.stderr != "":
                self._log.debug("Could not restart the SUT!")
        except Exception as ex:
            self._log.error("Could not restart the SUT! {0}".format(ex))
        self._log.info("'{}' has been sent to OS.".format(self.os_consts.Commands.RESTART))
        time.sleep(self.os_shutdown_delay)  # TODO: Find a better way to deal with this

        if self.is_alive():
            raise OsStateTransitionException("Could not restart the SUT! Was still alive after command was sent!")
        else:
            self.wait_for_os(timeout)

    def shutdown(self, timeout=None):
        # type: (float) -> None
        """
        Change system state to S5 using the SUT's operating system.

        :raises OsStateTransitionException: If SUT did not shut down properly.
        :param timeout: Time in seconds to allow SUT to enter into S5 power state.
        :return: None
        """
        if timeout:
            timewait = timeout
        else:
            timewait = self.os_shutdown_delay
        result = self.execute(self.os_consts.Commands.SHUTDOWN, self.os_shutdown_delay)
        # For some reason, if this command fails, it doesn't always return a non-zero value.
        # So, make sure stderr is empty as well (indicating no error messages). We also validate
        # after this that the SUT actually rebooted (OS not up anymore).
        if result.cmd_failed() or result.stderr != "":
            raise OsStateTransitionException("Could not shut down the SUT!")
        self._log.info("'{}' has been sent to OS.".format(self.os_consts.Commands.SHUTDOWN))
        start = datetime.datetime.now()
        while (datetime.datetime.now() - start).seconds < timewait:
            if not self.is_alive():
                return
        if self.is_alive():
            raise OsStateTransitionException("Could not shut down the SUT! Was still alive after command was sent!")

    @abstractmethod
    def execute(self, cmd, timeout, cwd=None):
        # type: (str, float, str) -> OsCommandResult
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
        raise NotImplementedError

    @abstractmethod
    def execute_async(self, cmd, cwd=None):
        # type: (str, str) -> OsCommandResult
        """
        Send a command to the SUTs active OS to execute in the background.

        The provided command will run in the background, so no response will be returned.

        :raises OsCommandException: If command fails to start.
                                    Note: This is not raised if the command fails, only if it fails to complete for some
                                    other reason, for example, if the environment has a problem or if the SUT's OS
                                    unexpectedly dies.
        :param cmd: String with the command to execute.
        :param cwd: If provided, absolute path to desired working directory for the command.
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def wait_for_os(self, timeout):
        # type: (float) -> None
        """
        Wait (for up to 'timeout' seconds) for SUT to enter the configured OS.

        :raises ValueError: If timeout is None or not a number.
        :raises OsBootTimeoutException: If SUT fails to reach the OS before 'timeout' elapses.
        :param timeout: Maximum time to wait for the OS, in seconds.
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def is_alive(self):
        # type: () -> bool
        """
        Check if the OS is alive and responsive.

        :return: True if OS is alive, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def copy_local_file_to_sut(self, source_path, destination_path):
        # type: (str, str) -> None
        """
        Copy local file to path on the SUT (note that in local execution this is equivalent to executing cp).

        :param source_path: Path to the source file to copy (on the machine the script is running on).
        :param destination_path: Path to the destination path to copy into (on the SUT regardless of where
                                 the script is running on).
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def copy_file_from_sut_to_local(self, source_path, destination_path):
        # type: (str, str) -> None
        """
        Copy file from SUT to local system (note that in local execution this is equivalent to executing cp).

        :param source_path: Path to the source path on SUT (on the SUT regardless of where
                            the script is running on).
        :param destination_path: Path to the destination file to copy (on the machine the script is running on).
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def check_if_path_exists(self, path, directory=False):
        # type: (str, bool) -> bool
        """
        Check if path exists on the SUT.

        :param path: String with path to check.
        :param directory: Set to True if 'path' is expected to be a directory, False otherwise.
        :return: True if path exists, False otherwise.
        """
        raise NotImplementedError
