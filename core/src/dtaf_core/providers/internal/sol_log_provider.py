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
import datetime
import os
import re
import sys
import threading
import time
from shutil import copyfile

from dtaf_core.lib.configuration import ConfigurationHelper

from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.drivers.internal.sol_driver import SolDriver
from dtaf_core.lib.exceptions import IncorrectKeyException, InvalidParameterError

from dtaf_core.providers.log import LogProvider


class SolLogProvider(LogProvider):
    """
    Base Class that record all output data into log file.
    """

    def __init__(self, cfg_opts, log):
        """
        Create a new ConsoleLogProvider object.

        :param cfg_opts: xml.etree.ElementTree.Element of configuration options for execution environment
        :param log: Logger object to use for output messages
        """
        super(SolLogProvider, self).__init__(cfg_opts, log)
        self.buffer_name = 'console_buffer'
        self.runtime_buffer = None
        self.keyword_buffer = None
        self.runtime_lock = threading.Lock()
        self.buffer_size = 4 * 1024 * 1024
        self.lock = threading.Lock()
        self.repo = ""
        self.drv_opts = ConfigurationHelper.get_driver_config(provider=cfg_opts, driver_name='sol')
        self.runwith_framework = self._config_model.runwith_framework
        self.logpath_local = self._config_model.logpath_local
        self.logpath_default = os.path.join(os.path.dirname(sys.argv[0]).replace('/', os.sep), 'local_logs')

        if not self.runwith_framework:
            self.log_path = self.logpath_default if not self.logpath_local else self.logpath_local
        elif self.runwith_framework.lower() == "caf":
            self.caf_path = os.getenv('CAF_CASE_LOG_PATH')
            if self.caf_path:
                self.log_path = self.caf_path
            elif self.logpath_local:
                self.log_path = self.logpath_local
            else:
                self.log_path = self.logpath_default
        else:
            raise InvalidParameterError('Unsupported running framework: {}'.format(self.runwith_framework))

        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)

        self.log_name = os.path.splitext(os.path.basename(sys.argv[0]))[0] + '_console.log'
        self.log_file = os.path.join(self.log_path, self.log_name)
        self.console_log = open(self.log_file, 'a+')

        self.serial = DriverFactory.create(self.drv_opts, log) # type: SolDriver
        self.serial.register(self.buffer_name, self.buffer_size)
        log.info("register buffer={}".format(self.buffer_name))
        self._start_logging = True
        self.log_thread = threading.Thread(target=self._log_thread)
        self.log_thread.setDaemon(True)
        self.log_thread.start()



    def __enter__(self):
        return super(SolLogProvider, self).__enter__()

    def close(self):
        super().close()
        try:
            self._start_logging = False
            self.log_thread.join(timeout=30)
            self.lock.acquire()
            if self.console_log:
                self.console_log.close()
            if self.repo:
                for handler in self._log.root.handlers:
                    dest_file = os.path.join(self.repo, os.path.basename(handler.baseFilename))
                    copyfile(handler.baseFilename, dest_file)
                copyfile(self.log_file, os.path.join(self.repo, self.log_name))
        except Exception as ex:
            print(ex)
        finally:
            self.lock.release()
            self.serial.stop()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        super(SolLogProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def inject_line(self, line):
        # type: (str) -> None
        """
        Insert a separate line into serial log file.

        :param line: data line, any sequence that can be converted into string
        :return: None
        """
        line = str(line) if line else ''
        self.lock.acquire()
        try:
            self.console_log.write('\n' + line + '\n')
            self.console_log.flush()
        finally:
            self.lock.release()

    def _log_thread(self):
        while self._start_logging:
            self.lock.acquire()
            try:
                data = self.serial.SshChannel.read_from(self.buffer_name)
                if not data:
                    # sleep(): release GIL so that it can be used for other threads
                    time.sleep(0)
                    continue
                else:
                    self.console_log.write(data)
                    self.console_log.flush()
            except IncorrectKeyException as ex:
                time.sleep(0.1) # sleep to wait for com driver to register buffer
            except ValueError as e:
                time.sleep(0.1)
            finally:
                self.lock.release()

    def read(self):
        """
        read data from console
        :return: data buffer received from console
        """
        try:
            self.runtime_lock.acquire()
            if self.runtime_buffer is None:
                self.runtime_buffer = r"runtime_buffer"
                self.serial.register(self.runtime_buffer, self.buffer_size)
        finally:
            self.runtime_lock.release()
        return self.serial.SshChannel.read_from(self.runtime_buffer)

    def write(self, buf):
        """
        write data to console
        """
        try:
            self.runtime_lock.acquire()
            if self.runtime_buffer is None:
                self.runtime_buffer = r"runtime_buffer"
                self.serial.register(self.runtime_buffer, self.buffer_size)
        finally:
            self.runtime_lock.release()
        return self.serial.SshChannel.write(buf) == len(buf)

    def make_repo(self, path):
        self.repo = path
        if path and not os.path.exists(self.repo):
            os.makedirs(self.repo)

    def redirect(self, log_file):
        try:
            self.log_file = log_file
            self.lock.acquire()
            self.runtime_lock.acquire()
            if self.console_log:
                self.console_log.close()
            self.console_log = open(self.log_file, 'a+')
        finally:
            self.runtime_lock.release()
            self.lock.release()

    def wait_for_keyword(self, pattern, timeout):
        # type:(str,int)->None
        """
        The API will create a new buffer to save data from console. It will return if the specified pattern detected or timeout

        :param pattern:
        :param timeout:
        :return: True/False
        :raise DriverIOError: if fail to read data
        """
        try:
            self.runtime_lock.acquire()
            if self.keyword_buffer is None:
                self.keyword_buffer = r"keyword_buffer"
                self.serial.register(self.keyword_buffer, self.buffer_size)
        finally:
            self.runtime_lock.release()

        self.serial.clean_buffer(self.keyword_buffer)
        start_time = datetime.now()
        data = ''
        while (datetime.now() - start_time).seconds < timeout:
            content = self.serial.SshChannel.read_from(self.keyword_buffer)
            data += content
            if re.search(pattern, data):
                return True
        return False

    def search_for_keyword(self, pattern, timeout):
        # type:(str,int)->None
        """
        The API will search the data in console for the keyword. It will return if the specified pattern detected or timeout

        :param pattern:
        :param timeout:
        :return: True/False
        :raise DriverIOError:if fail to read data
        """
        raise NotImplementedError("search for keyword hasn't been implemented in SOL")

