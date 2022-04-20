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
Pduusb Driver Layer
"""
import subprocess
import time
from abc import ABCMeta, abstractmethod
from os.path import dirname, join

import six

from dtaf_core.drivers.base_driver import BaseDriver


class PduusbDriverException(Exception):
    """Exception for when RSC fails to execute the requested command."""
    pass


@six.add_metaclass(ABCMeta)
class BasePduusbDriver(BaseDriver):
    """
    Wrapper interface for working with the dll for Belwin usb PDU

    PhysicalControlProvider and PowerControlProvider
    use this driver to implement their interfaces with pduusb dll
    """

    def __init__(self, cfg_opts, log):
        super(BasePduusbDriver, self).__init__(cfg_opts, log)
        self.pduusb_ac_port = self._driver_cfg_model.pduusb_ac_port

    @abstractmethod
    def remove_power(self):
        """
        Remove AC Power from the SUT.

        :raises PduusbDriverException: If RSC fails to execute the requested command.
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def connect_power(self):
        """
        Connect AC power to the SUT.

        :raises RscDriverException: If usb pdu fails to execute the requested command.
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def ac_connected(self, timeout):
        # type: (None) -> bool
        """
        Get AC power Detection of SUT.
        :return:
            True    -    AC POWER Detected
            NONE     -   AC POWER NOT Detected

        :raise DriverIOError: if command execution failed in driver
        """
        raise NotImplementedError


class PduusbDriver(BasePduusbDriver):
    """
    Provides platform control through the USBPower.dll ofor
    """

    def __init__(self, cfg_opts, log):
        super(PduusbDriver, self).__init__(cfg_opts, log)
        dirname(__file__)
        join(dirname(__file__), r"wrapper", r"usb_pdu.py")
        self.wrapper_script = join(dirname(__file__), "wrapper", r"usb_pdu.py")

        self.usb_pdu_port = str(self.pduusb_ac_port)

        self.dll_path = join(dirname(__file__), '..', '..', 'collateral', 'pduusb', 'USBPower')

    def __call_wrapper(self, port, action, *args):
        # Assemble script command
        cmd = ["python", self.wrapper_script, self.dll_path, port, action]

        if args is not None:
            cmd.extend(map(str, args))
        self._log.info("Running pdu cmd->" + str(cmd))

        # Execute command
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        try:
            self._log.debug("process pid={}".format(str(proc.pid)))
            cmd_output = proc.communicate(timeout=15)[0]

        except subprocess.CalledProcessError as call_error:  # this is called if returncode of cmd fails
            self._log.debug("wrapper RC={}".format(call_error.returncode))
            self._log.error("Failed first try on pduusb port {}, action={} command through wrapper, "
                            "trying again in 5 seconds {}".format(port, action, call_error))
            time.sleep(5.0)
            # kill process
            proc.kill()
            proc = subprocess.Popen(cmd, stderr=subprocess.STDOUT)
            self._log.info("retry pid={}".format(str(proc.pid)))
            cmd_output = proc.communicate(timeout=15)[0]
            if cmd_output is None:
                proc.kill()
                self._log.info("Failed to run pdu command->")
                return False
        except subprocess.TimeoutExpired as cmd_timeout_err:
            self._log.error("Timeout occurred {}".format(cmd_timeout_err))
            self._log.error("killing pdu process {}".format(proc.pid))
            proc.kill()
            # try getting data again
            cmd_output = proc.communicate(timeout=15)[0]
            self._log.info("cmd output=->{}".format(str(cmd_output)))
            if cmd_output[0] is None:
                self._log.error("Failed to get cmd data - running pdu cmd again")
                self._log.info("Retrying pdu cmd after timeout->" + str(cmd))
                proc = subprocess.Popen(cmd, stderr=subprocess.STDOUT)
                self._log.info("Retry pid after timeout={}".format(str(proc.pid)))
                cmd_output = proc.communicate(timeout=15)[0]
                if cmd_output is None:
                    proc.kill()
                    self._log.info("Failed to get response stdout from pdu command->")
                    return False
        finally:
            self._log.debug("cleanup: attempt to remove pdu process  {}".format(proc.pid))
            proc.kill()

        pdu_usb_result = None
        # sample cmd_result = b'\r\nNone\r\n' 'None' is always at the end of cmd try
        cmd_result = str(cmd_output).split("\\r")
        for i in range(len(cmd_result)):   # searching for None in cmd output
            if cmd_result[i].find("None") >= 0:
                pdu_usb_result = True
                break
            else:
                pdu_usb_result = False

        return pdu_usb_result

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def remove_power(self):
        """
        Call pduusb wrapper and connect AC power

        :return: True if cmd successful
        """
        return self.__call_wrapper(self.usb_pdu_port, "OFF")

    def connect_power(self):
        """
        Call pduusb wrapper and connect AC power

        :return: True if cmd successful
        """
        return self.__call_wrapper(self.usb_pdu_port, "ON")

    def ac_connected(self):
        # type: (None) -> bool
        """
        Get AC power Detection of SUT.
        :return:
            True    -    AC POWER Detected
            NONE     -   AC POWER NOT Detected

        :raise DriverIOError: if command execution failed in driver
        """
        ret=self.__call_wrapper(self.usb_pdu_port, "get_outlet_status")
        self._log.info(ret)
        return ret
