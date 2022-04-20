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
#################################################################################\
from dtaf_core.providers.ac_power import AcPowerControlProvider
from dtaf_core.providers.dc_power import DcPowerControlProvider

import time
import subprocess
from dtaf_core.drivers.base_driver import BaseDriver

class PdupiDriver(BaseDriver):
    
    def __init__(self,cfg_opts,log):
        super(PdupiDriver, self).__init__(cfg_opts, log)
        
    def __enter__(self):
        return super(PdupiDriver, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(PdupiDriver, self).__exit__(exc_type, exc_val, exc_tb)

    def dc_power_on(self,channel=None,timeout=None):
        """
        This API changes SUT from S5(Shutdown) State to S0(Wakeup)State. API will not check the initial state of SUT. It just sends signal.
        :param: channel which power socket on the PDU needs to be controlled
                operation turn off or turn on universal standard 0 is off 1 is on.
                timeout  :second, the max time spend for executing AC_power_off to SUT enter into G3, it should more than 0. If it is None, API will refer to configuration for the default value.
        :return:
                True        : DC power supply has been connected.
                None        : Fail to send power on command
        :raise DriverIOError: if command execution failed in driver
        """
        if channel is None:
            channel = self._driver_cfg_model.channel
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/dcpower/"+str(channel)+"/1/"+str(int(timeout))
            if(self._driver_cfg_model.proxy):
               url+= ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            if(b"Power ON" in ret):
                time.sleep(3)
                return True     
        except Exception:
            self._log.error("Dc-Power ON via Smart_R-PI_PDU Failed To Happen")
            raise

    def dc_power_off(self,channel=None,timeout=None):
        """
        This API changes SUT from S0(Wakeup)State to S5(Shutdown) State. API will not check the initial state of SUT. It just sends signal.
        :param: channel which power socket on the PDU needs to be controlled
                operation turn off or turn on universal standard 0 is off 1 is on.
                timeout  :second, the max time spend for executing AC_power_off to SUT enter into G3, it should more than 0. If it is None, API will refer to configuration for the default value.
        :return:
                True        : DC power OFF was performed.
                None        : Fail to send power on command
        :raise DriverIOError: if command execution failed in driver
        """
        if channel is None:
            channel = self._driver_cfg_model.channel
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/dcpower/"+str(channel)+"/0/"+str(int(timeout))
            if self._driver_cfg_model.proxy:
               url+= ' -x ' + self._driver_cfg_model.proxy
            ret = subprocess.check_output(url, shell=True)
            if(b"Power OFF" in ret):
                time.sleep(3)
                return True     
        except Exception:
            self._log.error("Dc-Power Off via Smart_R-PI_PDU Failed To Happen")
            raise
    
    def get_dc_power_state(self,channel=None):
        """
        Get DC power Detection of Platform(SUT).
        :param: username needs to be given for the pdu secure login identification purpose
                password for verfication of the username exists
                channel which power socket on the PDU needs to be controlled
        :return:
            True    -    DC POWER Detected
            NONE     -   DC POWER NOT Detected
            
        :raise DriverIOError: if command execution failed in driver
        """
        if channel is None:
            channel = self._driver_cfg_model.channel
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/dcdetect/"+str(channel)
            if(self._driver_cfg_model.proxy):
                url+= ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            if(b"Detected" in ret):
                return True
        except Exception:
            self._log.error("Dc-Power State Detection Failed To Happen")
            raise

    def dc_power_reset(self,channel=None):
        """
        :send DC_Reset command to Gpio To Turn The Relay to go High which physcialy interact with Front Panel Gpio.
        :return: True or None
        :exception
        FlaskError: Raspberry PDUpi Flask Error.
        """
        if channel is None:
            channel = self._driver_cfg_model.channel
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/reboot"+str(channel)
            if(self._driver_cfg_model.proxy):
                url+= ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            if(b"Reboot" in ret):
                return True
        except Exception:
            self._log.error("Dc-Reset via R-pi Failed To Happen")
            raise
        
    def ac_power_on(self,username=None,password=None,channel=None,timeout=None):
        # type: (int) -> bool
        """
        This API changes SUT from G3 to S0/S5. API will not check the initial state of SUT. It just sends signal.
        :param: username needs to be given for the pdu secure login identification purpose
                password for verfication of the username exists
                channel which power socket on the PDU needs to be controlled
                operation turn off or turn on universal standard 0 is off 1 is on.
                timeout  :second, the max time spend for executing AC_power_off to SUT enter into G3, it should more than 0. If it is None, API will refer to configuration for the default value.
        :return:
                True        : AC power supply has been connected.
                None        : Fail to send power on command
        :raise DriverIOError: if command execution failed in driver
        """
        if(username):
            usr=username
        else:
            usr=self._driver_cfg_model.username
        if(password):
            pwd=password
        else:
            pwd=self._driver_cfg_model.password
        if channel is None:
            channel = self._driver_cfg_model.channel
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/acpower/"+str(usr)+"/"+str(pwd)+"/"+str(channel)+"/1/"+str(int(timeout))
            if(self._driver_cfg_model.proxy):
               url+= ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            if(b"Power ON" in ret):
                return True     
        except Exception:
            self._log.error("Ac-Power ON via Smart_R-PI_PDU Failed To Happen")
            raise
    
    def ac_power_off(self,username=None,password=None,channel=None,timeout=None):
        # type: (int) -> str
        """
        This API will change SUT from S5/S0 to G3.
        It will check if the entrance state is S5 and if the final state is G3.
        :param: username needs to be given for the pdu secure login identification purpose
                password for verfication of the username exists
                channel which power socket on the PDU needs to be controlled
                operation turn off or turn on universal standard 0 is off 1 is on.
                timeout  :second, the max time spend for executing AC_power_off to SUT enter into G3, it should more than 0. If it is None, API will refer to configuration for the default value.
        :return:
                True        : AC power supply has been removed.
                None        : Fail to send power off command
        :raise DriverIOError: if command execution failed in driver
        :raise TimeoutException: fail to respond before timeout
        """
        if(username):
            usr=username
        else:
            usr=self._driver_cfg_model.username
        if(password):
            pwd=password
        else:
            pwd=self._driver_cfg_model.password
        if channel is None:
            channel = self._driver_cfg_model.channel
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/acpower/"+str(usr)+"/"+str(pwd)+"/"+str(channel)+"/0/"+str(int(timeout))
            if(self._driver_cfg_model.proxy):
                url+= ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            if(b"Power OFF" in ret):
                return True
        except Exception:
            self._log.error("Ac-Power OFF Smart_R-PI_PDU Failed To Happen")
            raise                                                                                                                                                     
        
    def get_ac_power_state(self,username=None,password=None,channel=None):
        # type: (None) -> str
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
        if(username):
            usr=username
        else:
            usr=self._driver_cfg_model.username
        if(password):
            pwd=password
        else:
            pwd=self._driver_cfg_model.password
        if channel is None:
            channel = self._driver_cfg_model.channel
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/acdetect/"+str(usr)+"/"+str(pwd)+"/"+str(channel)
            if(self._driver_cfg_model.proxy):
                url+= ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            if(b"Detected" in ret):
                return True
        except Exception:
            self._log.error("Ac-Power State Detection via R-pi_PDU Failed To Happen")
            raise                                                                                                                                                    
                                                                                                                      
    def set_username_password(self,channel,username,password):
        # type: (None) -> str
        """
        For Security Reason socket are controlled with username and Password
        :param: username needs to be given for the pdu secure login identification purpose
                password for verfication of the username exists
                channel which power socket on the PDU needs to be controlled
        :return:
            True    -   Password was set successfully.
            None    -   password failed to get set
        :raise DriverIOError: if command execution failed in driver
        :raise TimeoutException: fail to respond before timeout
        """
        if(username):
            usr=username
        else:
            usr=self._driver_cfg_model.username
        if(password):
            pwd=password
        else:
            pwd=self._driver_cfg_model.password
        if channel is None:
            channel = self._driver_cfg_model.channel
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/set/"+str(channel)+"/"+str(usr)+"/"+str(pwd)
            if(self._driver_cfg_model.proxy):
                url+= ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            print(ret)
            if((ret.find("Failed"))==-1):
                return True
        except Exception:
            self._log.error("Username and Password Failed To get set")
            raise                                                                                                                                                    
       
    def reset_username_password(self,channel,master_passkey):
        # type: (None) -> str
        """
        Reset Forgotten UserName and Password for PDU sockets
        
        Incase the user forgets username and password to override it from the API level

        :param channel which power socket on the PDU needs to be controlled
               masterkey which has super user access to override the existing username and password
        :return:
            True     -   if the reset of Username and Password was reset
            None     -   Unable to Do the restting of the username and password
        :raise PDUPIError:  Hardware Error from pi driver
        """
        try:
            url = "curl -X GET http://" + self._driver_cfg_model.ip + "/unset/"+str(channel)+"/"+str(master_passkey)
            if(self._driver_cfg_model.proxy):
                url+= ' -x ' + self._driver_cfg_model.proxy

            ret = subprocess.check_output(url, shell=True)
            if(b"UserName and Password Removed" in ret):
                return True
        except Exception:
            self._log.error("Ac-Power OFF via R-pi_PDU Failed To Happen")
            raise                                                                                                                                                    
