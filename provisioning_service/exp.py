import time
from typing import Optional, Callable, Any, Iterable, Mapping

import paramiko
import datetime
import socket
import threading
import subprocess

# __hostname = r"ub2-cm-test07.sh.intel.com"
# __port = 22
# __username = r"tester"
# __password = r"intel@123"

__hostname = r"simcloud0.intel.com"
__port = 22
__username = r"czhao"
__password = r"80198789*m*"

_client = paramiko.SSHClient()
_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # type: paramiko.SSHClient
print(f"connect {__hostname}:{__port}")
_client.connect(hostname=__hostname,
                port=__port,
                username=__username,
                password=__password,
                timeout=10)
_ssh = _client.get_transport().open_session()
_ssh.settimeout(timeout=10)
_ssh.get_pty()
_ssh.invoke_shell()
# _proc = subprocess.Popen(r"ssh simcloud.intel.com", shell=True,
#                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
__command = ""

# import paramiko
# ssh=paramiko.SSHClient()
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# ssh.connect(hostname,username=username,password=password)
# stdin,stdout,stderr = ssh.exec_command(command)
# for line in iter(lambda: stdout.readline(2048), ""):
#     print(line)
import re

_prompt = ""
class Printout(threading.Thread):
    container = ""
    def __init__(self, group: None = ..., target: Optional[Callable[..., Any]] = ..., name: Optional[str] = ...,
                 args: Iterable[Any] = ..., kwargs: Mapping[str, Any] = ..., *, daemon: Optional[bool] = ...) -> None:
        super().__init__()
        self._start = True
        self.start()

    def run(self):
        __start = datetime.datetime.now()
        while (datetime.datetime.now()-__start).seconds < 30:
            try:
                ret = _ssh.recv(102400).decode()
                print(ret)
                m = re.search("([a-z]+\d+)>", ret)
                if m:
                    _prompt = m.groups()[0]
                    print(f"prompt={_prompt}")
                    print(f"ret={ret}")
            except socket.timeout as e:
                time.sleep(0.5)
        _ssh.send("simlauncher run gnr-6.0 2022ww15.5 --cores 8 --memory 32\r")
        while self._start:
            try:
                ret = _ssh.recv(102400).decode()
                print(ret)
                m = re.findall("([a-z]+\d+)>", ret)
                for n in m:
                    print(f"n={n},m={m},_prompt={_prompt}")
                    if n != _prompt and not Printout.container:
                        Printout.container = f"{n}.zsc2.intel.com"
                        print(f"set container={Printout.container}")
            except socket.timeout as e:
                time.sleep(0.5)


p = Printout()
_client0 = paramiko.SSHClient()
_client0.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # type: paramiko.SSHClient
print(f"connect {__hostname}:{__port}")
_client0.connect(hostname=__hostname,
                port=__port,
                username=__username,
                password=__password,
                timeout=10)
_ssh0 = _client0.get_transport().open_session()
_ssh0.settimeout(timeout=10)
_ssh0.get_pty()
_ssh0.invoke_shell()
try:
    for i in range(0, 10):
        print(_ssh0.recv(102400).decode())
except socket.timeout as e:
    pass
while not Printout.container:
    print(f"container={Printout.container}")
    time.sleep(3)
__command = f"ssh {Printout.container}"

while __command != r"exit()":
    # __command = input("<input your commad>")
    if __command != r"exit()":
        _ssh0.send(f"{__command}\r")
        __start = datetime.datetime.now()
        data = ""
        while (datetime.datetime.now() - __start).seconds < 10:
            try:
                ret = _ssh0.recv(102400).decode()
                data += ret
            except socket.timeout as e:
                pass
        import re
        m = re.findall("inet\s+(\d+\.\d+\.\d+\.\d+)", data)
        if m:
            print(data)
            for a in m:
                if r"127.0.0.1" != a:
                    print(a)
                    __command=r"exit()"
        else:
            __command = "ip address"
            print(data)
        time.sleep(5)
p._start = False
p.join()
