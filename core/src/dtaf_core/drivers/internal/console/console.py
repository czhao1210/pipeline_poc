from abc import abstractmethod
from base64 import b64encode
from threading import Lock
from queue import Queue
import queue
from typing import Optional
import time
from threading import Thread
import re
import datetime

from dtaf_core.lib.singleton import Shared


@Shared(key=("console_name"))
class _ConsoleChannels(object):
    def __init__(self, console_name):
        self._console_name = console_name
        self._pool = dict()
        self._lock = Lock()

    def get(self, channel_name):
        with self._lock:
            if channel_name in self._pool.keys():
                if not self._pool[channel_name].empty():
                    return self._pool[channel_name].get_nowait()
                return None
        return None

    def put(self, channel_name, data):
        with self._lock:
            if channel_name in self._pool.keys():
                if self._pool[channel_name].full():
                    self._pool[channel_name].get_nowait()
                self._pool[channel_name].put_nowait(data)

    def add(self, channel_name, maxsize=1024 * 1024):
        with self._lock:
            if channel_name not in self._pool.keys():
                self._pool[channel_name] = Queue(maxsize=maxsize)

    def remove(self, channel_name):
        with self._lock:
            if channel_name in self._pool.keys():
                self._pool.pop(channel_name)

    def removeall(self):
        with self._lock:
            self._pool.clear()

    def clear(self, channel_name):
        with self._lock:
            if channel_name in self._pool.keys():
                maxsize = self._pool[channel_name].maxsize
                self._pool[channel_name] = Queue(maxsize)

    def put_to_all(self, data):
        with self._lock:
            for c in self._pool.values():
                if c.full():
                    c.get_nowait()
                c.put_nowait(data)


class Console(object):

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self._kwargs = kwargs
        for key, value in kwargs.items():
            setattr(self, f'_{key}', value)
        self._console_name = ":".join([self._host, str(self._port)])
        self._console_name_write = "{}_write".format(self._console_name)
        self._channel_name_write = "runtime_writing"

        if not hasattr(self, "_ref"):
            self._ref = 0
        else:
            raise Exception("re enter init")
        self._lock = Lock()
        self._is_running = False
        self._read_thrd = None
        self._write_thrd = None

    def is_running(self):
        return self._is_running

    def register(self, channel_name):
        _ConsoleChannels(console_name=self._console_name).add(channel_name)

    def unregister(self, channel_name):
        _ConsoleChannels(console_name=self._console_name).remove(channel_name)

    def read(self, channel_name):
        ret = _ConsoleChannels(console_name=self._console_name).get(channel_name)
        return ret

    def clear(self, channel_name):
        return _ConsoleChannels(console_name=self._console_name).clear(channel_name)

    def write(self, data):
        return _ConsoleChannels(console_name=self._console_name_write).put(self._channel_name_write, data)

    def start(self):
        with self._lock:
            if self._ref == 0:
                try:
                    self.connect(**self._kwargs)
                except Exception as ex:
                    pass
                self._is_running = True
                self._read_thrd = Thread(target=self._read_proc, daemon=True)
                self._read_thrd.start()
                _ConsoleChannels(console_name=self._console_name_write).add(self._channel_name_write)
                self._write_thrd = Thread(target=self._write_proc, daemon=True)
                self._write_thrd.start()
            self._ref += 1

    def stop(self):
        print("ref={},_is_running={}".format(self._ref, self._is_running))
        with self._lock:
            if self._ref == 1 and self._is_running:
                self._is_running = False
                self._read_thrd.join(timeout=60)
                self._write_thrd.join(timeout=60)
                self._read_thrd = None
                self._write_thrd = None
                _ConsoleChannels(console_name=self._console_name).removeall()
                _ConsoleChannels(console_name=self._console_name_write).removeall()
                try:
                    self.disconnect()
                except Exception as ex:
                    print("unexpected stop exceptoin={}".format(ex))
            self._ref -= 1

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return True

    @abstractmethod
    def connect(self, host, port, username="", password=""):
        raise NotImplementedError

    @abstractmethod
    def disconnect(self):
        raise NotImplementedError

    @abstractmethod
    def read_from_console(self, timeout=5):
        raise NotImplementedError

    @abstractmethod
    def write_to_console(self, data):
        raise NotImplementedError

    def _read_proc(self):
        _connection_closed = False
        while self._is_running:
            data = None
            try:
                if _connection_closed:
                    self.connect(**self._kwargs)
                    _connection_closed = False
                data = self.read_from_console(timeout=5)
                if data:
                    print(data)
                    _ConsoleChannels(console_name=self._console_name).put_to_all(data)
                else:
                    time.sleep(0.1)
            except TimeoutError as err:
                data = None
                _connection_closed = True
                time.sleep(3)
            except EOFError as eof_err:
                print("read_proc={}".format(eof_err))
                _connection_closed = True
                time.sleep(3)
            except ConnectionError as con_refused:
                print("read_proc={}".format(con_refused))
                _connection_closed = True
                time.sleep(3)
            except Exception as ex:
                _connection_closed = True
                print("unexpected read_proc exception ={}".format(ex))
                time.sleep(3)

    def _write_proc(self):
        _connection_closed = False
        while self._is_running:
            try:
                data = _ConsoleChannels(console_name=self._console_name_write).get(self._channel_name_write)
                if data:
                    if _connection_closed:
                        self.connect(**self._kwargs)
                        _connection_closed = False
                    self.write_to_console(data)
                else:
                    time.sleep(0.1)
            except TimeoutError as err:
                _connection_closed = True
                time.sleep(3)
            except EOFError as eof_err:
                print("write_proc={}".format(eof_err))
                _connection_closed = True
                time.sleep(3)
            except Exception as ex:
                _connection_closed = True
                print("unexpected write_proc exception ={}".format(ex))
                time.sleep(3)

    def get_channel(self, buffer_name):
        return Channel(self, buffer_name)


class Channel(object):
    def __init__(self, service: Console, buffer_name):
        self.__service = service
        self.__buffer_name = buffer_name

    def clean_buffer(self, buffer_name=None):
        if buffer_name is None:
            self.__service.clear(channel_name=self.__buffer_name)
        else:
            self.__service.clear(channel_name=buffer_name)

    def write(self, data):
        return self.__service.write(data=data)

    def read_from(self, buffer_name=None):
        ret = ""
        if buffer_name is None:
            ret = self.__service.read(channel_name=self.__buffer_name)
        else:
            ret = self.__service.read(channel_name=buffer_name)
        if not ret:
            time.sleep(0.1)
        if ret and ret.find(r"Press [F2") != -1:
            print("F2 detected in read from timestamp={}".format(datetime.datetime.now().timestamp()))
        return ret

    def execute_until(self, cmd, until_pat, timeout):
        self.clean_buffer()
        self.write(cmd)
        pat = re.compile(until_pat)
        __start = datetime.datetime.now()
        data = ""
        while (datetime.datetime.now() - __start).seconds < timeout:
            d = self.read_from()
            if d:
                data += d
                if re.search(until_pat, data):
                    return data
        if re.search(until_pat, data):
            return data
        return None
