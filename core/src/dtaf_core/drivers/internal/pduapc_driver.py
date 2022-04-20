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

import time
import telnetlib
from dtaf_core.drivers.base_driver import BaseDriver

class PduapcDriver(BaseDriver):
    def __init__(self, cfg_opts, log):
        super(PduapcDriver, self).__init__(cfg_opts, log)
        self._log = log
        self.tn = telnetlib.Telnet()
        self.username = self._driver_cfg_model.username
        self.password = self._driver_cfg_model.password
        self.outlet = self._driver_cfg_model.outlets
        self.ip = self._driver_cfg_model.ip
        self.port = self._driver_cfg_model.port

    def __enter__(self):
        return super(PduapcDriver, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(PduapcDriver, self).__exit__(exc_type, exc_val, exc_tb)

    def connect(self):
        try:
            self.tn.open(self.ip, port=self.port, timeout=20)
        except Exception as e:
            self._log.error('APC failed to connect! {0}'.format(e))
        self.tn.read_until(b'Username:', timeout=5)
        self.tn.write(self.username.encode('ascii') + b"\r\n")
        time.sleep(0.5)
        self.tn.read_until(b'Password:', timeout=5)
        self.tn.write(self.password.encode('ascii') + b"\r\n")
        command_result = self.tn.read_very_eager().decode('ascii')
        if 'error' not in command_result:
            self._log.info('APC PDU Telnet Communication Successful!')
            return True
        else:
            raise Exception('APC PDU Telnet Communication failed to login!')

    def disconnect(self):
        self.tn.write(b"exit\n")
        self.tn.close()

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
                False        : Fail to send power on command
        :raise DriverIOError: if command execution failed in driver
        """
        #print(self.outlet)
        try:
            if(self.connect() == True):
                for i in range(len(self.outlet)):
                    outlet = "olon  " + str(self.outlet[i])
                    self.tn.write(bytes(outlet,encoding='utf8') + b" \r\n")
                    time.sleep(1)
                    output = self.tn.read_very_eager().decode('ascii')
                    self._log.info(output)
                self._log.info("AC power connected.")
                self.disconnect()
                return True
        except Exception as ex:
            self._log.error("{0}".format(ex))
            self.disconnect()
            raise

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
                False        : Fail to send power off command
        :raise DriverIOError: if command execution failed in driver
        :raise TimeoutException: fail to respond before timeout
        """
        try:
            if(self.connect() == True):
                for i in range(len(self.outlet)):
                    outlet = "oloff  " + str(self.outlet[i])
                    self.tn.write(bytes(outlet, encoding='utf8') + b" \r\n")
                    time.sleep(1)
                    output = self.tn.read_very_eager().decode('ascii')
                    self._log.info(output)
                self._log.info("AC power Dis-Connected.")
                self.disconnect()
                return True
        except Exception as ex:
            self._log.error("{0}".format(ex))
            self.disconnect()
            raise


    def get_ac_power_state(self, timeout=None):
        # type: (None) -> bool
        """
        Get AC power Detection of SUT.
        :param: username needs to be given for the pdu secure login identification purpose
                password for verfication of the username exists
                channel which power socket on the PDU needs to be controlled
        :return:
            True    -    AC POWER Detected
            False     -   AC POWER NOT Detected

        :raise DriverIOError: if command execution failed in driver
        """
        try:
            if(self.connect() == True):
                for i in range(len(self.outlet)):
                    outlet = "olstatus  " + str(self.outlet[i])
                    self.tn.write(bytes(outlet, encoding='utf8') + b" \r\n")
                    time.sleep(1)
                    output = self.tn.read_very_eager().decode('ascii')
                    self._log.info(output)
                self.disconnect()
                if ": On" in output:
                    self._log.info("AC Outlet in Connected State and AC power Detected")
                    return True
                else:
                    self._log.info("AC Outlet in Dis-Connected State and AC power Not Detected")
                    return False
        except Exception as ex:
            self._log.error("{0}".format(ex))
            self.disconnect()
            raise