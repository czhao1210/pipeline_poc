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
This is an example of RSC2 implemented AC Power Control Provider
"""

import sys
import time
from threading import Thread
from xml.etree import ElementTree as eTree

import serial

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.console_log import ConsoleLogProvider
from dtaf_core.providers.provider_factory import ProviderFactory


class LogReading(Thread):
    def __init__(self, console):
        super(LogReading, self).__init__()
        self.__console = console  # type: ConsoleLogProvider
        self.__stop = False
        self.buffer = list()

    def join(self, timeout=None):
        self.__stop = True
        super(LogReading, self).join(timeout)

    def run(self):
        while not self.__stop:
            data = self.__console.read()
            if data:
                self.buffer.append(data.strip())
            else:
                time.sleep(0.3)


class SerialReading(Thread):
    def __init__(self):
        super(SerialReading, self).__init__()
        self.__stop = False
        self.buffer = list()

    def join(self, timeout=None):
        self.__stop = True
        super(SerialReading, self).join(timeout)

    def run(self):
        with serial.Serial("com2", 9600, timeout=0.5) as ser:
            data = ""
            while not self.__stop:
                c = ser.read(1).decode()
                if c == "\n":
                    self.buffer.append(data)
                    data = ""
                elif c:
                    data += c


class SutOsSystemTest(BaseTestCase):
    """
    Basic test case demonstrating the use of FlashProvider.

    Add the IFWI file you want to use to the working directory as IFWI.bin.
    This example test assumes 32MB flash and
    that the SUT is already powered-on and booted to the OS.
    This is designed to be triggered manually,
    and as such, is not marked as a system test for py test to pick up.
    """

    def __init__(self, test_log, arguments, cfg_opts):
        super(SutOsSystemTest, self).__init__(test_log, arguments, cfg_opts)

        tree = eTree.ElementTree()
        if sys.platform == 'win32':
            tree.parse(r'..\data\consolelog_configuration.xml')
        else:
            tree.parse('/opt/Automation/consolelog_configuration.xml')
        root = tree.getroot()
        sut = ConfigurationHelper.get_sut_config(root)
        # console_cfg = ConfigurationHelper.get_provider_config(sut=sut, provider_name=r"console_log")
        console_cfgs = ConfigurationHelper.filter_provider_config(sut=sut,
                                                                  provider_name=r"console_log")
        console_cfg = console_cfgs[0]
        self.__console_log1 = ProviderFactory.create(console_cfg, test_log)  # type: ConsoleLogProvider
        ########################
        console_cfgs = ConfigurationHelper.filter_provider_config(sut=sut,
                                                                  provider_name=r"console_log",
                                                                  attrib=dict(id="2"))
        console_cfg = console_cfgs[0]
        self.__console_log2 = ProviderFactory.create(console_cfg, test_log)  # type: ConsoleLogProvider
        pass

    def verify_console_log_read(self):
        """
        This is the function to verify console log Read/Write APIs
        :return: None
        """
        self.__console_log1.read()
        self.__console_log1.write()
        self.__console_log2.read()
        console_reading = LogReading(self.__console_log)
        console_reading.start()
        with serial.Serial("com2", 9600, timeout=0.5) as ser:
            for i in range(0, 20):
                ser.write("test console log rw APIs {}\n".format(i).encode())
                time.sleep(1)
        console_reading.join()
        log_buffer = list()
        with open(r"logs\example_console_log_console.log") as f:
            data = f.readline()
            while data:
                log_buffer.append(data.strip())
                data = f.readline()
        print("log_buffer:{}".format(log_buffer))
        for i in range(0, len(log_buffer)):
            assert log_buffer[i] == console_reading.buffer[i]


    def verify_console_log_write(self):
        """
        This is the function to verify console log Write APIs
        :return: None
        """
        read = SerialReading()
        read.start()
        time.sleep(1)
        for i in range(0, 20):
            msg = "test:{}\n".format(i)
            self.__console_log.write(msg)
        time.sleep(3)
        read.join()
        assert read.buffer
        for j in range(0, len(read.buffer)):
            assert read.buffer[j] == "test:{}".format(j)

    def execute(self):
        """
        The entry of Test Case.
        :return:
        """
        self.verify_console_log_write()
        return True


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if SutOsSystemTest.main() else Framework.TEST_RESULT_FAIL)
