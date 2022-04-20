#!/usr/bin/env python
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
COM Driver wrapper
"""
import time

import serial

from dtaf_core.drivers.internal.base_serial import SingletonSerialThread
from dtaf_core.lib.exceptions import DriverIOError
from dtaf_core.lib.private.drivercfg_factory import DriverCfgFactory


class ComDriver(SingletonSerialThread):
    """
    COM serial driver thread for COM/ttys* serial device. Each COM port will have only one instance,
    but different COM ports will have its own instance.
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
        return super(ComDriver, cls).__new__(cls, *args, **kwargs)

    def __init__(self, cfg_opts, log):
        """
        Initialize COM serial thread, if specified port is already initialized, just ignore it.

        :param cfg_opts: xml.etree.ElementTree.Element of configuration options for execution environment
        :param log: Logger object to use for output messages
        """
        self._log = log
        self.__proc = None
        try:
            self._single_lock.acquire()
            if self.__dict__.get('_addressed') is None:
                log.info('Serial driver is raw, in processing...')
                super(ComDriver, self).__init__(cfg_opts, log)
                log.info('Initialization process is done')
            else:
                log.info('This port is already addressed')

            log.info('port    : {}'.format(self._driver_cfg_model.port))
            log.info('baudrate: {}'.format(self._driver_cfg_model.baudrate))
            log.info('timeout : {}'.format(self._driver_cfg_model.timeout))
        finally:
            self._single_lock.release()

    def __cleanup(self):
        import psutil
        if self.__proc:
            self.__proc.kill()
            self.__proc = None
        for proc in psutil.process_iter():
            try:
                if proc.name().find("putty") != -1:
                    proc.kill()
            except psutil.PermissionError as perm_error:
                self._log.error("{}".format(perm_error))
            except Exception as ex:
                self._log.error("unexpected exception: {}".format(ex))


    def __start_logging(self, logfile):
        import subprocess
        import os
        self.__cleanup()
        if os.path.exists(self._temp_log):
            os.remove(self._temp_log)
        __cmd = "{} -serial -sessionlog {} -sercfg \"{},8,n,1,N\" {}".format(
            self._driver_cfg_model.delegate_app,
            logfile,
            self._driver_cfg_model.baudrate,
            self._driver_cfg_model.port
        )
        self.__proc = subprocess.Popen(__cmd, shell=True)

    def _new_resource(self):
        """
        Initialize COM port resource, and assign it to self._serial.

        :return: None
        """
        _init = _now = time.time()
        import subprocess
        while self._driver_cfg_model.timeout > _now - _init:
            self._serial_lock.acquire()
            try:
                if not self._driver_cfg_model.delegate_app:
                    self._serial = serial.Serial(port=self._driver_cfg_model.port,
                                                 baudrate=self._driver_cfg_model.baudrate,
                                                 timeout=5,
                                                 write_timeout=5)
                else:
                    self._serial = None
                    import os
                    import datetime
                    __timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    self._temp_log = os.path.join(self._driver_cfg_model.delegate_temp,
                                                  "putty_temp%s.log" % __timestamp)
                    if not os.path.exists(self._driver_cfg_model.delegate_temp):
                        os.makedirs(self._driver_cfg_model.delegate_temp)
                    self.__start_logging(self._temp_log)
                self._closed = False
                break
            except subprocess.CalledProcessError:
                self._log.info('wait for putty ready...')
                time.sleep(0.5)
                _now = time.time()
                continue
            except serial.SerialException:
                self._log.info('Wait for SERIAL PORT ready...')
                time.sleep(0.5)
                _now = time.time()
                continue
            finally:
                self._serial_lock.release()

    def _release_resource(self):
        """
        Close COM port and release related resource.

        :return: None
        """
        self._serial_lock.acquire()
        self._stopped = True
        self.__dict__['_addressed'] = None
        self._closed = True

        try:
            if self._driver_cfg_model.delegate_type == "putty":
                self.__cleanup()
            if self._serial:
                self._serial.close()
                self._serial = None
            if self._driver_cfg_model.delegate_type == "putty":
                import os
                for i in range(0, 3):
                    if os.path.exists(self._temp_log):
                        try:
                            os.remove(self._temp_log)
                        except Exception as ex:
                            self._log.debug("Failed to remove file({}):{}".format(self._temp_log, ex))
                            import time
                            time.sleep(3)
        finally:
            self._serial_lock.release()

    def run(self):
        # type: () -> None
        """
        Running serial thread to read data into buffer.

        :return: None
        """
        import os
        while not self._stopped:
            try:
                self._serial_lock.acquire()
                if self._serial:
                    length = 0
                    if self._driver_cfg_model.delegate_type == "putty":
                        length = 10240
                    else:
                        length = int(self._serial.in_waiting)
                    if not length > 0:
                        continue
                    data = self._serial.read(length)
                    if len(data) <= 0:
                        continue
                    try:
                        if isinstance(data, bytes):
                            self._push_to_all_buffer(data.decode())
                        else:
                            self._push_to_all_buffer(data)
                    except Exception as ex:
                        self._log.debug(ex)
                        try:
                            self._push_to_all_buffer("{}".format(data))
                        except Exception as e:
                            self._log.debug(e)
                else:
                    import os
                    if self._driver_cfg_model.delegate_type == "putty" and os.path.exists(self._temp_log):
                        if os.path.exists(self._temp_log):
                            self._serial = open(self._temp_log)
                    time.sleep(0.1)
            finally:
                self._serial_lock.release()

    def write(self, data):
        # type: (str) -> int
        """
        Write data bytes to COM port.

        :param data: Data string
        :raise DriverIOError: If fail to write data to serial
        :return: Data length
        """
        if not self._closed and self._serial:
            for cell in data:
                if self._driver_cfg_model.delegate_type == "putty":
                    raise NotImplementedError
                else:
                    self._serial.write(cell.encode())
                print(cell)
            return len(data)
        else:
            raise DriverIOError('No serial instance to write data')