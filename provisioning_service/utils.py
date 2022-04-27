import datetime
import re
import socket
import time
from typing import Optional, Callable, Any, Iterable, Mapping

import requests
import paramiko
import threading
import queue

class Pool(object):
    tasks = list()

class ProvisioningTask(threading.Thread):

    def __init__(self, hostname, port, username, password, ww):
        super().__init__()
        self._ww = ww
        self._hostname = hostname
        self._port = port
        self._username = username
        self._password = password
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # type: paramiko.SSHClient
        print(f"connect {self._hostname}:{self._port}")
        self._client.connect(hostname=self._hostname,
                        port=self._port,
                        username=self._username,
                        password=self._password,
                        timeout=10)
        self._ssh = self._client.get_transport().open_session()
        self._ssh.settimeout(timeout=10)
        self._ssh.get_pty()
        self._ssh.invoke_shell()
        self._container_ip = ""
        self.__stop = False
        self.start()

    @property
    def container_ip(self):
        return self._container_ip

    @property
    def is_stopped(self):
        return self.__stop

    def run(self):
        self.parse_prompt(30)
        container_name = self.parse_container_name(timeout=360)
        self._container_ip = self.parse_container_ip_address(container_name)
        _start = datetime.datetime.now()
        while not self.__stop and (datetime.datetime.now() - _start).seconds < 3600:
            try:
                self._ssh.recv(102400)
            except socket.timeout as e:
                time.sleep(1)
        self._ssh.close()
        self._client.close()
        self.__stop = True


    def parse_prompt(self, timeout):
        _start = datetime.datetime.now()
        no_data_count = 0
        while no_data_count < 10 and (datetime.datetime.now() - _start).seconds < timeout:
            try:
                ret = self._ssh.recv(102400).decode()
                no_data_count = 0
                print(ret)
                m = re.search("([a-z]+\d+)>", ret)
                if m:
                    self._prompt = m.groups()[0]
            except socket.timeout as e:
                no_data_count += 1
                time.sleep(1)

    def parse_container_name(self, timeout):
        _start = datetime.datetime.now()
        no_data_count = 0
        self._ssh.send(f"simlauncher run gnr-6.0 {self._ww} --cores 8 --memory 32\r")
        print("execute simlauncher")
        data = ""
        host_name = ""
        while not host_name and (datetime.datetime.now() - _start).seconds < timeout:
            try:
                data += self._ssh.recv(102400).decode()
                m = re.findall("([a-z]+\d+)>", data)
                for n in m:
                    if n != self._prompt:
                        host_name = f"{n}.zsc2.intel.com"
            except socket.timeout as e:
                time.sleep(1)
        return host_name

    def _execute(self, ssh, command, timeout):
        ssh.send(f"{command}\r")
        no_data_count = 0
        _start = datetime.datetime.now()
        data = ""
        while no_data_count < 10 and (datetime.datetime.now() - _start).seconds < timeout:
            try:
                data += ssh.recv(102400).decode()
                no_data_count = 0
            except socket.timeout as e:
                no_data_count += 1
                time.sleep(1)

        print(f"execute {command} return={data}")
        return data

    def parse_container_ip_address(self, container_name):
        _client = paramiko.SSHClient()
        _client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # type: paramiko.SSHClient
        print(f"connect container: {container_name}:{self._port}")
        _client.connect(hostname=container_name,
                        port=self._port,
                        username=self._username,
                        password=self._password,
                        timeout=10)
        _ssh = _client.get_transport().open_session()
        _ssh.settimeout(timeout=10)
        _ssh.get_pty()
        _ssh.invoke_shell()
        no_data_count = 0
        _start = datetime.datetime.now()
        while no_data_count < 10 and (datetime.datetime.now() - _start).seconds < 60:
            try:
                _ssh.recv(102400)
                no_data_count = 0
            except socket.timeout as e:
                no_data_count += 1
                time.sleep(1)
        #ret = self._execute(self._ssh, f"ssh {container_name}", 60)
        ret = self._execute(self._ssh, "ip address", 60)
        m = re.findall("inet\s+(\d+\.\d+\.\d+\.\d+)", ret)
        container_ip = ""
        if m:
            print(ret)
            for a in m:
                if r"127.0.0.1" != a:
                    container_ip = a
        _ssh.close()
        _client.close()
        return container_ip


    def stop(self):
        self.__stop = True
        self.join()


class SshSession(object):
    def __init__(self, hostname, port, username, password):
        self._client = paramiko.SSHClient
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # type: paramiko.SSHClient
        print(f"connect {hostname}:{port}")
        self._client.connect(hostname=hostname,
                        port=port,
                        username=username,
                        password=password,
                        timeout=10)
        self._ssh = self._client.get_transport().open_session()
        self._ssh.settimeout(timeout=10)
        self._ssh.get_pty()
        self._ssh.invoke_shell()

# t = ProvisioningTask(hostname=r"simcloud0.intel.com",
#                      port="22", username=r"czhao", password=r"80198789*m*", ww=r"2022ww15.5")
# command = ""
# while not t.container_ip:
#     time.sleep(5)
# while command != r"exit()":
#     print(f"container ip={t.container_ip}")
#     command = input(r"<type exit() to close")
#     time.sleep(3)
# print(t.container_ip)
# t.stop()