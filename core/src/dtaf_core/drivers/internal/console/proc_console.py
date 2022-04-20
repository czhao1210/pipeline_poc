import subprocess

from dtaf_core.drivers.internal.console.console import Shared, Console
import time
import datetime


@Shared(key=("host", "port"))
class ProcConsole(Console):
    def connect(self, **kwargs):
        pass

    def disconnect(self):
        pass

    def launch_console(self, cmd):
        if not self._client:
            self._client = subprocess.Popen(cmd, shell=True,
                                            stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT
                                            )

    def shutdown_console(self):
        if self._client:
            import psutil
            psutil.Process(self._client.pid).kill()
            self._client = None

    def wait_for_completion(self, timeout, time_block=10):
        self.flag = False
        __start = datetime.datetime.now()
        __absolute_start = datetime.datetime.now()
        if self._client:
            while (datetime.datetime.now() - __absolute_start).seconds < timeout and (
                    datetime.datetime.now() - __start).seconds < time_block:
                if self.flag:
                    __start = datetime.datetime.now()
                else:
                    time.sleep(2)
            if (datetime.datetime.now() - __start).seconds >= time_block:
                return True
            else:
                raise RuntimeError('proc_console run timeout')

    def read_from_console(self, timeout=5):
        __start = datetime.datetime.now()
        data = ""
        while not data and (datetime.datetime.now() - __start).seconds < timeout:
            self.flag = False
            ret = self._client.stdout.readline() if self._client else None
            if ret:
                self.flag = True
                data = ret.decode()
        return data

    def write_to_console(self, data):
        self._client.stdin.write(data) if self._client else None
        self._client.stdin.flush() if self._client else None
