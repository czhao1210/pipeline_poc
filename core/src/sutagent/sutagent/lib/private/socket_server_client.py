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
This module defines send/receive APIs for socket communication
"""
import errno
import os
import re
import socket
import time
from datetime import datetime
from sutagent import BUFFER_SIZE, IP_ADDRESS, IP_PORT
from sutagent.lib.private.serial_transport import sparklogger

RESPONSE_PATTERN = re.compile(r'Reply from')


class PacketError(Exception):
    pass


class SocketError(Exception):
    pass


def __socket_connect():
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            socket_client.connect((IP_ADDRESS, IP_PORT))
            sparklogger.info("connect to server socket successfully")
            return socket_client
        except socket.error:
            sparklogger.warning("try to connect to server socket every 5s")
            time.sleep(5)


def __ping(address, duration=300):
    cmd = r'ping -n 1 {}'.format(address[0])
    start = datetime.now()
    while (datetime.now() - start).seconds < duration:
        output = os.popen(cmd).readlines()
        sparklogger.info('[output]=> '.format(output))
        if RESPONSE_PATTERN.search(''.join(output)):
            sparklogger.info('[Matched] network ping through')
            return True
    else:
        sparklogger.error('network counldn\'t ping through')
        return False


def sut_eth_message_send(data):
    """
    send data to host
    :param data:
    :return:send data length

    :exception: PacketError,SocketError,TimeoutError
    :dependence
    :black box equivalent class
                    send data >1030 ,0 < send data <1024,1024 < send data <=1030 0505x0 in send data,0505x0 endswith send data
                    no endtoken with 0505x0,space in 1024 ->1030
    """
    socket_client = __socket_connect()
    sparklogger.info('will send data:{}'.format(data))
    send_length = 0
    try:
        while data:
            try:
                if len(data) > BUFFER_SIZE:
                    length = socket_client.send(data[:BUFFER_SIZE].encode("utf-8"))
                    send_length += length
                    data = data[BUFFER_SIZE:]
                elif 0 < len(data) <= 1024:
                    length = socket_client.send((data + '0505x0').encode("utf-8"))
                    send_length += length
                    data = ''
                elif 1024 < len(data) <= BUFFER_SIZE:
                    socket_client.send(data.ljust(BUFFER_SIZE))
                    socket_client.send(b'0505x0')
                    send_length = len(data) + 6
                    data = ''
            except socket.error as ex:
                sparklogger.error('[client socket send error:] {}'.format(ex))
                raise SocketError('client socket send data error')
            except socket.timeout as ex:
                sparklogger.error('[client socket send error:] {}'.format(ex))
                raise SocketError('client socket send data error')
        return send_length - 6
    finally:
        sparklogger.info('close client socket')
        if socket_client:
            sparklogger.info('client socket closed')
            socket_client.close()


def sut_eth_message_receive(timeout):
    """
    receive a data from host constantly
    :param timeout:
    :return: data receive from host

    :exception: PacketError,SocketError
    :dependence
    :black box equivalent class
                    receive data >1030 ,0 < receive data <= 1030,0505x0 in receive data,0505x0 endswith receive data
                    no endtoken with 0505x0,space in 1024 ->1030
    """

    socket_client = __socket_connect()
    total_data = []
    try:
        start = datetime.now()
        while True:
            try:
                if (datetime.now() - start).seconds > timeout >= 0:
                    raise SocketError('client socket receive data timeout')
                data = socket_client.recv(BUFFER_SIZE).decode()
                if 0 < len(data) < BUFFER_SIZE and not data.endswith('0505x0'):
                    raise PacketError('client socket packet error')
                elif 0 < len(data) <= BUFFER_SIZE and data.endswith('0505x0'):
                    total_data.append(data[:data.rfind('0505x0')])
                    break
                elif data:
                    total_data.append(data)
            except socket.error as ex:
                if ex.errno != errno.ECONNRESET:
                    sparklogger.error('[client socket receive error:] {}'.format(ex))
                    raise SocketError('client socket receive data error')
            except socket.timeout as ex:
                if ex.errno != errno.ECONNRESET:
                    sparklogger.error('[client socket receive error:] {}'.format(ex))
                    raise SocketError('client socket receive data error')
        return ''.join(total_data).rstrip()
    finally:
        sparklogger.info('close client socket')
        if socket_client:
            sparklogger.info('client socket closed')
            socket_client.close()
