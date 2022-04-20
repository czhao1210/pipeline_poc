import socket

from dtaf_core.drivers.internal.console.console import Shared, Console
from telnetlib import Telnet
import paramiko
import time
import datetime


@Shared(key=("host", "port"))
class SshConsole(Console):
    def connect(self, **kwargs):
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # type: paramiko.SSHClient
        print("connect {}:{}".format(kwargs['host'], kwargs['port']))
        self._client.connect(hostname=kwargs['host'],
                             port=kwargs['port'],
                             username=kwargs['user'],
                             password=kwargs['password'],
                             timeout=10)
        self._ssh = self._client.get_transport().open_session()
        self._ssh.settimeout(timeout=10)
        self._ssh.get_pty()
        self._ssh.invoke_shell()

    def disconnect(self):
        if self._ssh:
            self._ssh.close()
            self._ssh = None
        if self._client:
            self._client.close()
            self._client = None

    def read_from_console(self, timeout=5):
        __start = datetime.datetime.now()
        data = ""
        while not data and (datetime.datetime.now() - __start).seconds < timeout:
            try:
                ret = self._ssh.recv(1024 * 100)
            except socket.timeout as e:
                ret = None
            if ret:
                data = ret.decode()
                if data.find(r"Press [F2") != -1:
                    self._ssh.send('\33' + '7' + "\r\n")
                    self._ssh.send('\33' + '2')
                    print(
                        "F2 detected in read from ssh console timestamp={}".format(datetime.datetime.now().timestamp()))
            else:
                time.sleep(0.1)
        return data

    def write_to_console(self, data):
        return self._ssh.send(data)
