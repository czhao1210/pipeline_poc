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

import socket
import time
import paramiko
from dtaf_core.drivers.base_driver import BaseDriver
from dtaf_core.drivers.internal.console.ssh_console import SshConsole
from dtaf_core.lib.private.drivercfg_factory import DriverCfgFactory
from dtaf_core.lib.exceptions import DriverIOError


class SolDriver(BaseDriver):
    """
    SOL serial driver based on BMC SOL SSH service. Before using this driver, please make sure
    that SOL and SOL ssh is enabled in BMC. This driver will connect to BMC SOL ssh service and
    invoke a shell object, read from or send to data through ssh channel. Each pair <addr, port>
    will have only one instance, but different pairs will have its own instance.
    """

    @property
    def SshChannel(self):
        channel = self.__ssh_console.get_channel(self.__buffer_name)
        return channel

    def read_from(self, buffer_name):
        return self.__ssh_console.get_channel(buffer_name=self.__buffer_name).read_from(buffer_name=buffer_name)

    def write(self, data):
        return self.__ssh_console.get_channel(buffer_name=self.__buffer_name).write(data=data)

    def register(self, buffer_name, buffer_size=4 * 1024 * 1024):
        self.__buffer_name = buffer_name
        if self.__ssh_console:
            self.__ssh_console.register(self.__buffer_name)

    def unregister(self, buffer_name):
        self.__buffer_name = buffer_name
        if self.__ssh_console:
            self.__ssh_console.unregister(self.__buffer_name)

    def stop(self):
        if self.__ssh_console_started and self.__ssh_console:
            self.__ssh_console.stop()
            self.__ssh_console_started = False
            self.unregister(f"{self._driver_cfg_model.user}"
                            f"@{self._driver_cfg_model.address}"
                            f":{self._driver_cfg_model.port}")

    def __start_ssh_console(self):
        if not self.__ssh_console_started and self.__ssh_console:
            self.register(f"{self._driver_cfg_model.user}"
                          f"@{self._driver_cfg_model.address}"
                          f":{self._driver_cfg_model.port}")
            self.__ssh_console.start()
            self.__ssh_console_started = True

    def start(self):
        self.__start_ssh_console()

    def __init__(self, cfg_opts, log):
        super().__init__(cfg_opts, log)
        self.__ssh_console = SshConsole(host=self._driver_cfg_model.address,
                                        port=self._driver_cfg_model.port,
                                        user=self._driver_cfg_model.user,
                                        password=self._driver_cfg_model.password)
        self.__ssh_console_started = False

    def __enter__(self):
        self.start()
        return super(SolDriver, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        super(SolDriver, self).__exit__(exc_type, exc_val, exc_tb)
