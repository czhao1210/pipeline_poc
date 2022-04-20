#!/usr/bin/env python
"""
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
"""
import re
import time
import datetime
from dtaf_core.drivers.base_driver import BaseDriver

class Powersplitter_Driver(BaseDriver):
    def __init__(self, cfg_opts, log):
        super(Powersplitter_Driver, self).__init__(cfg_opts, log)
        self._log = log
        self.username = self._driver_cfg_model.username
        self.password = self._driver_cfg_model.password
        self.port = self._driver_cfg_model.port
        self.ip = self._driver_cfg_model.ip

    def __enter__(self):
        return super(PduDriver, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(PduDriver, self).__exit__(exc_type, exc_val, exc_tb)

    def get_recv_data(self, ssh):
        ssh.sendall(self.invoke_cmd)
        time.sleep(0.5)
        self.invoke_recv_data += ssh.recv(1024).decode("utf-8")

    def wait_for_invoke(self, ssh):
        self.invoke_recv_data = ""
        nowtime = datetime.datetime.now()
        while (datetime.datetime.now() - nowtime).seconds < int(self.invoke_timeout):
            t = threading.Thread(target=self.get_recv_data, args=[ssh])
            t.setDaemon(True)
            t.start()
            t.join(3)
            for symbol in self.invoke_symbols:
                if symbol in self.invoke_recv_data:
                    if re.search(self.invoke_re, self.invoke_recv_data):
                        return
        time.sleep(int(self.invoke_timeout))

    def _execute(self, cmd_list):
        ssh = None
        client = None
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=self.ip, port=self.port,
                           username=self.username, password=self.password)
            ssh = client.get_transport().open_session()
            ssh.get_pty()
            ssh.invoke_shell()
            self.wait_for_invoke(ssh)
            for cmd in cmd_list:
                num = 0
                while num < 3:
                    ssh.sendall(cmd)
                    time.sleep(0.5)
                    num += 1
        except Exception as ex:
            self._log.error("[%s] %s target failed, the reason is %s"
                            % (datetime.datetime.now(), self.ip, str(ex)))
            raise ex
        finally:
            ssh.close()
            client.close()

    def _check_dict_value(self, dict_data):
        data = set(dict_data.values())
        if len(data) > 1:
            return False
        elif len(data) == 1 and list(data)[0]:
            return True
        elif len(data) == 1 and not list(data)[0]:
            return False
        else:
            return None

    def ac_power_on(self, timeout=None):
        # type: (int) -> bool
        """
        This API changes SUT from G3 to S0/S5. API will not check
        the initial state of SUT. It just sends signal.
        :param: username needs to be given for the pdu secure login identification purpose
                password for verfication of the username exists
                channel which power socket on the PDU needs to be controlled
                operation turn off or turn on universal standard 0 is off 1 is on.
                timeout  :second, the max time spend for executing AC_power_off to
                 SUT enter into G3, it should more than 0. If it is None,
                  API will refer to configuration for the default value.
        :return:
                True        : AC power supply has been connected.
                None        : Fail to send power on command
        :raise DriverIOError: if command execution failed in driver
        """

        self._execute(self.cmd_on)
        return self.get_ac_power_state(timeout)

    def ac_power_off(self, timeout=None):
        # type: (int) -> bool
        """
        This API will change SUT from S5/S0 to G3.
        It will check if the entrance state is S5 and if the final state is G3.
        :param: username needs to be given for the pdu secure login identification purpose
                password for verfication of the username exists
                channel which power socket on the PDU needs to be controlled
                operation turn off or turn on universal standard 0 is off 1 is on.
                timeout  :second, the max time spend for executing AC_power_off to
                 SUT enter into G3, it should more than 0. If it is None,
                 API will refer to configuration for the default value.
        :return:
                True        : AC power supply has been removed.
                None        : Fail to send power off command
        :raise DriverIOError: if command execution failed in driver
        :raise TimeoutException: fail to respond before timeout
        """

        self._execute(self.cmd_off)
        return not self.get_ac_power_state(timeout)

    def get_ac_power_state(self, timeout):
        # type: (None) -> bool
        """
        Get AC power Detection of SUT.
        :param: username needs to be given for the pdu secure login identification purpose
                password for verfication of the username exists
                channel which power socket on the PDU needs to be controlled
        :return:
            True    -    AC POWER Detected
            NONE     -   AC POWER NOT Detected

        :raise DriverIOError: if command execution failed in driver
        """
        ssh = None
        client = None
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=self.ip, port=self.port, username=self.username,
                           password=self.password, timeout=timeout)
            ssh = client.get_transport().open_session()
            ssh.get_pty()
            ssh.invoke_shell()
            self.wait_for_invoke(ssh)
            state_list = {}
            for cmd in self.cmd_show:
                num = 0
                while num < 3:
                    ssh.sendall(cmd)
                    time.sleep(0.5)
                    ret_data = ssh.recv(1024).decode("utf-8")
                    if 'On' in ret_data:
                        state_list[cmd] = True
                    elif 'Off' in ret_data:
                        state_list[cmd] = False
                    num += 1
            return self._check_dict_value(state_list)
        except Exception as ex:
            self._log.error("[%s] %s target failed, the reason is %s"
                            % (datetime.datetime.now(), self.ip, str(ex)))
            raise ex
        finally:
            ssh.close()
            client.close()
