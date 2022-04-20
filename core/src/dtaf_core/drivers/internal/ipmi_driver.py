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
import time
import subprocess
from subprocess import Popen,PIPE,STDOUT
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.drivers.base_driver import BaseDriver

class IpmiDriver(BaseDriver):
    
    def __init__(self,cfg_opts,log):
        super(IpmiDriver, self).__init__(cfg_opts, log)
            
    def __enter__(self):
        return super(IpmiDriver, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(IpmiDriver, self).__exit__(exc_type, exc_val, exc_tb)

    def dc_power_on(self, timeout=None):
        """
        :send DC_POWER_ON command to Turn the platform on loads up the post code.
        :return: True or None
        :exception
            Error: BMC Ipmi Error.
        """
        try:
            self.__cmd_ipmitool = ("{0} -I lanplus -H {1} -U {2} -P {3}".format(self._driver_cfg_model.cmd,self._driver_cfg_model.ip,self._driver_cfg_model.username, self._driver_cfg_model.password))
            opt=subprocess.Popen(self.__cmd_ipmitool +" chassis power on",stdin=PIPE,stdout=PIPE,stderr=STDOUT,shell=True)
            opt=opt.stdout.read()
            if(str(opt).find(r"Chassis Power Control: Up/On")!=-1):
                self._log.info("SUT Is DC Powered On")
                return True
            else:
                self._log.error(opt)
        except Exception:
            self._log.error("Dc-Power ON via BMC-IPMI Failed To Happen")
            raise

    def dc_power_off(self, timeout=None):
        """
        :send DC_POWER_OFF command to Turn The Platform OFF puts in S5, So called dc powered off state.
        :return: True or None
        :exception
            Error: BMC Ipmi Error.
        """
        try:
            self.__cmd_ipmitool = (r"{0} -I lanplus -H {1} -U {2} -P {3}".format(self._driver_cfg_model.cmd,self._driver_cfg_model.ip,self._driver_cfg_model.username, self._driver_cfg_model.password))
            opt=subprocess.Popen(self.__cmd_ipmitool +" chassis power off",stdin=PIPE,stdout=PIPE,stderr=STDOUT,shell=True)
            opt=opt.stdout.read()
            if(str(opt).find(r"Chassis Power Control: Down/Off")!=-1):
                self._log.info("SUT Is DC Powered Off")
                return True
            else:
                self._log.error(opt)
        except Exception:
            self._log.error("Dc-Power OFF via BMC-IPMI Failed To Happen")
            raise

    def get_dc_power_state(self):
        """
        This API shields platform and control box difference.
        according to the platform setting in Config module,
        which signals' voltage need to be got are different support.
        Power states dependent on platform power schematic.
        :return:
        On      -   True
        Off     -   NONE
            Error: BMC Ipmi Error.
        """
        try:
            self.__cmd_ipmitool = (r"{0} -I lanplus -H {1} -U {2} -P {3}".format(self._driver_cfg_model.cmd,self._driver_cfg_model.ip,self._driver_cfg_model.username, self._driver_cfg_model.password))
            opt=subprocess.Popen(self.__cmd_ipmitool +" chassis power status",stdin=PIPE,stdout=PIPE,stderr=STDOUT,shell=True)
            opt=opt.stdout.read()
            if(str(opt).find(r"Chassis Power is on")!=-1):
                self._log.info("SUT DC Power Is Detected")
                return True
            else:
                self._log.info("SUT DC Power Is NOT Detected")
                self._log.debug(opt)
                return False
        except Exception:
            self._log.error("Dc-Power Detection via BMC-IPMI Failed To Happen")
            raise

    def dc_power_reset(self):
        """
        :send DC_Reset command reboot platform via BMC IPMI protocol 
        :return: True or None
        :exception
            Error: BMC Ipmi Error
        """
        try:
            self.__cmd_ipmitool = (r"{0} -I lanplus -H {1} -U {2} -P {3}".format(self._driver_cfg_model.cmd,self._driver_cfg_model.ip,self._driver_cfg_model.username, self._driver_cfg_model.password))
            opt=subprocess.Popen(self.__cmd_ipmitool +" chassis power reset",stdin=PIPE,stdout=PIPE,stderr=STDOUT,shell=True)
            opt=opt.stdout.read()
            if(str(opt).find(r"Chassis Power Control: Reset")!=-1):
                self._log.debug("SUT Reboot functionality Performed")
                return True
            elif(opt.find(r"Set Chassis Power Control to Reset failed: Command not supported in present state")!=-1):                
                self._log.error("SUT is in DC powered OFF S5 state,Hence Can't Perform Reboot Operation")
            else:
                self._log.debug(opt)
        except Exception:
            self._log.error("Dc-Power Reset via BMC-IPMI Failed To Happen")
            raise

    def execute(self,ipmi_cmd=None):
        """
        : sends command to bmc using ipmi tool
        many user required commands are available in order to perform various functionalities in such cases cmd can be executed using this api.
        :ipmi_cmd parameter to take the inputs from the user and executes it over ipmi tool
        :return output of the passed cmd
        :exception
            Error: BMC Ipmi Error
        """
        try:
            self.__cmd_ipmitool = (r"{0} -I lanplus -H {1} -U {2} -P {3}".format(self._driver_cfg_model.cmd,self._driver_cfg_model.ip,self._driver_cfg_model.username, self._driver_cfg_model.password))
            opt=subprocess.Popen(self.__cmd_ipmitool +" "+str(ipmi_cmd),stdin=PIPE,stdout=PIPE,stderr=STDOUT,shell=True)
            output=opt.stdout.read()
            self._log.debug(output)
            return output
        except Exception:
            self._log.error("Execution Of Given "+str(ipmi_cmd)+" Failed")
            raise
