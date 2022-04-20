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
The base implementation of UEFIShell
"""
import os
import re
import time
from datetime import datetime
from xml.etree.ElementTree import Element

from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.exceptions import TimeoutException, InvalidParameterError
from dtaf_core.providers.uefi_shell import UefiShellProvider
import xml

class BaseUefiShellProvider(UefiShellProvider):
    """
    Base Class that communicates with UEFI shell.
    """

    def __init__(self, cfg_opts, log):
        """
        Create a new UEFIProvider object.

        :param cfg_opts: xml.etree.ElementTree.Element of configuration options for execution environment
        :param log: Logger object to use for output messages
        """
        super(BaseUefiShellProvider, self).__init__(cfg_opts, log)
        self.buffer_name = 'uefi_buffer'
        self.buffer_size = 4 * 1024 * 1024
        self.uefi_page = re.compile(r'UEFI Interactive Shell|EFI Shell version|Shell>', re.I)
        self.uefi_prompt = re.compile(r'Shell>|FS\d+:[\\\w]*\\>', re.I)
        self.linesep = "\r\n"

        if self._config_model.driver_cfg.name == "com":
            if isinstance(cfg_opts, dict):
                self.drv_opts = cfg_opts["driver"]
            elif xml.etree.ElementTree.iselement(cfg_opts):
                self.drv_opts = ConfigurationHelper.get_driver_config(provider=cfg_opts, driver_name='com')
            else:
                self.drv_opts = None
        elif self._config_model.driver_cfg.name == "sol":
            if isinstance(cfg_opts, dict):
                self.drv_opts = cfg_opts["driver"]
            elif xml.etree.ElementTree.iselement(cfg_opts):
                self.drv_opts = ConfigurationHelper.get_driver_config(provider=cfg_opts, driver_name='sol')
            else:
                self.drv_opts = None
        elif self._config_model.driver_cfg.name == "wsol":
            if isinstance(cfg_opts, dict):
                self.drv_opts = cfg_opts["driver"]
            elif xml.etree.ElementTree.iselement(cfg_opts):
                self.drv_opts = ConfigurationHelper.get_driver_config(provider=cfg_opts, driver_name='wsol')
            else:
                self.drv_opts = None
        else:
            raise InvalidParameterError('Driver {com, sol} lost for UefishellProvider')

        self.serial = DriverFactory.create(self.drv_opts, log)
        self.serial.register(self.buffer_name, self.buffer_size)

    def __enter__(self):
        return super(BaseUefiShellProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(BaseUefiShellProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def wait_for_uefi(self, timeout):
        # type: (int) -> None
        """
        Wait for SUT booting/rebooting into UEFI shell within specific timeout.

        :param timeout: Maximum timeout seconds
        :raise InvalidParameterError: If timeout is a negative value
        :raise TimeoutException: If not get UEFI prompt within specific timeout
        :return: None
        """
        self._read_output(self.uefi_page, timeout)

    def exit_uefi(self):
        # type: () -> None
        """
        Exit UEFI shell.

        :return: None
        """
        self.execute('exit')

    def in_uefi(self):
        # type: () -> bool
        """
        Check if the SUT is really in UEFI shell or not.

        :return: True if in UEFI else False
        """
        try:
            self.execute(self.linesep, timeout=5)
            return True
        except TimeoutException:
            return False

    def shutdown(self):
        # type: () -> None
        """
        Do shutdown action in UEFI shell.

        :return: None
        """
        self.execute('reset -s')

    def reboot(self):
        # type: () -> None
        """
        Do reboot action in UEFI shell.

        :return: None
        """
        self.execute('reset -w')

    def warm_reset(self):
        # type: () -> None
        """
        Do warm reset action in UEFI shell.

        :return: None
        """
        self.execute('reset')

    def cold_reset(self):
        # type: () -> None
        """
        Do cold reset action in UEFI shell.

        :return: None
        """
        self.execute('reset -c')

    def execute(self, cmd, timeout=0, end_pattern=None):
        # type: (str, int) -> str
        """
        Execute cmd in UEFI shell.

        :param cmd: UEFI command
        :param timeout: Maximum execution timeout, 0 means no need to wait for output data
        :param end_pattern: search pattern in output of command. if any match, API will return the data received.
        :raise InvalidParameterError: If input is an empty string, or timeout is a negative value
        :raise TimeoutException: If not get result within specific timeout
        :return: Execution result
        """
        if not cmd:
            raise InvalidParameterError('UEFI cmd should not be blank')

        if not isinstance(cmd, str):
            raise InvalidParameterError('UEFI cmd should be a string')

        if timeout < 0:
            raise InvalidParameterError('Invalid timeout value: {}'.format(timeout))
        self._log.debug('Execute UEFI cmd: {}'.format(cmd))
        self._cleanup_buffer()
        for c in cmd:
            self.serial.write(c)
            time.sleep(0.1)
        self.serial.write(self.linesep)
        if 0 == timeout:
            return ''
        elif end_pattern is None:
            return self._read_output(self.uefi_prompt, timeout)
        else:
            pat = re.compile(end_pattern)
            return self._read_output(pat, timeout)

    def _cleanup_buffer(self):
        """
        cleanup buffer
        :return:
        """
        self.serial.read_from(self.buffer_name)

    def _read_output(self, flag, timeout):
        """
        Read data until flag within timeout seconds.

        :param flag: Compiled python RE object
        :param timeout: Maximum waiting seconds
        :raise InvalidParameterError: If timeout is a negative value
        :raise TimeoutException: If not get flag within specific timeout
        :return: Data string till flag
        """
        if timeout < 0:
            raise InvalidParameterError('Invalid timeout value: {}'.format(timeout))

        data = ''
        start = datetime.now()
        while (datetime.now() - start).seconds < timeout:
            c = self.serial.read_from(self.buffer_name)
            if not c:
                continue

            data += c
            if flag.search(data):
                self._log.debug('Response data: ' + data)
                return data
        else:
            self._log.debug('Response timeout: ' + data)
            raise TimeoutException('Timeout to wait for {} within {}s'.format(flag.pattern, timeout))
