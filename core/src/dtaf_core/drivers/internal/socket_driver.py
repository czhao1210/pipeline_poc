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
import re
import socket
from abc import ABCMeta
from datetime import datetime

from six import add_metaclass

from dtaf_core.lib.private.socket_comm import SocketComm

from dtaf_core.drivers.base_driver import BaseDriver
from dtaf_core.lib.exceptions import DriverIOError


class SocketComm_Server(SocketComm):
    def create_server(self):
        self.__socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket_server.bind((self._ip_address, self._port))

    def accept(self, timeout=60, max_num=1):
        start_time = datetime.now()
        if timeout:
            self.__socket_server.settimeout(timeout)
        self.__socket_server.listen(max_num)
        conn, address = self.__socket_server.accept()
        current_time = datetime.now()
        elapsed_time = (current_time - start_time).seconds
        remainder_time = timeout - elapsed_time
        conn.settimeout(remainder_time)
        return conn, address


@add_metaclass(ABCMeta)
class SocketDriver(BaseDriver):
    """
    Socket Driver for data transfer.
    """

    def __enter__(self):
        """
        Enter resource context for this driver.

        :return: Resource to use (usually self)
        """
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit resource context for this driver.

        :param exc_type: Exception type
        :param exc_val: Exception value
        :param exc_tb: Exception traceback
        :return: None
        """
        self.close()

    def __init__(self, cfg_opts, log):
        """
        Create a new driver object.

        :param cfg_opts: Dictionary of configuration options provided by the ConfigFileParser.
        :param log: logging.Logger object to use to store debug output from this Provider.
        """
        BaseDriver.__init__(self, cfg_opts, log)
        self._cfg = cfg_opts
        self.__pat = re.compile(r'Reply from')
        self.__socket_server = SocketComm_Server(ip=self._driver_cfg_model.ip_address, port=self._driver_cfg_model.port,
                                                 log=log, buffer_size=self._driver_cfg_model.buffer_size)
        self.open()

    def open(self):
        try:
            self.__socket_server.create_server()
        except socket.error as ex:
            self._log.error('[socket accept error:] {}'.format(ex))
            raise DriverIOError('socket accept fail')
        except socket.timeout as ex:
            self._log.error('[socket accept error:] {}'.format(ex))
            raise DriverIOError('socket accept fail')

    def close(self):
        """
        close serial port
        """
        if self.__socket_server is not None:
            self.__socket_server.close()

    def receive(self, timeout=60):
        conn, addr = self.__socket_server.accept(timeout=timeout, max_num=1)
        try:
            ret = self.__socket_server.receive(conn=conn, address=addr, timeout=timeout)
        finally:
            self._log.info("close a connection")
            if conn:
                self.__socket_server.close_session(conn=conn)
        return ret

    def send(self, data, timeout=60):
        conn, addr = self.__socket_server.accept(timeout=timeout, max_num=1)
        try:
            ret = self.__socket_server.send(conn=conn, data=data, timeout=timeout)
        finally:
            self._log.info("close a connection")
            if conn:
                self.__socket_server.close_session(conn=conn)
        return ret
