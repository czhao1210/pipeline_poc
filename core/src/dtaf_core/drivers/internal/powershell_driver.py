"""
#################################################################################
# INTEL CONFIDENTIAL
# Copyright Intel Corporation All Rights Reserved.
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material may contain trade secrets and proprietary
# and confidential information of Intel Corporation and its suppliers and
# licensors, and is protected by worldwide copyright and trade secret laws and
# treaty provisions. No part of the Material may be used, copied, reproduced,
# modified, published, uploaded, posted, transmitted, distributed, or disclosed
# in any way without Intel's prior express written permission.
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
#################################################################################
"""

import json
import requests

from dtaf_core.drivers.base_driver import BaseDriver
from dtaf_core.lib.exceptions import DriverIOError
import queue
import subprocess
import threading
import re

class PowershellCommand(threading.Thread):
    def __init__(self, command, timeout, hostname, username, password):
        self._host = hostname
        self._username = username
        self._password = password
        self._command = command
        self._timeout = timeout
        self._return_value = ""
        self._is_running = True
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.start()

    def run(self):
        try:
            self._return_value = self.__remote_execute(self._command, self._timeout)
        except subprocess.CalledProcessError as error:
            self._return_value = error
        self._is_running = False

    def __remote_execute(self, cmd, timeout):
        commandlines = ["powershell", "-c"]
        command = """
        $Username = "%s"
        $Password = "%s"
        $pass = ConvertTo-SecureString -AsPlainText $Password -Force
        $Cred = New-Object System.Management.Automation.PSCredential -ArgumentList $Username,$pass
        Invoke-Command -ComputerName %s -ScriptBlock {%s} -credential $Cred
        """ % (self._username,
               self._password,
               self._host, cmd)
        commandlines.append(command)
        p = subprocess.Popen(commandlines, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        lines = list()
        while p.poll() is None:
            ln = p.stdout.readline().decode()
            if ln:
                lines.append(ln)
        ln = p.stdout.readline().decode()
        if ln:
            lines.append(ln)
        return "\r\n".join(lines)

    @property
    def result(self):
        if isinstance(self._return_value, Exception):
            raise self._return_value
        return self._return_value

    @property
    def is_running(self):
        return self._is_running


class PowershellDriver(BaseDriver):
    def __init__(self, cfg_opts, log):
        super(PowershellDriver, self).__init__(cfg_opts, log)
        self.__queue=queue.Queue(maxsize=10)

    def __enter__(self):
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)

    def remote_execute(self, cmd, timeout):
        thrd = PowershellCommand(command=cmd, timeout=timeout,
                                 hostname=self._driver_cfg_model.host,
                                 username=self._driver_cfg_model.username,
                                 password=self._driver_cfg_model.password)
        thrd.join(timeout)
        return thrd.result

    def remote_execute_async(self, cmd):
        thrd = PowershellCommand(command=cmd, timeout=None,
                                 hostname=self._driver_cfg_model.host,
                                 username=self._driver_cfg_model.username,
                                 password=self._driver_cfg_model.password)
        qsize = self.__queue.qsize()
        for i in range(0, qsize):
            d = self.__queue.get()
            if not d.is_running():
                d.join()
            else:
                self.__queue.put(d)
        self.__queue.put(thrd)

    def local_execute(self, cmd):
        commandlines = ["powershell", "-c", cmd]
        try:
            return subprocess.check_output(commandlines).decode()
        except subprocess.CalledProcessError as error:
            raise DriverIOError(error)

    def copy_local_to_remote(self, src_file, dest_file):
        command = """
            Invoke-Command -ScriptBlock {
            $mySession = new-PSSession -ComputerName %s
            Copy-Item -Path %s -Destination %s -ToSession $mySession 
            }
        """ % (self._driver_cfg_model.host, src_file, dest_file)
        commandlines = ["powershell", "-c"]
        commandlines.append(command)
        return subprocess.check_output(commandlines).decode()

    def copy_remote_to_local(self, src_file, dest_file):
        # get hostname
        commandlines = ["powershell", "-c", "systeminfo"]
        ret = subprocess.check_output(commandlines).decode()
        m = re.search(r"Host Name:\s+(\S+)\s+[\s\S]+Domain:\s+(\S+)", ret)
        if m:
            hostname = ".".join(m.groups())
            print(hostname)
            # remote copy
            command = """
                Invoke-Command -ScriptBlock {
                $mySession = new-PSSession -ComputerName %s
                Copy-Item -Path %s -Destination %s -ToSession $mySession 
                }
            """ % (hostname, src_file, dest_file)
            cmd = PowershellCommand(command=command, timeout=None,
                                 hostname=self._driver_cfg_model.host,
                                 username=self._driver_cfg_model.username,
                                 password=self._driver_cfg_model.password)
            cmd.join()
            return cmd.result
        else:
            raise DriverIOError("Cannot get systeminfo")


