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
Base Serial
"""
import threading
from abc import abstractmethod

from dtaf_core.drivers.base_driver import BaseDriver
from dtaf_core.lib.exceptions import IncorrectKeyException


class Buffer(object):
    """
    Buffer object that used for maintaining the serial data.
    """

    def __init__(self, name, max_size, log=None):
        """
        Initialize a buffer object.

        :param name: Buffer name
        :param max_size: Buffer size, take it in bytes
        :param log: Logger object to use for output messages
        """
        self._name = name
        self._data = ''
        self._max_size = max_size
        self._log = log

    def pull(self):
        # type: () -> str
        """Return buffer data"""
        return self._data

    def clean(self):
        # type: () -> None
        """Clean buffer data"""
        self._data = ''

    def push(self, data):
        # type: (str) -> None
        """
        Push data into buffer, will drop left data if data size is larger than buffer size.

        :param data: Any sequence that can be converted into string
        :return: None
        """
        data = str(data) if data else ''
        length = len(data) + len(self._data)
        if length <= self._max_size:
            self._data += data
        else:
            full = self._data + data
            self._data = full[0:self._max_size]
            # self._log.warning('Serial buffer overflow: <{}>, '
            #                   'overflowed data: {}'.format(self._name, full[self._max_size:]))


class SerialBufferSet(object):
    """
    Serial data buffer set, provide individual buffer for the layer communicate
    with serial driver module. One buffer also can be shared by upper layer with
    the buffer name, it depends on layer's requirement to the buffer.
    """

    def __init__(self, log):
        """
        Initialize a buffer set object.

        :param log: Logger object to use for output messages
        """
        self._buf_set = {}
        self._log = log

    def new_buffer(self, name, max_size):
        # type: (str, int) -> Buffer
        """
        Create a named buffer in buffer set, if the named buffer already exists,
        just return it.

        :param name: Buffer name
        :param max_size: Buffer size, take it in bytes
        :return: Named buffer object
        """
        if name in self._buf_set.keys():
            # return self._buf_set[name]
            self._buf_set.pop(name)

        buffer = Buffer(name, max_size, self._log)
        self._buf_set[name] = buffer
        return buffer

    def get_buffer_data(self, name):
        # type: (str) -> str
        """
        Return data in named buffer.

        :param name: Buffer name
        :raise IncorrectKeyException: If the named buffer doesn't exist
        :return: Data in named buffer
        """
        if name not in self._buf_set.keys():
            raise IncorrectKeyException('No such buffer: {}'.format(name))

        buffer = self._buf_set[name]
        return buffer.pull()

    def clean_buffer(self, name):
        # type: (str) -> None
        """
        Clean data in named buffer.

        :param name: Buffer name
        :raise IncorrectKeyException: If the named buffer doesn't exist
        :return: None
        """
        if name not in self._buf_set.keys():
            raise IncorrectKeyException('No such buffer: {}'.format(name))

        buffer = self._buf_set[name]
        buffer.clean()

    def push_to_buffer(self, name, data):
        # type: (str, str) -> None
        """
        Push data to a existing named buffer.

        :param name: Buffer name
        :param data: Data string
        :raise IncorrectKeyException: If the named buffer doesn't exist
        :return: None
        """
        if name not in self._buf_set.keys():
            raise IncorrectKeyException('No such buffer: {}'.format(name))

        buffer = self._buf_set[name]
        buffer.push(data)

    def buffers_name(self):
        # type:() -> KeysView
        """
        Return all buffer names.

        :return: A set-like object
        """
        return self._buf_set.keys()


class SingletonSerialThread(threading.Thread, BaseDriver):
    """
    A wrapper class for serial hardware driver, will only generate a singleton object
    for the same hardware resource.

    This class will maintain a buffer set for incoming serial data, it is identified
    by buffer name. using register function to register a new buffer for upper layer
    modules.
    """
    _single_lock = threading.Lock()
    _serialization = ''
    _vars = {}

    def __new__(cls, *args, **kwargs):
        if 'serialization' not in list(kwargs.keys()):
            raise RuntimeError('serialization is mandatory to a serial thread')
        serialization = kwargs.get('serialization')

        instance_key = cls._instance_key(serialization)
        if instance_key in cls._vars:
            return cls._vars[instance_key]
        try:
            cls._single_lock.acquire()
            cls._vars[instance_key] = super(SingletonSerialThread, cls).__new__(cls)
            cls._serialization = serialization
            return cls._vars[instance_key]
        finally:
            cls._single_lock.release()

    def __init__(self, cfg_opts, log):
        """
        Initialize a new SingletonSerialThread object.

        :param cfg_opts: xml.etree.ElementTree.Element of
        configuration options for execution environment
        :param log: Logger object to use for output messages

        """
        if self.__dict__.get('_addressed') is None:
            threading.Thread.__init__(self)
            BaseDriver.__init__(self, cfg_opts, log)

            self._stopped = False
            self._closed = False
            self._serial_lock = threading.Lock()
            self._serial = None
            self._log = log
            if not hasattr(self, "_buf_set"):
                self._buf_set = SerialBufferSet(self._log)
            self._addressed = True
            self._serialization = self._serialization
            self._new_resource()
            self._start()

    def __enter__(self):
        return super(SingletonSerialThread, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(SingletonSerialThread, self).__exit__(exc_type, exc_val, exc_tb)
        if self._stopped:
            self._release()

    @classmethod
    def _serialize(cls, serialization):
        """
        Return a digital serialized string based on the input.

        :param serialization: The string want to be serialized
        :return: Digital number string
        """
        serialized = ''
        for ele in serialization.lower():
            serialized += str(ord(ele))
        return serialized

    @classmethod
    def _instance_key(cls, serialization):
        """
        Return a flag string that used for describing the object.

        :param serialization: String object
        :return: String object
        """
        return '{}{}'.format(id(cls), cls._serialize(serialization))

    def _destroy(self):
        """
        Destroy singleton resource from cls._var.
        make sure before call this function, all source is released.

        :return: None
        """
        instance_key = self._instance_key(self._serialization)
        SingletonSerialThread._vars.pop(instance_key)

    @abstractmethod
    def _new_resource(self):
        """
        Initialize serial resource, and assign it to self._serial,
        it should be implemented by child class.

        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def _release_resource(self):
        """
        Release serial resource, it should be implemented by child class.

        :return: None
        """
        raise NotImplementedError

    def _push_to_all_buffer(self, data):
        """
        Push data to all buffers that saved in buffer set.

        :param data: Data string
        :return: None
        """
        for buffer_name in self._buf_set.buffers_name():
            self._buf_set.push_to_buffer(buffer_name, data)

    def clean_buffer(self, buffer_name):
        """
        Clear Buffer
        :param buffer_name:
        :return:
        """
        with self._serial_lock:
            self._buf_set.clean_buffer(buffer_name)

    def _start(self):
        """
        Start serial thread instance if it isn't alive.

        :return: None
        """
        if not self.is_alive():
            self._log.info('Start serial driver thread...')
            self.setDaemon(True)
            super(SingletonSerialThread, self).start()
        else:
            self._log.info('Serial driver is already started')

    def _release(self):
        """
        Release hardware resource and stop related driver thread

        :return: None
        """
        if not self._stopped:
            self._log.info('Stopping serial driver...')
            self._stopped = True
            self.join()
            self._release_resource()
            self._destroy()
        else:
            self._log.info('{} is already stopped'.format(self.__class__.__name__))

    def register(self, buffer_name, buffer_size=4 * 1024 * 1024):
        # type: (str, int) -> None
        """
        Register a new buffer for upper layer module. By default, there is no default buffer created
        when new this SingletonSerialThread class. If upper layer wants to talk with serial driver,
        it must call this method before reading data from serial driver. One buffer can be used as
        a standalone buffer to upper layer, also can be a shared buffer between different upper
        layers by the buffer name.

        :param buffer_name: Buffer name
        :param buffer_size: Buffer size, take it in bytes
        :return: None
        """

        self._buf_set.new_buffer(name=buffer_name,
                                 max_size=buffer_size)

    def search_data(self, buffer_name):
        """
        Read all data from specified buffer.

        :param buffer_name: Buffer name
        :return: Buffer data
        """
        with self._serial_lock:
            data = self._buf_set.get_buffer_data(buffer_name)
        return data

    def read_from(self, buffer_name):
        # type: (str) -> str
        """
        Read all data from specified buffer, then erase existing data in this buffer.

        :param buffer_name: Buffer name
        :return: Buffer data
        """
        with self._serial_lock:
            data = self._buf_set.get_buffer_data(buffer_name)
            self._buf_set.clean_buffer(buffer_name)
        return data

    @abstractmethod
    def write(self, data):
        # type: (str) -> int
        """
        Write data to serial port, it should be implemented by child class.

        :param data: Data string
        :raise SerialException: If fail to write data to serial
        :return: Data length
        """
        raise NotImplementedError

    def close(self):
        # type: () -> None
        """
        Close and release serial hardware resource, here the driver thread will still keep alive.

        :return: None
        """
        self._release_resource()

    def reopen(self):
        # type: () -> None
        """
        Reopen driver resource while driver thread is alive.
        """
        if self._stopped:
            self._log.error('Serial thread is stopped, resource cannot be reopened')
            return

        if not self._closed:
            self._log.error('Serial driver is already opened')
            return

        self._new_resource()
