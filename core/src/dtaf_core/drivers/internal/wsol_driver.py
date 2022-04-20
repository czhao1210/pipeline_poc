#!/usr/bin/env python
"""
#################################################################################
# INTEL CONFIDENTIAL
# Copyright Intel Corporation All Rights Reserved.
#
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material may contain trade secrets and proprietarygit
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
import asyncio
import base64
import errno
import ssl
import time

import serial
import websockets

from dtaf_core.drivers.internal.base_serial import SingletonSerialThread
from dtaf_core.lib.private.drivercfg_factory import DriverCfgFactory


class WebSocketConnection:
    """
    WebSocketConnection
    """

    def __init__(self, uri, user, pw, log):
        self.uri = uri
        self.user = user
        self.pw = pw
        self._log = log
        self.websocket = None
        return

    async def __ws_recv(self, websocket):
        try:
            message = await websocket.recv()
            return message
        except websockets.exceptions.ConnectionClosedOK:
            self._log.error("BMC Closed Connection\r")

    async def __ws_send(self, websocket, data):
        try:
            message = await websocket.send(data)
            return message
        except websockets.exceptions.ConnectionClosedOK:
            self._log.error("BMC Closed Connection\r")

    async def __ws_connect(self, uri, user, pw):
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        b64userpw = base64.b64encode(f"{user}:{pw}".encode()).decode('ascii')
        headers = {
            "Authorization": f"Basic {b64userpw}"
        }
        wscon = websockets.connect(uri, ssl=ssl_context, extra_headers=headers)
        websocket = None
        try:
            websocket = await asyncio.wait_for(wscon, timeout=3)
        except websockets.exceptions.InvalidStatusCode as error:
            if error.status_code == 401:
                self._log.error("Connection Error:  Username/Password Authentication Failed\r")
            elif error.status_code == 409:
                self._log.error("Connection Error: BMC serial console interface is in used\r")
            else:
                self._log.error(f"Connection Error: {error}\r")
        except asyncio.TimeoutError:
            self._log.error("Connection Timed Out\r")
        except ConnectionResetError:
            self._log.error("Connection Reset (likely an authentication error)\r")
        except OSError as error:
            if error.errno == errno.ECONNREFUSED:
                self._log.error("Connection Failed\r")
            elif error.errno == errno.ETIMEDOUT:
                self._log.error("Connection Socket Timed Out\r")
            elif error.errno == 1:
                self._log.error("Connection Protocol Error\r")
            elif error.errno is None:
                self._log.error("Connection Mystery Error. {error}\r")
            else:
                self._log.error(f"Connection Error: OS error {error} ({error.errno})\r")
        return websocket

    async def main(self):
        """
        connect websocket
        :return:
        """
        self.websocket = await self.__ws_connect(self.uri, self.user, self.pw)

    async def recv(self):
        """
        receive message
        :return:
        """
        ws_rcv_task = asyncio.ensure_future(self.__ws_recv(self.websocket))
        res = await ws_rcv_task
        return res

    async def send(self, data):
        """
        send message
        :param data:data you will send
        :return:
        """
        ws_rcv_task = asyncio.ensure_future(self.__ws_send(self.websocket, data))
        res = await ws_rcv_task
        return res

    async def close(self):
        """
        close websocket
        :return:
        """
        self.websocket = None


class WsolDriver(SingletonSerialThread):
    """
    WsolDriver
    """

    def __new__(cls, *args, **kwargs):
        if len(args) == 2:
            cfg_opts = args[0]
            log = args[1]
        elif len(kwargs) == 2:
            cfg_opts = kwargs['cfg_opts']
            log = kwargs['log']
        else:
            cfg_opts = args[0]
            log = kwargs['log']

        cfg_model = DriverCfgFactory.create(cfg_opts=cfg_opts, log=log)
        port = cfg_model.port
        kwargs['serialization'] = port
        return super(WsolDriver, cls).__new__(cls, *args, **kwargs)

    def __init__(self, cfg_opts, log):
        self.wsobj_send = None
        self.wsobj_recv = None
        self._log = log
        try:
            self._single_lock.acquire()
            if self.__dict__.get('_addressed') is None:
                log.info('Wsol driver is raw, in processing...')
                super(WsolDriver, self).__init__(cfg_opts, log)
                log.info('Initialization process is done')
            else:
                log.info('This port is already addressed')
            log.info('port    : {}'.format(self._driver_cfg_model.port))
            log.info('timeout : {}'.format(self._driver_cfg_model.timeout))
        finally:
            self._single_lock.release()

    def _new_resource(self):
        _init = _now = time.time()
        while self._driver_cfg_model.timeout > _now - _init:
            self._serial_lock.acquire()
            try:
                self.addr = 'wss://%s/%s' % (self._driver_cfg_model.ip, self._driver_cfg_model.port)
                self.loop_send = asyncio.get_event_loop()
                self._closed = False
                break
            except serial.SerialException:
                self._log.info('Wait for SERIAL PORT ready...')
                time.sleep(0.5)
                _now = time.time()
                continue
            finally:
                self._serial_lock.release()

    def _release_resource(self):
        self._serial_lock.acquire()
        try:
            if self.wsobj_send:
                self.loop_send.run_until_complete(self.wsobj_send.close())
                self.wsobj_send = None

            if self.wsobj_recv:
                self.loop_recv.run_until_complete(self.wsobj_recv.close())
                self.wsobj_recv = None

            self.loop_send = None
            self.loop_recv = None

            self._closed = True
            self._stopped = True
        finally:
            self._serial_lock.release()

    def run(self):
        """
        The threading to receive message
        :return: None
        """
        self.loop_recv = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop_recv)
        self.wsobj_recv = WebSocketConnection(uri=self.addr, user=self._driver_cfg_model.user,
                                              pw=self._driver_cfg_model.password, log=self._log)
        self.wsobj_send = WebSocketConnection(uri=self.addr, user=self._driver_cfg_model.user,
                                              pw=self._driver_cfg_model.password, log=self._log)
        while not self._stopped:
            try:
                if not self.wsobj_recv.websocket:
                    self._log.debug('func run:retry connect recv obj')
                    self.loop_recv.run_until_complete(self.wsobj_recv.main())
                    if not self.wsobj_recv.websocket:
                        self.loop_send.run_until_complete(self.wsobj_send.close())
                    continue

                if not self.wsobj_send.websocket:
                    self._log.debug('func run:retry connect send obj')
                    self.loop_send.run_until_complete(self.wsobj_send.main())
                    if not self.wsobj_send.websocket:
                        self.loop_recv.run_until_complete(self.wsobj_recv.close())
                    continue

                try:
                    data = self.loop_recv.run_until_complete(self.wsobj_recv.recv())
                except websockets.exceptions.ConnectionClosedError as ex:
                    self._log.error(ex)
                    if self.wsobj_recv.websocket:
                        self._log.error('recv error:will close wsobj_recv')
                        self.loop_recv.run_until_complete(self.wsobj_recv.close())
                    if self.wsobj_send.websocket:
                        self._log.error('recv error:will close wsobj_send')
                        self.loop_send.run_until_complete(self.wsobj_send.close())
                    continue
                try:
                    self._push_to_all_buffer(data.decode())
                except Exception as ex:
                    self._log.debug(ex)
            except AttributeError as ex:
                self._log.error(ex)
                self.wsobj_recv = WebSocketConnection(self.addr, self._driver_cfg_model.user,
                                                      self._driver_cfg_model.password, self._log)
                self.wsobj_send = WebSocketConnection(self.addr, self._driver_cfg_model.user,
                                                      self._driver_cfg_model.password, self._log)

    def write(self, data):
        """
        send message to BMC websocket over lan
        :param data: data you will send
        :return: length of data or None
        """
        if self.wsobj_send and not self._closed:
            if self.wsobj_send.websocket:
                try:
                    self.loop_send.run_until_complete(self.wsobj_send.send(data))
                except websockets.exceptions.ConnectionClosedError as e:
                    self._log.info("%s %s" % (e, type(e)))
                    self.loop_send.run_until_complete(self.wsobj_send.close())
                    self.loop_send.run_until_complete(self.wsobj_send.main())
                    self.loop_send.run_until_complete(self.wsobj_send.send(data))
                return len(data)
