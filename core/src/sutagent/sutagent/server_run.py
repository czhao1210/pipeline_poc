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

import base64
import collections
import configparser as config_parser
import json
import socket
import subprocess
import threading
from datetime import datetime
from subprocess import PIPE
from threading import Thread

from sutagent.lib.private.socket_comm import SocketComm


class SocketCommServer(SocketComm):
    """SocketComm Server"""

    def create_server(self, timeout=60, max_num=1):
        """Create server"""
        self.__socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket_server.bind((self._ip_address, self._port))
        if timeout:
            self.__socket_server.settimeout(timeout)
        self.__socket_server.listen(max_num)

    def accept(self, timeout=0):
        """Accept connect"""
        start_time = datetime.now()
        conn, address = self.__socket_server.accept()
        current_time = datetime.now()
        elapsed_time = (current_time - start_time).seconds
        remainder_time = timeout - elapsed_time
        if timeout:
            conn.settimeout(remainder_time)
        return conn, address


class ExecuteTask(Thread):
    def __init__(self, comm, conn, cmd):
        self.__comm = comm
        self.__conn = conn
        self.__cmd = cmd
        super().__init__()
        self.setDaemon(True)

    def run(self):
        try:
            ret = subprocess.Popen(self.__cmd, stdin=PIPE,
                                   stdout=PIPE,
                                   stderr=PIPE,
                                   shell=True)
            retrun_pid = str(ret.pid)
            self.__comm.send(self.__conn, base_encode(retrun_pid))
        finally:
            self.__comm.close_session(self.__conn)
        return_dict = {}
        return_dict['stdout'] = ret.stdout.read().decode()
        return_dict['stderr'] = ret.stderr.read().decode()
        return_dict['return_code'] = ret.poll()
        res = json.dumps(return_dict)

        try:
            mutex.acquire()
            result_dict[retrun_pid] = res
            if len(result_dict.keys()) > 20:
                result_dict.pop(list(result_dict.keys())[0])
        finally:
            mutex.release()


class SendTask(Thread):
    def __init__(self, comm, conn, data):
        self.__comm = comm
        self.__conn = conn
        self.__data = data
        super().__init__()
        self.setDaemon(True)

    def run(self):
        try:
            self.__comm.send(self.__conn, base_encode(self.__data))
        finally:
            self.__comm.close_session(self.__conn)


config = config_parser.ConfigParser()
config.read('lib/configuration/SUT_config.cfg')
port = config.get('SSHlib', 'port')

IP_PORT = ('127.0.0.1', int(port))


def base_encode(data):
    """return encrypted data"""
    data = data.encode()
    res = base64.b64encode(data)
    return res.decode()


def base_decode(data):
    """return decrypted data"""
    data = base64.b64decode(data)
    res = data.decode()
    return res


class _Log(object):
    @classmethod
    def debug(cls, msg):
        print(msg)

    @classmethod
    def info(cls, msg):
        print(msg)

    @classmethod
    def warning(cls, msg):
        print(msg)

    @classmethod
    def error(cls, msg):
        print(msg)

    @classmethod
    def critical(cls, msg):
        print(msg)

    warn = warning
    fatal = critical

    @classmethod
    def exception(cls, msg):
        print(msg)


log = _Log()

comm = SocketCommServer(ip='127.0.0.1', port=8010, log=log)
comm.create_server(timeout=0, max_num=10)

result_dict = collections.OrderedDict()

mutex = threading.Lock()

while True:
    print("waiting for connection...")
    conn, addr = comm.accept()
    print("...connected from:", addr)

    data = base_decode(comm.receive(conn=conn, address=addr))
    func_key = data.split(' ', 1)[0]
    cmd = data.split(' ', 1)[1]

    if func_key == 'execute':
        ExecuteTask(comm=comm, conn=conn, cmd=cmd).start()
    elif func_key == 'status':
        data = '1' if result_dict.get(cmd) else '0'
        SendTask(comm=comm, conn=conn, data=data).start()
    elif func_key == 'result':
        if result_dict.get(cmd):
            try:
                mutex.acquire()
                data = result_dict.pop(cmd)
            finally:
                mutex.release()
        else:
            data = '0'
        SendTask(comm=comm, conn=conn, data=data).start()
