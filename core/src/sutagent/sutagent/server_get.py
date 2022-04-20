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

import argparse
import configparser as config_parser

from sutagent.lib.private.socket_comm import SocketComm
import socket
import base64


class SocketCommClient(SocketComm):
    """SocketComm Client"""

    def client_connection(self):
        addr = (self._ip_address, self._port)
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(addr)
        return conn, self._ip_address


PARSER = argparse.ArgumentParser(description='Parse Parameters')
PARSER.add_argument('--execute', type=str, default=None)
PARSER.add_argument('--status', type=str, default=None)
PARSER.add_argument('--result', type=str, default=None)
PARSER.add_argument('--getport', type=str, default=None)

ARGS = PARSER.parse_args()
execute = ARGS.execute
status = ARGS.status
result = ARGS.result
getport = ARGS.getport
no_recive = False

config = config_parser.ConfigParser()
config.read('lib/configuration/SUT_config.cfg')
port = int(config.get('SSHlib', 'port'))

if getport:
    no_recive = True
    print(port)


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

socket_obj = SocketCommClient(ip='127.0.0.1', port=port, log=log)
conn, addr = socket_obj.client_connection()

if not no_recive:
    try:
        content = ''
        if execute:
            socket_obj.send(conn=conn, data=base_encode('execute ' + execute))
        elif status:
            socket_obj.send(conn=conn, data=base_encode('status ' + status))
        elif result:
            socket_obj.send(conn=conn, data=base_encode('result ' + result))

        ret = base_decode(socket_obj.receive(conn=conn, address=addr))

        print("get_result:\n=======\n%s\n=======" % ret)
    finally:
        socket_obj.close_session(conn=conn)
