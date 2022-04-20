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
from dtaf_core.drivers.internal.simics_driver import SimicsDriver
from dtaf_core.drivers.internal.console.console import Channel
from dtaf_core.lib.exceptions import TimeoutException, InvalidParameterError
from dtaf_core.providers.uefi_shell import UefiShellProvider
import xml

class SimicsUefiShellProvider(UefiShellProvider):
    """
    Base Class that communicates with UEFI shell.
    """

    def __init__(self, cfg_opts, log):
        """
        Create a new UEFIProvider object.

        :param cfg_opts: xml.etree.ElementTree.Element of configuration options for execution environment
        :param log: Logger object to use for output messages
        """
        super(SimicsUefiShellProvider, self).__init__(cfg_opts, log)
        self._linesep = "\r\n"
        self.buffer_name = 'uefi_buffer_{}'.format(self._config_model.driver_cfg.host)
        self.buffer_size = 4 * 1024 * 1024
        self.uefi_page = re.compile(r'[Ss]hell>|[Ff][Ss]\d+:[\\\w]*\\>', re.I)
        self.uefi_prompt = r'[Ss]hell>|[Ff][Ss]\d+:[\\\w]*\\>'

        if self._config_model.driver_cfg.name == "simics":
            if isinstance(cfg_opts, dict):
                self.drv_opts = cfg_opts["driver"]
            elif xml.etree.ElementTree.iselement(cfg_opts):
                self.drv_opts = ConfigurationHelper.get_driver_config(provider=cfg_opts, driver_name='simics')
            else:
                self.drv_opts = None
        else:
            raise InvalidParameterError('Driver {com, sol} lost for UefishellProvider')

        self.serial = DriverFactory.create(self.drv_opts, log) #type: SimicsDriver
        self.serial.register(self.buffer_name, self.buffer_size)

    def __enter__(self):
        self.serial.register(self.buffer_name, self.buffer_size)
        self.serial.start()
        return super(SimicsUefiShellProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.serial.stop()
        self.serial.unregister(self.buffer_name)
        super(SimicsUefiShellProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def wait_for_uefi(self, timeout):
        # type: (int) -> None
        """
        Wait for SUT booting/rebooting into UEFI shell within specific timeout.

        :param timeout: Maximum timeout seconds
        :raise InvalidParameterError: If timeout is a negative value
        :raise TimeoutException: If not get UEFI prompt within specific timeout
        :return: None
        """
        self.serial.start()
        self.serial.register(self.buffer_name, self.buffer_size)
        channel = self.serial.SerialChannel #type: Channel
        channel.clean_buffer()
        _start = datetime.now()
        data = ""
        while (datetime.now()-_start).seconds < timeout:
            d = channel.read_from()
            if d:
                data += d
                if self.uefi_page.search(data):
                    return True
        raise TimeoutException("fail to enter uefi")

    def close(self):
        self.serial.stop()

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
            self.execute("", timeout=5)
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
        self.serial.start()
        self.serial.register(self.buffer_name, self.buffer_size)

        if not isinstance(cmd, str):
            raise InvalidParameterError('UEFI cmd should be a string')

        if timeout < 0:
            raise InvalidParameterError('Invalid timeout value: {}'.format(timeout))
        self._log.debug('Execute UEFI cmd: {}'.format(cmd))
        serial_channel = self.serial.SerialChannel #type: Channel
        if end_pattern:
            pat = "%s" % end_pattern
        else:
            pat = "%s" % self.uefi_prompt
        from dtaf_core.lib.private.cl_utils.adapter.private.pyte_interface.gernal_pyte_api import GernalPYTE
        pyte = GernalPYTE(80, 24)
        serial_channel.clean_buffer()
        serial_channel.write(data="%s%s" % (cmd, self._linesep))
        __start = datetime.now()
        data = ""
        echo_command = False
        while (datetime.now()-__start).seconds < timeout:
            d = serial_channel.read_from()
            if d:
                pyte.feed(d)
                data += d
            if not echo_command and re.search(cmd, "\n".join(pyte.get_screen_display())):
                echo_command = True
                pyte = GernalPYTE(80, 24)
            elif echo_command and re.search(pat, "\n".join(pyte.get_screen_display())):
                pyte = GernalPYTE(80, 24)
                pyte.feed(data, history=True)
                data = pyte.get_history()
                return "\n".join(data)
        return None


    def _cleanup_buffer(self):
        """
        cleanup buffer
        :return:
        """
        self.serial.register(self.buffer_name, self.buffer_size)
        self.serial.SerialChannel.clean_buffer()
