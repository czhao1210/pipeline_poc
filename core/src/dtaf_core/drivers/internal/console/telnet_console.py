from dtaf_core.drivers.internal.console.console import Shared, Console
from telnetlib import Telnet
import time
import datetime

@Shared(key=("host", "port"))
class TelnetConsole(Console):
    def connect(self, **kwargs):
        self._telent = Telnet()
        try:
            print("connect to {}:{}".format(self._host, self._port))
            self._telent.open(self._host, self._port)
        except OSError as e:
            self._telent = None
            raise e

    def disconnect(self):
        if self._telent:
            self._telent.close()
            self._telent = None

    def read_from_console(self, timeout=5):
        ret = self._telent.read_until(b"\n", timeout=timeout).decode()
        return ret

    def write_to_console(self, data):
        if self._telent:
            return self._telent.write(data.encode())