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
import subprocess
from dtaf_core.drivers.base_driver import BaseDriver
from dtaf_core.lib.configuration import ConfigurationHelper

class YkushDriver(BaseDriver):
    def __init__(self, cfg_opts, log):
        super(YkushDriver, self).__init__(cfg_opts, log)
        self._ykush_app_path = self._driver_cfg_model.ykusk_app_path
        self._ykush_app_name = "ykushcmd.exe"

    def __enter__(self):
        return super(YkushDriver, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(YkushDriver, self).__exit__(exc_type, exc_val, exc_tb)

    def enable_usb_power(self,*port):
        """
        This Function Enables the YKUSH PORTS
        input:- ports numbers
        output:- True if successfull on Enabling the Ykush Ports
                 False if error or operation not performed
        """
        port = str(port).split(',')
        special_sym = [' ', '\'', '[', ')', ']', ',', '(', '"']
        for i in special_sym:
            port = str(port).replace(i, '')
        for i in range(0, len(port)):
            try:
                self._log.info("Before Enabling Checking For Port Status {0}".format(port[i]))
                ret=subprocess.check_output(self._ykush_app_path+"\\"+self._ykush_app_name+" -g "+port[i],shell=True)
                self._log.info({0}.format(ret))
            except Exception as ex:
                self._log.error("Failed to Check Port {0}".format(ex))
                False
        for i in range(0, len(port)):
            try:
                self._log.info("Enabling Ykush Ports {0}".format(port[i]))
                ret=subprocess.check_output(self._ykush_app_path+"\\"+self._ykush_app_name+" -u "+port[i],shell=True)
                self._log.info({0}.format(ret))
            except Exception as ex:
                self._log.error("Failed to Enable Port {0}".format(ex))
        for i in range(0, len(port)):
            try:
                self._log.info("After Enabling Checking For Port Status {0}".format(port[i]))
                ret=subprocess.check_output(self._ykush_app_path+"\\"+self._ykush_app_name+" -g "+port[i],shell=True)
                self._log.info({0}.format(ret))
            except Exception as ex:
                self._log.error("Failed to Check Port {0}".format(ex))
                return False
        return True

    def disable_usb_power(self,*port):
        """
        This Function Diables the YKUSH PORTS
        input ports numbers
        output:- True if successfull on Disabling the Ykush Ports
                 False if error or operation not performed
        """
        port = str(port).split(',')
        special_sym = [' ', '\'', '[', ')', ']', ',', '(', '"']
        for i in special_sym:
            port = str(port).replace(i, '')
        for i in range(0, len(port)):
            try:
                self._log.info("Before Diabling Checking For Port Status {0}".format(port[i]))
                ret = subprocess.check_output(self._ykush_app_path +"\\"+ self._ykush_app_name + " -g " + port[i],
                                              shell=True)
                self._log.info({0}.format(ret))
            except Exception as ex:
                self._log.error("Failed to Check Port {0}".format(ex))
                return False
        for i in range(0, len(port)):
            try:
                self._log.info("Disabling Ykush Ports {0}".format(port[i]))
                ret = subprocess.check_output(self._ykush_app_path +"\\"+ self._ykush_app_name + " -d " + port[i],
                                              shell=True)
                self._log.info({0}.format(ret))
            except Exception as ex:
                self._log.error("Failed to Disable Port {0}".format(ex))
                return False
        for i in range(0, len(port)):
            try:
                self._log.info("After Enabling Checking For Port Status {0}".format(port[i]))
                ret = subprocess.check_output(self._ykush_app_path +"\\"+ self._ykush_app_name + " -g " + port[i],
                                              shell=True)
                self._log.info({0}.format(ret))
            except Exception as ex:
                self._log.error("Failed to Check Port {0}".format(ex))
                return False
        return True