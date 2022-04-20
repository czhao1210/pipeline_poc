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
Socket Driver provide APIs to send/receive data
"""
import base64
import os
import socket
from abc import ABCMeta
from datetime import datetime

from six import add_metaclass
import re

@add_metaclass(ABCMeta)
class SocketComm(object):
    """
    Socket Communication for data transfer.
    """

    def __init__(self, ip, port, log=None, buffer_size=2048):
        self._ip_address = ip
        self._port = port
        self._log = log
        self.__socket_server = None
        self.buffer_size = buffer_size
        self.__pat = re.compile(r'Reply from')

    def close(self):
        """
        close serial port
        """
        if self.__socket_server is not None:
            self.__socket_server.close()
            self.__socket_server = None

    def close_session(self, conn):
        if conn:
            conn.close()

    def receive(self, conn, address, timeout=60):
        total_data = []
        time = 1
        while_time = datetime.now()
        while True:
            try:
                data = conn.recv(self.buffer_size).decode()
                if 0 < len(data) < self.buffer_size and not data.endswith('0505x0'):
                    if self.__ping(address):
                        if time == 1:
                            if self._log:
                                self._log.info(
                                    "this data package is not found 0505x0,Set to suspect data.Wait for the next check. ")
                            time += 1
                        if time != 1:
                            if self._log:
                                self._log.error('server receive data error: {}'.format(data))
                            time = 1
                            raise Exception('server socket packet error')
                    else:
                        raise Exception('network connection broken')
                elif 0 < len(data) <= self.buffer_size and data.endswith('0505x0'):
                    if time != 1:
                        total_data.append('')
                        time = 1
                    total_data.append(data[:data.rfind('0505x0')])
                    break
                elif data:
                    total_data.append(data)
                elif timeout != 0 and (datetime.now() - while_time).seconds > timeout:
                    break
            except socket.error as ex:
                if self._log:
                    self._log.error('[socket receive error:] {}'.format(ex))
                raise ex
            except socket.timeout as ex:
                if self._log:
                    self._log.error('[socket receive error:] {}'.format(ex))
                raise ex

        return ''.join(total_data).rstrip()

    def __ping(self, address, duration=300):
        cmd = r'ping -n 1 {}'.format(address[0])
        start = datetime.now()
        while (datetime.now() - start).seconds < duration:
            output = os.popen(cmd).readlines()
            self._log.info('[output]=> '.format(output))
            if self.__pat.search(''.join(output)):
                self._log.info('[Matched] network ping through')
                return True
        else:
            self._log.error('network counldn\'t ping through')
            return False

    def send(self, conn, data, timeout=60):
        """
        Send out data via socket
        :param data: data to send
        :param timeout:
        :return: (data size sent, connection object)
        """
        send_length = 0
        while data:
            try:
                if len(data) > self.buffer_size:
                    length = conn.send(data[:self.buffer_size].encode("utf-8"))
                    send_length += length
                    data = data[self.buffer_size:]
                elif 0 < len(data) <= 1024:
                    length = conn.send((data + '0505x0').encode("utf-8"))
                    send_length += length
                    data = ''
                elif 1024 < len(data) <= self.buffer_size:
                    conn.send(data.ljust(self.buffer_size).encode("utf-8"))
                    conn.send('0505x0'.encode("utf-8"))
                    send_length = len(data) + 6
                    data = ''
            except socket.error as ex:
                raise ex
            except socket.timeout as ex:
                raise ex
        return send_length - 6
