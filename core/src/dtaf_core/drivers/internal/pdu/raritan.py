#!/usr/bin/env python
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
import re
import time
from threading import Thread

class Raritan(object):
    invoke_cmd = "show pdu\n"
    invoke_symbols = ["#", ">"]
    invoke_re = 'PDU [\s\S]*Model'

    def __init__(self, ip, port, username, password, invoke_timeout):
        super(Raritan, self).__init__()
        self.__ip = ip
        self.__port = port
        self.__username = username
        self.__password = password
        self.__invoke_timeout = invoke_timeout

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __read_until(self, ssh, pat, timeout):
        data = ""
        for i in range(0, timeout):
            if ssh.recv_ready():
                data += ssh.recv(1024 * 10).decode()
                if re.search(pat, data):
                    return data
            else:
                time.sleep(1)
        return ""

    def execute(self, cmd, timeout):
        import paramiko
        with paramiko.SSHClient() as client:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # type: paramiko.SSHClient
            client.connect(hostname=self.__ip, port=self.__port,
                           username=self.__username, password=self.__password, timeout=10)
            with client.get_transport().open_session() as ssh:
                ssh.get_pty()
                ssh.invoke_shell()
                data = ""
                login=False
                from datetime import datetime
                __start = datetime.now()
                ret_count = 0
                ret = ""
                while not login and (datetime.now() - __start).seconds < timeout and (ret_count==0 or ret):
                    ret = self.__read_until(ssh=ssh, pat="\n", timeout=3)
                    ret_count = (ret_count+1) if len(ret)>0 else ret_count
                if self.__invoke_timeout is not None and self.__invoke_timeout > 0:
                    time.sleep(self.__invoke_timeout)
                for i in range(0, 3):
                    if ssh.send_ready():
                        ssh.send(cmd + "\n")
                        if timeout:
                            for j in range(0, timeout):
                                data += self.__read_until(ssh=ssh, pat="\n", timeout=1)
                        else:
                            data += self.__read_until(ssh=ssh, pat="\n")
                        return data
                    else:
                        time.sleep(1)
                return ""


class RaritanCommand(Thread):
    def __init__(self, onegroup, cmdline, timeout):
        super().__init__()
        self._onegroup = onegroup
        self.__cmdline = cmdline
        self._return_data = None
        self.__timeout = timeout
        self.setDaemon(True)
        self.start()

    def run(self):
        result = ""
        with Raritan(self._onegroup.ip, self._onegroup.port,
                     self._onegroup.username, self._onegroup.password,
                     self._onegroup.invoke_timeout) as r:
            self._return_data = r.execute(self.__cmdline, self.__timeout)
            print("return_data={}".format(self._return_data))

    def wait_result(self):
        if self.__timeout:
            for i in range(0, self.__timeout):
                if self._return_data:
                    self.join()
                    return self._return_data
                time.sleep(1)
        else:
            while self._return_data is None:
                time.sleep(1)
        self.join()
        return self._return_data


class RaritanPoweron(RaritanCommand):
    def __init__(self, onegroup, timeout):
        cmd_on = "".join(["power outlets {} on /y \n".format(i) for i in onegroup.outlets])
        super().__init__(onegroup, cmd_on, timeout)


class RaritanPoweroff(RaritanCommand):
    def __init__(self, onegroup, timeout):
        cmd_off = "".join(["power outlets {} off /y \n".format(i) for i in onegroup.outlets])
        super().__init__(onegroup, cmd_off, timeout)


class RaritanPowerstate(RaritanCommand):
    def __init__(self, onegroup, timeout):
        cmd_state = "".join(["show outlets {}\n".format(i) for i in onegroup.outlets])
        super().__init__(onegroup, cmd_state, timeout)

    def wait_result(self):
        data = super().wait_result()
        if data:
            return_pat = "Outlet\s+(\d+)\W*[^:]*?:[^\r\n]*[\r\n]+Power\s+state:\s+(\w+)"
            return re.findall(return_pat, data)
        else:
            return data

