#!/usr/bin/env python
#################################################################################
# INTEL CONFIDENTIAL
# Copyright Intel Corporation All Rights Reserved.
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material may contain trade secrets and proprietary
# and confidential information of Intel Corporation and its suppliers and
# licensors, and is protected by worldwide copyright and trade secret laws and
# treaty provisions. No part of the Material may be used, copied, reproduced,
# modified, published, uploaded, posted, transmitted, distributed, or disclosed
# in any way without Intel's prior express written permission.
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
#################################################################################
import re
import subprocess
import time
import datetime
from collections import OrderedDict

import requests

from dtaf_core.drivers.base_driver import BaseDriver
from dtaf_core.drivers.internal.console.proc_console import ProcConsole
from dtaf_core.drivers.internal.console.ssh_console import SshConsole
from dtaf_core.drivers.internal.console.telnet_console import TelnetConsole
from dtaf_core.drivers.internal.console.console import Shared
from datetime import datetime

from dtaf_core.lib.exceptions import DriverIOError


def init_return(func):
    def inner(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
        except DriverIOError as ex:
            print(ex)
            return False
        return res

    return inner


class SimicsDriver(BaseDriver):

    @property
    def SimicsChannel(self):
        channel = self.__console.get_channel(self.__buffer_name)
        return channel

    @property
    def SerialChannel(self):
        channel = self.__serial.get_channel(self.__buffer_name)
        return channel

    @property
    def HostChannel(self):
        channel = self.__host_console.get_channel(self.__buffer_name)
        return channel

    def register(self, buffer_name, buffer_size=4 * 1024 * 1024):
        self.__buffer_name = buffer_name
        if self.__host_console:
            self.__host_console.register(self.__buffer_name)
        self.__serial.register(self.__buffer_name)
        self.__console.register(self.__buffer_name)

    def unregister(self, buffer_name):
        self.__buffer_name = buffer_name
        if self.__host_console:
            self.__host_console.unregister(self.__buffer_name)
        self.__serial.unregister(self.__buffer_name)
        self.__console.unregister(self.__buffer_name)

    def stop(self):
        if self.__host_console_started and self.__host_console:
            self.__host_console.stop()
            self.__host_console_started = False
        if self.__serial_started:
            self.__serial.stop()
            self.__serial_started = False
        if self.__console_started:
            self.__console.stop()
            self.__console_started = False

    def __start_host_console(self):
        if not self.__host_console_started and self.__host_console:
            self.__host_console.start()
            self.__host_console_started = True

    def __start_serial(self):
        if not self.__serial_started:
            try:
                self.__serial.start()
                self.__serial_started = True
            except EOFError as e:
                self._log.warn(e)
            except ConnectionRefusedError as e:
                self._log.warn(e)

    def __start_console(self):
        if not self.__console_started:
            try:
                self.__console.start()
                self.__console_started = True
            except EOFError as e:
                self._log.warn(e)
            except ConnectionRefusedError as e:
                self._log.warn(e)

    def start(self):
        self.__start_host_console()
        self.__start_serial()
        self.__start_console()

    def __init__(self, cfg_opts, log):
        requests.urllib3.disable_warnings()
        self.session = requests.session()
        self.session.headers["Content-Type"] = "application/json"
        super(SimicsDriver, self).__init__(cfg_opts, log)
        host = self._driver_cfg_model.host
        self.__host = host
        self.__app = self._driver_cfg_model.app
        self.__script = self._driver_cfg_model.script
        self.__serial_port = self._driver_cfg_model.serial_port
        self.__service_port = self._driver_cfg_model.service_port
        self.__console = TelnetConsole(host=self.__host, port=self.__service_port, user="", password="")
        self.__serial = TelnetConsole(host=self.__host, port=self.__serial_port, user="", password="")
        self.__host_console = SshConsole(host=self._driver_cfg_model.host,
                                         port=self._driver_cfg_model.host_port,
                                         user=self._driver_cfg_model.host_username,
                                         password=self._driver_cfg_model.host_password) if host != 'localhost' else \
            ProcConsole(host=self._driver_cfg_model.host, port=self._driver_cfg_model.host_port, client=None)
        self.__host_console.start_console = self.__start_console
        self.__console_started = False
        self.__serial_started = False
        self.__host_console_started = False
        self.__buffer_name = ""
        self.__dhcp_pool_ip = self._driver_cfg_model.dhcp_pool_ip
        self.__simics_os = self._driver_cfg_model.simics_os
        self.__network_user = self._driver_cfg_model.network_user
        self.__network_password = self._driver_cfg_model.network_password
        self.__simics_network = self._driver_cfg_model.simics_network
        self.__init_dict = OrderedDict([
            ('os', [
                {'cmd': f"$os = {self.__simics_os}",
                 'until_pat': "[\s\S]+simics>",
                 'min_time': 5,
                 }]
             ),
            ('network', [
                {'cmd': "$enable_i82599_real_network = TRUE",
                 'until_pat': "[\s\S]+simics>",
                 'min_time': 5,
                 },
                {'cmd': f"$dhcp_pool_ip = {self.__dhcp_pool_ip}",
                 'until_pat': "[\s\S]+simics>",
                 'min_time': 5,
                 },
                {'cmd': '$service_node_ip_address = "192.168.1.1"',
                 'until_pat': "[\s\S]+simics>",
                 'min_time': 5,
                 },
                {'cmd': f'run-command-file "{self.__script}"',
                 'until_pat': "[\s\S]+simics>",
                 'min_time': 30,
                 },
                {'cmd': "connect-real-network target-ip = $dhcp_pool_ip",
                 'until_pat': "[\s\S]+simics>",
                 'min_time': 30,
                 }]),
            ('telnet_frontend', [
                {'cmd': f'telnet-frontend {self.__service_port}',
                 'until_pat': "[\s\S]+simics>",
                 'min_time': 5,
                 }]
             ),
            ('run_scripts', [
                {'cmd': f'run-command-file "{self.__script}"',
                 'until_pat': "[\s\S]+simics>",
                 'min_time': 20,
                 }]
             ),
            ('telnet_setup', [
                {'cmd': f"$system.serconsole.con.telnet-setup -ipv4 port={self.__serial_port}",
                 'until_pat': "[\s\S]+simics>",
                 'min_time': 30,
                 }]
             ),
            ('telnet_status', [
                {'cmd': "$system.serconsole.con.telnet-status",
                 'until_pat': "[\s\S]+simics>",
                 'min_time': 5,
                 }]
             ),
            ('real_time', [
                {'cmd': 'enable-real-time-mode',
                 'until_pat': "[\s\S]+simics>",
                 'min_time': 5,
                 }]
             ),
        ])

    def __enter__(self):
        self.start()
        return super(SimicsDriver, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        super(SimicsDriver, self).__exit__(exc_type, exc_val, exc_tb)

    def is_simics_running(self):
        if self._driver_cfg_model.host != "localhost":
            if self.__host_console.is_running():
                return self.HostChannel.execute_until("help\r", until_pat="running>", timeout=10) is not None

        else:
            if self.__host_console:
                return self.__host_console._client is not None
        return False

    def __launch_simics_in_remote_mode(self, command, time_out):
        self.__start_host_console()
        self.HostChannel.execute_until(cmd=command + '\r', until_pat="[\s\S]+simics>",
                                       timeout=max(30, time_out * 0.2))
        # enable telnet for simics console
        if self.__simics_os:
            self.__init_config(os=time_out * 0.1)
        self.__init_config(telnet_frontend=time_out * 0.1)
        if self.__simics_network:
            self.__init_config(network=time_out * 0.3)
        else:
            self.__init_config(run_scripts=time_out * 0.3)
        self.__start_console()
        if self._driver_cfg_model.mode_real_time:
            self.__init_config(real_time=time_out * 0.1)
        self.__init_config(telnet_setup=time_out * 0.1)
        ret = self.HostChannel.execute_until(cmd='run\r', until_pat="running>",
                                             timeout=max(30, time_out * 0.3))
        self.__start_serial()
        return ret is not None

    def __launch_simics_in_native_mode(self, command, time_out):
        self.__start_host_console()
        self.__host_console.launch_console(command)
        if self.__simics_os:
            self.__init_config(os=time_out * 0.1)
        self.__init_config(telnet_frontend=time_out * 0.1)
        if self.__simics_network:
            self.__init_config(network=time_out * 0.3)
        else:
            self.__init_config(run_scripts=time_out * 0.3)
        self.__start_console()
        self.__host_console.wait_for_completion(timeout=60, time_block=10)
        self.__start_console()
        self.__init_config(telnet_setup=time_out * 0.1, telnet_status=time_out * 0.1)
        ret = self.HostChannel.execute_until(cmd=b"run\r\n",
                                             until_pat="running>", timeout=max(20, time_out * 0.3))
        self.__start_serial()
        return ret is not None

    @init_return
    def launch_simics(self, time_out=0):
        if self._driver_cfg_model.host != "localhost":
            cmd = self.__app
            return self.__launch_simics_in_remote_mode(command=cmd, time_out=time_out)
        else:
            cmd = self.__app
            return self.__launch_simics_in_native_mode(command=cmd, time_out=time_out)

    def shutdown_simics(self):
        if self._driver_cfg_model.host == "localhost":
            if self.is_simics_running():
                time.sleep(5)
                self._kill_simics(pid=getattr(self.__host_console, '_client').pid)
                setattr(self.__host_console, '_client', None)
                return True
        else:
            if self.is_simics_running():
                self.HostChannel.execute_until(cmd="exit\r", until_pat="[\s\S]+simics>", timeout=5)
                self.HostChannel.execute_until(cmd="exit\r", until_pat=">", timeout=3)
                self.stop()
                return True
        return True

    def _kill_simics(self, pid=None):
        import psutil
        if pid is None:
            for p in psutil.process_iter():
                try:
                    if p.name().find("simics-com") != -1:
                        p.kill()
                except Exception as ex:
                    self._log.warn(ex)
        else:
            try:
                psutil.Process(pid).kill()
            except Exception as ex:
                self._log.error(f"simics pid is error ---- {ex}")

    def __init_config(self, **kwargs):
        ret = ''
        for init_name, time_out in kwargs.items():
            exe_list = self.__init_dict.get(init_name)
            for exe_args in exe_list:
                if self._driver_cfg_model.host == 'localhost':
                    cmd = ''.join([exe_args['cmd'], '\r\n']).encode()
                else:
                    cmd = ''.join([exe_args['cmd'], '\r'])
                ret = self.HostChannel.execute_until(cmd=cmd, until_pat=str(exe_args['until_pat']),
                                                     timeout=max(exe_args['min_time'], time_out))
                if ret:
                    time.sleep(0.5)
                else:
                    raise DriverIOError(f'There was an error executing the command -- {init_name}')
            if init_name == 'network':
                self._driver_cfg_model.extra_attr[f'{self._driver_cfg_model.host}:{self._driver_cfg_model.host_port}'][
                    'os_port'] = re.search(r"Host TCP port (\d+) -> .*?:22", ret).group(1)
