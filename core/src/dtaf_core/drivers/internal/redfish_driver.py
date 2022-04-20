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
import json
import asyncio
import requests
from dtaf_core.drivers.base_driver import BaseDriver
from dtaf_core.drivers.internal.bmc.idrac import IdracBmc
from dtaf_core.drivers.internal.bmc.ilo import IloBmc
from dtaf_core.lib.exceptions import DriverIOError
import time

from datetime import datetime

class RedfishDriver(BaseDriver):

    def __init__(self, cfg_opts, log):
        requests.urllib3.disable_warnings()
        self.session = requests.session()
        super(RedfishDriver, self).__init__(cfg_opts, log)
        self._platform_bmc = self._driver_cfg_model.bmc_type
        self._session_timer = self._driver_cfg_model.session

    def __enter__(self):
        return super(RedfishDriver, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(RedfishDriver, self).__exit__(exc_type, exc_val, exc_tb)

    def ac_power_on(self, timeout=None):
        if self._driver_cfg_model.bmc_type == "aurora":
            from dtaf_core.drivers.internal.tunnel.aurora import AuroraBMC, AuroraSUT
            bmc = AuroraBMC(bmc_address=f"{self._driver_cfg_model.chassis_server}:{self._driver_cfg_model.chassis_port}",
                            username=f"{self._driver_cfg_model.chassis_username}",
                            password=f"{self._driver_cfg_model.chassis_password}")
            sut = AuroraSUT(bmc_address=f"{self._driver_cfg_model.system_server}:{self._driver_cfg_model.system_port}",
                            username=f"{self._driver_cfg_model.system_username}",
                            password=f"{self._driver_cfg_model.system_password}")
            bmc.turn_on_bmc(self._driver_cfg_model.blade)
            __start = datetime.now()
            timeout = 10 if timeout is None else timeout
            power_on = False
            while (datetime.now()-__start).seconds < timeout and not power_on:
                power_on = sut.is_bmc_alive()
                time.sleep(1)
            if power_on:
                return sut.dc_power_on()
            return False
        else:
            try:
                data = {"ResetType": "ForceOn"}
                data = json.dumps(data)
                url = (
                    r'https://{0}/redfish/v1/Systems/system/Actions/ComputerSystem.Reset'.format(self._driver_cfg_model.ip))
                auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
                reps = self.session.post(url, auth=auth1, verify=False, data=data)
                if (reps.status_code != 200):
                    self._log.error(
                        "post method response failed for AC Power On,{0} operation failed".format(reps.status_code))
                else:
                    self._log.debug("SUT Is AC Powered On")
                    self._log.debug("Ac-power On via {0}".format(reps.content))
                    return True
            except Exception:
                self._log.error("Ac-Power ON via BMC-Redfish Failed To Happen")
                raise

    def ac_power_off(self, timeout=None):
        if self._driver_cfg_model.bmc_type == "aurora":
            from dtaf_core.drivers.internal.tunnel.aurora import AuroraBMC, AuroraSUT
            bmc = AuroraBMC(bmc_address=f"{self._driver_cfg_model.chassis_server}:{self._driver_cfg_model.chassis_port}",
                            username=f"{self._driver_cfg_model.chassis_username}",
                            password=f"{self._driver_cfg_model.chassis_password}")
            sut = AuroraSUT(bmc_address=f"{self._driver_cfg_model.system_server}:{self._driver_cfg_model.system_port}",
                            username=f"{self._driver_cfg_model.system_username}",
                            password=f"{self._driver_cfg_model.system_password}")
            ret = bmc.turn_off_bmc(self._driver_cfg_model.blade)
            __start = datetime.now()
            timeout = 30 if timeout is None else timeout
            power_on = False
            while (datetime.now()-__start).seconds < timeout and power_on:
                power_on = sut.is_bmc_alive()
                time.sleep(1)
            time.sleep(self._driver_cfg_model.safe_time)
            return ret
        else:
            try:
                data = {"ResetType": "ForceOff"}
                data = json.dumps(data)
                url = (
                    r'https://{0}/redfish/v1/Systems/system/Actions/ComputerSystem.Reset'.format(self._driver_cfg_model.ip))
                auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
                reps = self.session.post(url, auth=auth1, verify=False, data=data)
                if (reps.status_code != 200):
                    self._log.error(
                        "post method response failed for AC power OFF,{0} operation failed".format(reps.status_code))
                else:
                    self._log.debug("SUT Is AC Powered Off via BMC Redfish")
                    self._log.debug("Ac-power Off  {0}".format(reps.content))
                    return True
            except Exception:
                self._log.error("Ac-Power OFF via BMC-Redfish Failed To Happen")
                raise

    def dc_power_on(self, timeout=None):
        """
        :send DC_POWER_ON command to Turn the platform on loads up the post code.
        :return: True or None
        :exception
            Error: BMC Redfish Error.
        """
        if self._driver_cfg_model.bmc_type == "aurora":
            from dtaf_core.drivers.internal.tunnel.aurora import AuroraSUT
            sut = AuroraSUT(bmc_address=f"{self._driver_cfg_model.system_server}:{self._driver_cfg_model.system_port}",
                            username=f"{self._driver_cfg_model.system_username}",
                            password=f"{self._driver_cfg_model.system_password}")
            ret = sut.dc_power_on()
            __start = datetime.now()
            timeout = 30 if timeout is None else timeout
            power_on = False
            while (datetime.now()-__start).seconds < timeout and not power_on:
                power_on = sut.get_dc_power_state()
                time.sleep(1)
            return power_on
        elif self._driver_cfg_model.bmc_type == "idrac":
            obj = IdracBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                return obj.dc_power_on(computersystemid="System.Embedded.1")
            except Exception:
                raise DriverIOError('Dc on failed.')
        elif self._driver_cfg_model.bmc_type in[ "ilo","sm"]:
            obj = IloBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                if(obj.dc_power_on(computersystemid="1") == True):
                    self._log.info("Platform Dc-Power ON for this BMC-IP Successful {0}".format(self._driver_cfg_model.ip))
                    return True
                else:
                    self._log.error("Platform Dc-Power On Failed for this BMC-IP {0}".format(self._driver_cfg_model.ip))
                    return False
            except Exception:
                raise DriverIOError('Dc on Failed via BMC ILO Interface')
        try:
            ret = []
            ret = self._driver_cfg_model.ip.split("|")
            if (self._platform_bmc == "rvp"):
                for i in range(0, len(ret)):
                    data = {"ResetType": "On"}
                    data = json.dumps(data)
                    url = (
                        r'https://{0}/redfish/v1/Systems/system/Actions/ComputerSystem.Reset'.format(ret[i]))
                    auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
                    if (self._session_timer == False):
                        reps = requests.post(url, auth=auth1, verify=False, data=data)
                    else:
                        reps = self.session.post(url, auth=auth1, verify=False, data=data)
                    if (reps.status_code != 200):
                        self._log.error(
                            "post method response failed for DC Power On,{0} operation failed".format(reps.status_code))
                        return False
                    else:
                        self._log.info("Platform is Dc-Power On for this BMC-IP {0}".format(ret[i]))
                        self._log.debug("Dc-power On via {0}".format(reps.content))
                return True
            else:
                session = requests.session()
                requests.urllib3.disable_warnings()
                for i in range(0, len(ret)):
                    url = (
                        r'https://{0}/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset'.format(ret[i]))
                    payload = {'ResetType': 'On'}
                    headers = {'content-type': 'application/json'}
                    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False,
                                             auth=(self._driver_cfg_model.username, self._driver_cfg_model.password))
                    if (response.status_code == 204):
                        self._log.info("Platform is Dc-Power On for this BMC-IP {0}".format(ret[i]))
                        self._log.debug("Dc-power On  {0}".format(response.content))
                    else:
                        self._log.error("post method response failed for DC power On,{0} operation failed".format(
                            response.status_code))
                        return False
                return True
        except Exception as ex:
            self._log.error("Dc-Power ON via BMC-Redfish Failed To Happen {0}".format(ex))
            raise

    def dc_power_off(self, timeout=None):
        """
        :send DC_POWER_OFF command to Turn The Platform OFF puts in S5, So called dc powered off state.
        :return: True or None
        :exception
            Error: BMC Redfish Error.
        """

        if self._driver_cfg_model.bmc_type == "aurora":
            from dtaf_core.drivers.internal.tunnel.aurora import AuroraSUT
            sut = AuroraSUT(bmc_address=f"{self._driver_cfg_model.system_server}:{self._driver_cfg_model.system_port}",
                            username=f"{self._driver_cfg_model.system_username}",
                            password=f"{self._driver_cfg_model.system_password}")
            ret = sut.dc_power_off()
            __start = datetime.now()
            timeout = 30 if timeout is None else timeout
            power_on = False
            while (datetime.now()-__start).seconds < timeout and power_on:
                power_on = sut.get_dc_power_state()
                time.sleep(1)
            return not power_on
        elif self._driver_cfg_model.bmc_type == "idrac":
            obj = IdracBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                return obj.dc_power_off(computersystemid="System.Embedded.1")
            except Exception:
                raise DriverIOError("Dc off failed.")
        elif self._driver_cfg_model.bmc_type in ["ilo", "sm"]:
            obj = IloBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                if(obj.dc_power_off(computersystemid="1") == True):
                    self._log.info("Platform is Dc-Power OFF for this BMC-IP {0}".format(self._driver_cfg_model.ip))
                    return True
                else:
                    self._log.error("Dc-Power OFF for this BMC-IP Failed{0}".format(self._driver_cfg_model.ip))
                    return False
            except Exception:
                raise DriverIOError("Dc Power OFF Failed via BMC ILO Interface")
        try:
            ret = []
            ret = self._driver_cfg_model.ip.split("|")
            if (self._platform_bmc == "rvp"):
                for i in range(0, len(ret)):
                    data = {"ResetType": "ForceOff"}
                    data = json.dumps(data)
                    url = (
                        r'https://{0}/redfish/v1/Systems/system/Actions/ComputerSystem.Reset'.format(ret[i]))
                    auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
                    if(self._session_timer == False):
                        reps = requests.post(url, auth=auth1, verify=False, data=data)
                    else:
                        reps = self.session.post(url, auth=auth1, verify=False, data=data)
                    if (reps.status_code != 200):
                        self._log.error(
                            "post method response failed for DC power OFF,{0} operation failed".format(
                                reps.status_code))
                    else:
                        self._log.info("Platform is Dc-Power OFF for this BMC-IP {0}".format(ret[i]))
                        self._log.debug("Dc-power Off  {0}".format(reps.content))
                return True
            else:
                session = requests.session()
                requests.urllib3.disable_warnings()
                for i in range(0, len(ret)):
                    url = (
                        r'https://{0}/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset'.format(ret[i]))
                    payload = {'ResetType': 'ForceOff'}
                    headers = {'content-type': 'application/json'}
                    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False,
                                             auth=(self._driver_cfg_model.username, self._driver_cfg_model.password))
                    if (response.status_code == 204):
                        self._log.info("Platform is Dc-Power OFF for this BMC-IP {0}".format(ret[i]))
                        self._log.debug("Dc-power Off  {0}".format(response.content))
                    else:
                        self._log.error("post method response failed for DC power OFF,{0} operation failed".format(
                            response.status_code))
                        return False
                return True
        except Exception as ex:
            self._log.error("Dc-Power OFF via BMC-Redfish Failed To Happen {0}".format(ex))
            raise

    def get_ac_power_state(self):
        """
        Power states dependent on platform power schematic.
        :return:
        On      -   True
        Off     -   NONE
            Error: BMC Redfish Error.
        """
        if self._driver_cfg_model.bmc_type == "aurora":
            from dtaf_core.drivers.internal.tunnel.aurora import AuroraBMC, AuroraSUT
            bmc = AuroraBMC(bmc_address=f"{self._driver_cfg_model.chassis_server}:{self._driver_cfg_model.chassis_port}",
                            username=f"{self._driver_cfg_model.chassis_username}",
                            password=f"{self._driver_cfg_model.chassis_password}")
            sut = AuroraSUT(bmc_address=f"{self._driver_cfg_model.system_server}:{self._driver_cfg_model.system_port}",
                            username=f"{self._driver_cfg_model.system_username}",
                            password=f"{self._driver_cfg_model.system_password}")
            return sut.is_bmc_alive()
        else:
            try:
                url = (r'https://{0}/redfish/v1/Systems/system'.format(self._driver_cfg_model.ip))
                auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
                reps = self.session.get(url, auth=auth1, verify=False)
                b = reps.json()
                c = b["PowerState"]
                if (reps.status_code != 200):
                    self._log.error("GET method response fail for Dc Power State Detection,{0} operation failed".format(
                        reps.status_code))
                elif (str(b["PowerState"]).find("On") != -1):
                    return True
                elif (str(b["PowerState"]).find("Off") != -1):
                    return True
            except Exception as ex:
                self._log.error("Dc-Power State Detectionvia BMC-Redfish Failed To Happen {0}".format(ex))
                raise

    def get_dc_power_state(self):
        """
        Power states dependent on platform power schematic.
        :return:
        On      -   True
        Off     -   NONE
            Error: BMC Redfish Error.
        """

        if self._driver_cfg_model.bmc_type == "aurora":
            from dtaf_core.drivers.internal.tunnel.aurora import AuroraSUT
            sut = AuroraSUT(bmc_address=f"{self._driver_cfg_model.system_server}:{self._driver_cfg_model.system_port}",
                            username=f"{self._driver_cfg_model.system_username}",
                            password=f"{self._driver_cfg_model.system_password}")
            ret = sut.get_dc_power_state()
            return ret
        elif self._driver_cfg_model.bmc_type == "idrac":
            obj = IdracBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                if obj.dc_power_state(computersystemid="System.Embedded.1") == "On":
                    return True
                return False
            except Exception:
                raise DriverIOError("Get dc power state failed.")
        elif self._driver_cfg_model.bmc_type == "ilo":
            obj = IloBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                if obj.dc_power_state(computersystemid="1") == "On":
                    self._log.info("Platform Dc-Power State is Detected")
                    return True
                else:
                    self._log.info("Platform Dc-Power State is NOT Detected")
                    return False
            except Exception:
                raise DriverIOError("Get dc power state failed.")
        try:
            ret = []
            ret = self._driver_cfg_model.ip.split("|")
            if (self._platform_bmc == "rvp"):
                for i in range(0, len(ret)):
                    url = (r'https://{0}/redfish/v1/Systems/system'.format(ret[i]))
                    auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
                    if (self._session_timer == False):
                        reps = requests.get(url, auth=auth1, verify=False)
                    else:
                        reps = self.session.get(url, auth=auth1, verify=False)
                    b = reps.json()
                    c = b["PowerState"]
                    if (reps.status_code != 200):
                        self._log.error(
                            "GET method response fail for Dc Power State Detection,{0} operation failed {1}".format(
                                reps.status_code, ret[i]))
                    if (str(b["PowerState"]).find("On") != -1):
                        self._log.info(
                            "Platform Dc-Power State Detection for this BMC-IP {0} is Getting Detected".format(ret[i]))
                        flag = True
                    elif (str(b["PowerState"]).find("Off") != -1):
                        self._log.info(
                            "Platform Dc-Power State Detection for this BMC-IP {0} is Not Getting Detected".format(
                                ret[i]))
                        flag = False
                return flag
            else:
                for i in range(0, len(ret)):
                    session = requests.session()
                    requests.urllib3.disable_warnings()
                    response = requests.get("https://{0}/redfish/v1/Systems/System.Embedded.1",
                                            verify=False,
                                            auth=(self._driver_cfg_model.username, self._driver_cfg_model.password))
                    data = response.json()
                    if (response.status_code != 204):
                        self._log.error(
                            "GET method response fail for Dc Power State Detection,{0} operation failed {1}".format(
                                response.status_code, ret[i]))
                    if (str(data[u'PowerState']).find("On") != -1):
                        flag = True
                    elif (str(data["PowerState"]).find("Off") != -1):
                        self._log.info(
                            "Platform Dc-Power State Detection for this BMC-IP {0} is Not Getting Detected".format(
                                ret[i]))
                        flag = None
                return flag
        except Exception as ex:
            self._log.error("Power State Detection via BMC-Redfish Failed To Happen {0}".format(ex))
            raise

    def dc_power_reset(self):
        """
        :send DC_Reset command reboot platform via BMC Redfish Interface
        :return: True or None
        :exception
            Error: BMC Redfish Error.
        """
        if self._driver_cfg_model.bmc_type == "aurora":
            timeout = 30
            self.dc_power_off(timeout=timeout)
            return self.dc_power_on(timeout=timeout)
        elif self._driver_cfg_model.bmc_type == "idrac":
            obj = IdracBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                return obj.dc_power_reset(computersystemid="System.Embedded.1")
            except Exception:
                raise DriverIOError("dc reset failed.")
        elif self._driver_cfg_model.bmc_type in ["ilo","sc"]:
            obj = IloBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                if(obj.dc_power_reset(computersystemid="1") == "power off"):
                    self._log.error("DC power is Turned OFF, reset Won't in DC OFF state")
                    return False
                else:
                    self._log.info("Platform Dc-Reboot Operation is Performed from this BMC-IP {0}".format(self._driver_cfg_model.ip))
                    return True
            except Exception:
                raise DriverIOError("Get dc power restart failed via bmc ilo interface")
        try:
            ret = []
            ret = self._driver_cfg_model.ip.split("|")
            if (self._platform_bmc == "rvp"):
                for i in range(0, len(ret)):
                    data = {"ResetType": "ForceRestart"}
                    data = json.dumps(data)
                    url = (
                        r'https://{0}/redfish/v1/Systems/system/Actions/ComputerSystem.Reset'.format(ret[i]))
                    auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
                    if (self._session_timer == False):
                        reps = requests.get(url, auth=auth1, verify=False, data=data)
                    else:
                        reps = self.session.post(url, auth=auth1, verify=False, data=data)
                    if (reps.status_code != 200):
                        self._log.error(
                            "post method response failed for DC Power Reset,{0} operation failed".format(
                                reps.status_code))
                    else:
                        self._log.info("Platform Dc-Reboot Operation is Performed from this BMC-IP {0}".format(ret[i]))
                        self._log.debug(" SUT Reboot functionality Performed via BMC-Redfish Interface")
                        self._log.debug("Dc-Power Reset {0}".format(reps.content))
                return True
            else:
                session = requests.session()
                requests.urllib3.disable_warnings()
                for i in range(0, len(ret)):
                    url = (
                        r'https://{0}/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset'.format(ret[i]))
                    payload = {'ResetType': 'ForceRestart'}
                    headers = {'content-type': 'application/json'}
                    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False,
                                             auth=(self._driver_cfg_model.username, self._driver_cfg_model.password))
                    if (response.status_code == 204):
                        self._log.info("Platform Reboot for this BMC-IP {0} Successfull".format(ret[i]))
                        self._log.debug("Dc Reboot  {0}".format(response.content))
                    else:
                        self._log.error("post method response failed for DC Reboot,{0} operation failed".format(
                            response.status_code))
                        return False
                return True
        except Exception as ex:
            self._log.error("Dc-Power Reset via BMC-Redfish Failed To Happen {0}".format(ex))
            raise

    def clear_cmos(self):
        if self._driver_cfg_model.bmc_type == "idrac":
            obj = IdracBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                return obj.clear_cmos(computersystemid="System.Embedded.1")
            except Exception:
                raise DriverIOError("Clear cmos failed")
        elif self._driver_cfg_model.bmc_type in ["ilo","sc"]:
            obj = IloBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                if obj.clear_cmos(computersystemid="1") == True:
                    return True
                else:
                    return False
            except Exception as ex:
                self._log.error("Bios Default Cmd via BMC-Redfish HPL ILO Failed To Happen {0}".format(ex))
                raise
        try:
            data = {"ResetType": "ForceRestart"}
            data = json.dumps(data)
            url = (r'https://{0}/redfish/v1/Systems/1/Bios/Actions/Bios.ResetBios'.format(self._driver_cfg_model.ip))
            auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
            if (self._session_timer == False):
                reps = requests.post(url, auth=auth1, verify=False, data=data)
            else:
                reps = self.session.post(url, auth=auth1, verify=False, data=data)
            if (reps.status_code != 200):
                self._log.error(
                    "post method response failed for Bios Default Cmd,{0} operation failed".format(reps.status_code))
                return False
            else:
                self._log.debug(
                    " Platform BIOS Factory Restoring Operation functionality Performed via BMC-Redfish Interface")
                self._log.debug("Bios Default Setting Successful {0}".format(reps.content))
                return True
        except Exception as ex:
            self._log.error("Bios Default Cmd via BMC-Redfish Failed To Happen {0}".format(ex))
            raise

    def execute(self, redfish_url=None, redfish_cmd=None):
        """
        : sends command to bmc using ipmi tool
        many user required commands are available in order to perform various functionalities in such cases cmd can be executed using this api.
        :return output of the passed cmd
        :exception
            Error: BMC Redfish Error.
        """
        try:
            self.session = requests.session()
            requests.urllib3.disable_warnings()
            try:
                data = redfish_cmd
                data = json.dumps(data)
            except:
                self._log.debug("No Specific Command Passed")
            default_url = (r"https://{0}/redfish/v1/".format(self._driver_cfg_model.ip))
            auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
            url = default_url + str(redfish_url)
            reps = self.session.post(url, auth=auth1, verify=False, data=data)
            if (reps.status_code != 200):
                self._log.error(
                    "post method response fail with status code,{0} operation failed".format(reps.status_code))
            else:
                self._log.debug(" SUT Reboot functionality Performed via BMC-Redfish Interface")
                self._log.debug("Execution Output {0}".format(reps.content))
                return reps.content
        except Exception as ex:
            self._log.error("Execution Of Given " + str(ipmi_cmd) + " Failed {0}".format(ex))
            raise

    def current_bmc_version_check(self, one_Timer="", bmc_ip=""):
        """
        This API get current bmc frimware Version this is used to identify Current residing bmc frimware image on platform.
        :return output of the current BMC frimware version
        :exception
            Error: BMC Redfish Error.
        """
        if self._driver_cfg_model.bmc_type == "idrac":
            obj = IdracBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                return True, obj.get_bmc_version(managerid="iDRAC.Embedded.1")
            except Exception:
                raise DriverIOError("get bmc version failed.")
        if (one_Timer == True):
            try:
                self.session = requests.session()
                requests.urllib3.disable_warnings()
                url = (r'https://{0}/redfish/v1/Managers/bmc/'.format(bmc_ip))
                auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
                reps = self.session.get(url, auth=auth1, verify=False)
                version = reps.json()['FirmwareVersion']
                self._log.info("BMC Frimware Version {0}".format(version))
                return True, version
            except Exception as ex:
                self._log.error("Failed to Detect Current BMC Flash Version in Chip error >> {0}".format(ex))
                raise
        else:
            try:
                ret = []
                ret = self._driver_cfg_model.ip.split("|")
                for i in range(0, len(ret)):
                    self._log.info("Mentioned BMC IP Address {0}".format(ret[i]))
                    self.session = requests.session()
                    requests.urllib3.disable_warnings()
                    url = (r'https://{0}/redfish/v1/Managers/bmc/'.format(ret[i]))
                    auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
                    reps = self.session.get(url, auth=auth1, verify=False)
                    version = reps.json()['FirmwareVersion']
                    self._log.info("BMC Frimware Version for This ip {0} is {1}".format(ret[i], version))
                return True, version
            except Exception as ex:
                self._log.error("Failed to Detect Current BMC Flash Version in Chip error >> {0}".format(ex))
                raise

    def chip_flash_bmc(self, path=None, image_name=None):
        """
        This function takes care of identifying and erasing and writing a new image from a location.
        it takes the ifwi image or the bmc image based on the modification/creation time it is going to take the lateset time by default of the image.
        Image for flashing will be taken from the "+str(root)+"/firmware/ folder name is frimware from this the image will be taken.
        path in this are fixed path even though folders don't exists it will created it,2nd time run it will copy them
        """
        if self._driver_cfg_model.bmc_type == "idrac":
            obj = IdracBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                return obj.flash_bmc(str(path) + "\\" + str(image_name), self._driver_cfg_model.image_username,
                                     self._driver_cfg_model.image_password, self._driver_cfg_model.transferprotocol)
            except Exception:
                raise DriverIOError("Flash bmc failed.")
        try:
            ret = []
            ret = self._driver_cfg_model.ip.split("|")
            for i in range(0, len(ret)):
                self.current_bmc_version_check(one_Timer=True, bmc_ip=ret[i])
                self._log.info("Before Flashing BMC Firmware Version")
                self.session = requests.session()
                requests.urllib3.disable_warnings()
                url = (r'https://{0}/redfish/v1/UpdateService'.format(ret[i]))
                auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
                image_name = str(path) + "\\" + str(image_name)
                with open(image_name, 'rb') as f:
                    data = f.read()
                reps = self.session.post(url, data=data, auth=auth1, verify=False)
                self._log.debug(reps.status_code)
                if (reps.status_code != 202):
                    self._log.error(
                        "post method response fail with status code,{0} operation failed".format(reps.status_code))
                    return False
                else:
                    self._log.info(" Flashing Image Functionality Successfully Performed via BMC-Redfish Interface")
                    self._log.info("Execution Output {0}".format(reps.content))
            return True
        except Exception as ex:
            self._log.error("Failed to Detect Flash Chip {0}".format(ex))
            raise

    def current_bios_version_check(self, one_Timer="", bios_ip=""):
        """
        This API get current bmc frimware Version this is used to identify Current residing bmc frimware image on platform.
        :return output of the current BMC frimware version
        :exception
            Error: BMC Redfish Error.
        """
        if self._driver_cfg_model.bmc_type == "idrac":
            obj = IdracBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                return True, obj.get_bios_version(computersystemid="System.Embedded.1")
            except Exception:
                raise DriverIOError("get bios version failed.")
        if (one_Timer == True):
            try:
                self.session = requests.session()
                requests.urllib3.disable_warnings()
                url = (r'https://{0}/redfish/v1/Systems/system'.format(bios_ip))
                auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
                reps = self.session.get(url, auth=auth1, verify=False)
                version = reps.json()['BiosVersion']
                self._log.info("Bios Frimware Version {0}".format(version))
                return True, version
            except Exception as ex:
                self._log.error("Failed to Detect Current BIOS Flash Version in Chip error >> {0}".format(ex))
                raise
        else:
            try:
                ret = []
                ret = self._driver_cfg_model.ip.split("|")
                for i in range(0, len(ret)):
                    self._log.info("Mentioned BIOS IP Address {0}".format(ret[i]))
                    self.session = requests.session()
                    requests.urllib3.disable_warnings()
                    url = (r'https://{0}/redfish/v1/Systems/system'.format(ret[i]))
                    auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
                    reps = self.session.get(url, auth=auth1, verify=False)
                    version = reps.json()['BiosVersion']
                    self._log.info("BIOS Frimware Version for This ip {0} is {1}".format(ret[i], version))
                return True, version
            except Exception as ex:
                self._log.error("Failed to Detect Current BIOS Flash Version in Chip error >> {0}".format(ex))
                raise

    def chip_flash_bios(self, path=None, image_name=None):
        """
        This function takes care of identifying and erasing and writing a segment of ifwi, bios image from a location.
        """
        if self._driver_cfg_model.bmc_type == "idrac":
            obj = IdracBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                return obj.flash_bios(str(path) + "\\" + str(image_name), self._driver_cfg_model.image_username,
                                      self._driver_cfg_model.image_password, self._driver_cfg_model.transferprotocol)
            except Exception:
                raise DriverIOError("Flash bios failed.")
        try:
            ret = []
            ret = self._driver_cfg_model.ip.split("|")
            for i in range(0, len(ret)):
                self.current_bios_version_check(one_Timer=True, bios_ip=ret[i])
                self._log.info("Before Flashing BIOS Firmware Version")
                self.session = requests.session()
                requests.urllib3.disable_warnings()
                clear_config_raw_body = json.dumps({"Oem": {"ApplyOptions": {"ClearConfig": True}}})
                url = (r'https://{0}/redfish/v1/UpdateService'.format(ret[i]))
                auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
                image_name = str(path) + "\\" + str(image_name)
                with open(image_name, 'rb') as f:
                    data = f.read()
                try:
                    clear_config = self.session.post('patch', url, data=clear_config_raw_body, auth=auth1, verify=False)
                    if "\"Severity\": \"OK\"" in clear_config.content:
                        self._log.info("Clear Config Done")
                except Exception as ex:
                    self._log.error("Failed to do clear config {0}".format(ex))
                reps = self.session.post(url, data=data, auth=auth1, verify=False)
                self._log.debug(reps.status_code)
                if (reps.status_code != 202):
                    self._log.error(
                        "post method response fail with status code,{0} operation failed".format(reps.status_code))
                    return False
                else:
                    self._log.info(" Flashing Image Functionality Successfully Performed via BIOS-Redfish Interface")
                    self._log.info("Execution Output {0}".format(reps.content))
            return True
        except Exception as ex:
            self._log.error("Failed to Detect Flash Chip {0}".format(ex))
            raise

    def current_cpld_version_check(self, one_Timer="", platform_ip=""):
        """
        This API get current bmc frimware Version this is used to identify Current residing bmc frimware image on platform.
        :return output of the current cpld frimware version
        :exception
            Error: BMC Redfish Error.
        """
        if self._driver_cfg_model.bmc_type == "idrac":
            obj = IdracBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                return True, obj.get_cpld_version(managerid="iDRAC.Embedded.1", dellattributesid="iDRAC.Embedded.1")
            except Exception:
                raise DriverIOError("Get cpld version failed.")
        if (one_Timer == True):
            try:
                self.session = requests.session()
                requests.urllib3.disable_warnings()
                url = (r'https://{0}/redfish/v1/UpdateService/FirmwareInventory/cpld_active'.format(platform_ip))
                auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
                reps = self.session.get(url, auth=auth1, verify=False)
                version = reps.json()['Version']
                self._log.info("CPLD Frimware Version {0}".format(version))
                return True, version
            except Exception as ex:
                self._log.error("Failed to Detect Current CPLD Flash Version >> {0}".format(ex))
                raise
        else:
            try:
                ret = []
                ret = self._driver_cfg_model.ip.split("|")
                for i in range(0, len(ret)):
                    self._log.info("Mentioned Platform IP Address {0}".format(ret[i]))
                    self.session = requests.session()
                    requests.urllib3.disable_warnings()
                    url = (r'https://{0}/redfish/v1/UpdateService/FirmwareInventory/cpld_active'.format(ret[i]))
                    auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
                    reps = self.session.get(url, auth=auth1, verify=False)
                    version = reps.json()['Version']
                    self._log.info("CPLD Frimware Version for This ip {0} is {1}".format(ret[i], version))
                return True, version
            except Exception as ex:
                self._log.error("Failed to Detect Current CPLD Flash Version >> {0}".format(ex))
                raise

    def chip_flash_cpld(self, path=None, image_name=None):
        """
        This function takes care of identifying and erasing and writing a new cpld image from a location.
        """
        if self._driver_cfg_model.bmc_type == "idrac":
            obj = IdracBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                return obj.flash_cpld(str(path) + "\\" + str(image_name), self._driver_cfg_model.image_username,
                                      self._driver_cfg_model.image_password,
                                      self._driver_cfg_model.transferprotocol)
            except Exception:
                raise DriverIOError("Flash cpld failed.")
        try:
            ret = []
            ret = self._driver_cfg_model.ip.split("|")
            for i in range(0, len(ret)):
                self.current_cpld_version_check(one_Timer=True, platform_ip=ret[i])
                self._log.info("Before Flashing CPLD Firmware Version")
                self.session = requests.session()
                requests.urllib3.disable_warnings()
                url = (r'https://{0}/redfish/v1/UpdateService'.format(ret[i]))
                auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
                image_name = str(path) + "\\" + str(image_name)
                with open(image_name, 'rb') as f:
                    data = f.read()
                reps = self.session.post(url, data=data, auth=auth1, verify=False)
                self._log.info(reps.status_code)
                if (reps.status_code != 202):
                    self._log.error(
                        "post method response fail with status code,{0} operation failed".format(reps.status_code))
                    return False
                else:
                    self._log.info(" CPLD Flashing Image Functionality Successfully Performed via Redfish Interface")
                    self._log.info("Execution Output {0}".format(reps.content))
            return True
        except Exception as ex:
            self._log.error("Failed to Flash CPLD Firmware {0}".format(ex))
            raise

    def _redfish_query(self, url_entry):
        self.session = requests.session()
        requests.urllib3.disable_warnings()
        url = url_entry
        auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
        reps = self.session.get(url, auth=auth1, verify=False)
        print(reps)
        return reps

    def _redfish_patch(self, url_entry, data):
        self.session = requests.session()
        requests.urllib3.disable_warnings()
        url = url_entry
        auth1 = (r"debuguser", r"0penBmc1")
        print(json.dumps(data))
        reps = self.session.patch(url, auth=auth1, verify=False, data=json.dumps(data))
        print(reps)
        return reps

    def read_voltages(self):
        response = self._redfish_query(r"https://{}/redfish/v1/Chassis".format(self._driver_cfg_model.ip))
        ret_dict = response.json()
        for r in ret_dict[r"Members"]:
            for v in r.values():
                if v and v.find("Baseboard") != -1:
                    response = self._redfish_query(r"https://{}{}/Power".format(self._driver_cfg_model.ip, r[r"@odata.id"]))
                    voltages = response.json()[r"Voltages"]
                    ret = dict()
                    for volt in voltages:
                        ret[volt["Name"]] = volt["ReadingVolts"]
                    return ret

    def get_boot_device(self):
        response = self._redfish_query(r"https://{}/redfish/v1/Systems/system".format(self._driver_cfg_model.ip))
        ret_dict = response.json()
        return ret_dict[r"Boot"]["BootSourceOverrideTarget"]

    def select_boot_device(self, boot_device):
        data = {"Boot": {"BootSourceOverrideEnabled": "Once",
                             "BootSourceOverrideTarget": boot_device}}
        response = self._redfish_patch(r"https://{}/redfish/v1/Systems/system".format(self._driver_cfg_model.ip),data=data)
        return response.status_code in (200, 204)

    def read_volt(self):
        try:
            self.session = requests.session()
            requests.urllib3.disable_warnings()
            try:
                url = (
                    r'https://{0}/redfish/v1/Chassis/AC_Baseboard/Power#/Voltages/0'.format(self._driver_cfg_model.ip))
                auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
                reps = self.session.get(url, auth=auth1, verify=False)
            except Exception as ex:
                self._log.error("Redfish AC_baseboard is Different on this Platform Trying Alternative Approach")
                url = (
                    r'https://{0}/redfish/v1/Chassis/BC_Baseboard/Power#/Voltages/0'.format(self._driver_cfg_model.ip))
                auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
                reps = self.session.get(url, auth=auth1, verify=False)
            version = reps.json()
            self._log.debug(json.dumps(version, indent=4, sort_keys=True))
            for volt in version['Voltages']:
                if (volt['Name'] == "P3V3"):
                    fp_volt = volt['ReadingVolts']
                    if not fp_volt:
                        fp_volt = 0
                if (volt['Name'] == "P3VBAT"):
                    dc_volt = volt['ReadingVolts']
                    break
            self._log.info("P3V3 {0}  P3VBAT {1}".format(fp_volt, dc_volt))
            version = [fp_volt, dc_volt]
            return True, version
        except Exception as ex:
            self._log.error("Failed to Get Volt Value >> {0}".format(ex))
            raise

    def platform_postcode(self):
        if self._driver_cfg_model.bmc_type == "idrac":
            obj = IdracBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                data=obj.get_postcode(managerid="iDRAC.Embedded.1", dellattributesid="iDRAC.Embedded.1")
                return True,data
                #return True, obj.get_postcode(managerid="iDRAC.Embedded.1", dellattributesid="iDRAC.Embedded.1")
            except Exception:
                raise DriverIOError("get postcode failed.")
        try:
            self.session = requests.session()
            requests.urllib3.disable_warnings()
            url = (
                r'https://{0}/redfish/v1/Systems/system/LogServices/PostCodes/Entries'.format(
                    self._driver_cfg_model.ip))
            auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
            reps = self.session.get(url, auth=auth1, verify=False)
            postcode = reps.json()
            self._log.debug(json.dumps(postcode, indent=4, sort_keys=True))
            pst = json.dumps(postcode)
            data = json.loads(pst)
            print(type(data['Members']))
            pst_data = ""
            for i in data['Members']:
                self._log.info(i['Message'])
                pst_data += i['Message']
            pst_data = pst_data.split('\n')
            if isinstance(pst_data, list):
                import re
                m = re.search("POST Code:\W*(0x[a-e0-9]+)", pst_data[0])
                if m:
                    return True, m.groups()[0]
            return True, pst_data
        except Exception as ex:
            self._log.error("Reading Postcode via BMC-Redfish Failed To Happen {0}".format(ex))
            raise

    def set_bios_category_bootorder(self, first_boot=""):
        if self._driver_cfg_model.bmc_type == "idrac":
            obj = IdracBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                return obj.change_bootorder(bootorder=first_boot, FunctionEnabled=True, TimeoutAction=None,
                                            computersystemid="System.Embedded.1")
            except Exception:
                raise DriverIOError("change bootorder failed.")
        if self._driver_cfg_model.bmc_type == "ilo":
            obj = IloBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                ret=obj.change_bootorder(bootorder=first_boot, FunctionEnabled=True, TimeoutAction=None,
                                            computersystemid="1")
                if (ret == True):
                    self._log.info("Boot Order Device List {0} Set Successfully".format(first_boot))
                    return True
                else:
                    return False
            except Exception as ex:
                self._log.error("BOOT Order Set via ILO Failed To Happen {0}".format(ex))
                raise
        try:
            self.session = requests.session()
            requests.urllib3.disable_warnings()
            if not first_boot:
                self._log.error(
                    "First BOOT Order Tag is not passed \"Pxe\",\"Hdd\",\"Cd\",\"Diags\",\"BiosSetup\",\"Usb\"")
                return False
            data = {"Boot": {"BootSourceOverrideEnabled": "Continuous",
                             "BootSourceOverrideTarget": "" + str(first_boot) + ""}}
            data = json.dumps(data)
            # print(data)
            url = (
                r'https://{0}/redfish/v1/Systems/system'.format(self._driver_cfg_model.ip))
            auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
            reps = self.session.patch(url, auth=auth1, verify=False, data=data)
            if (reps.status_code != 204):
                self._log.error(
                    "post method failed to Set First Boot order Tag,{0} operation failed".format(reps.status_code))
            else:
                self._log.info("First Boot Order Tag Set Successfully")
                return True
        except Exception as ex:
            self._log.error("Setting First boot Order Tag Failed To Happen {0}".format(ex))
            raise

    def get_bios_category_bootorder(self):
        if self._driver_cfg_model.bmc_type == "idrac":
            obj = IdracBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                return obj.get_bootorder(computersystemid="System.Embedded.1")
            except Exception:
                raise DriverIOError("Get bootorder failed.")
        if self._driver_cfg_model.bmc_type == "ilo":
            obj = IloBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                ret=obj.get_bootorder(computersystemid="1")
                if (ret[0] == True):
                    self._log.info("Boot Order Device List {0}".format(ret[1]))
                    return True
                else:
                    return False
            except Exception as ex:
                self._log.error("Faield to Get Boot Order List via BMC-Redfish HPL ILO {0}".format(ex))
                raise
        try:
            self.session = requests.session()
            requests.urllib3.disable_warnings()
            url = (
                r'https://{0}/redfish/v1/Systems/system'.format(self._driver_cfg_model.ip))
            auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
            reps = self.session.patch(url, auth=auth1, verify=False)
            postcode = reps.json()
            self._log.debug(json.dumps(postcode, indent=4, sort_keys=True))
            pst = json.dumps(postcode)
            data = json.loads(pst)
            self._log.info(type(data['Boot']))
            pst_data = ""
            for i in data['Boot']:
                self._log.info(i['BootSourceOverrideTarget@Redfish.AllowableValues'])
                pst_data += i['BootSourceOverrideTarget@Redfish.AllowableValues']
            pst_data = pst_data.split('\n')
            if (reps.status_code != 204):
                self._log.error(
                    "post method failed to Get First Boot order Tag,{0} operation failed".format(reps.status_code))
            else:
                self._log.info("Get First Boot Order Successful")
                return True
        except Exception as ex:
            self._log.error("Setting First boot Order Tag Failed To Happen {0}".format(ex))
            raise

    def _get_baseboard_odataid(self):
        response = self._redfish_query(r"https://{}/redfish/v1/Chassis".format(self._driver_cfg_model.ip))
        ret_dict = response.json()
        for r in ret_dict[r"Members"]:
            for v in r.values():
                if v and v.find("Baseboard") != -1:
                    return r[r"@odata.id"]

    def get_system_info(self):
        try:
            odataid = self._get_baseboard_odataid()
            print(odataid)
            ret = self._redfish_query(r"https://{}{}".format(self._driver_cfg_model.ip, odataid))
            data = ret.json()
            chassis_type = (data['ChassisType'])
            Manufacturer = (data['Manufacturer'])
            Model = (data['Model'])
            PartNumber = (data['PartNumber'])
            SerialNumber = (data['SerialNumber'])
            try:
                url = (
                    r'https://{0}/redfish/v1/Systems/system'.format(self._driver_cfg_model.ip))
                auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
                if (self._session_timer == False):
                    reps = requests.get(url, auth=auth1, verify=False)
                else:
                    reps = self.session.get(url, auth=auth1, verify=False)
            except Exception as ex:
                self._log.error("Getting System UUID Failed To Happen {0}".format(ex))
                raise
            data = reps.json()
            for i in data:
                UUID = (data['UUID'])
                break
            self._log.info(
                "Chassis_Type {0} , Manufacturer {1} , Model {2} ,PartNumber {3}, SerialNumber {4} ,UUID {5}".format(
                    chassis_type, Manufacturer, Model, PartNumber, SerialNumber, UUID))
            data = chassis_type, Manufacturer, Model, PartNumber, SerialNumber, UUID
            return True, data
        except Exception as ex:
            self._log.error("Failed To Get System Details Via REDFISH BMC To Happen {0}".format(ex))
            return False

    def get_system_status_led(self):
        g = "Green"
        ab = "Amber Blink"
        r = "Amber"
        try:
            self.session = requests.session()
            requests.urllib3.disable_warnings()
            url = (
                r'https://{0}/redfish/v1/Systems/system'.format(self._driver_cfg_model.ip))
            auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
            reps = self.session.get(url, auth=auth1, verify=False)
        except Exception as ex:
            self._log.error("Getting System Indicator Status LED Failed To Happen {0}".format(ex))
            raise
        data = reps.json()
        for i in data:
            mem_IndicatorLED = (data['MemorySummary'])
            processor_IndicatorLED = (data['ProcessorSummary'])
            overall_IndicatorLED = (data['Status'])
            break
        for i in mem_IndicatorLED:
            memory_health = mem_IndicatorLED['Status']['Health'].lower()
            processor_health = processor_IndicatorLED['Status']['Health'].lower()
            overall_health = overall_IndicatorLED['Health'].lower()
            break

        print(memory_health, processor_health, overall_health)
        if (memory_health == "ok"):
            mem_status_Led = g
        elif (memory_health == "warning"):
            mem_status_Led = ab
        elif (memory_health == "critical"):
            mem_status_Led = r
        else:
            self._log.error("Unexpected Value For Memory LED Status")
        if (processor_health == "ok"):
            processor_health = g
        elif (processor_health == "warning"):
            processor_health = ab
        elif (processor_health == "critical"):
            processor_health = r
        else:
            self._log.error("Unexpected Value For PROCESSOR LED Status")
        if (overall_health == "ok"):
            overall_health = g
        elif (overall_health == "warning"):
            overall_health = ab
        elif (overall_health == "critical"):
            overall_health = r
        else:
            self._log.error("Unexpected Value For Overall Platform LED Status")
        led = (str(mem_status_Led), (processor_health), (overall_health))
        self._log.info(
            "MemoryLED_Status --> {0} , ProcessorLED_Status --> {1} , Overalll PLatform Status --> {2}".format(
                mem_status_Led, processor_health, overall_health))
        return True, led

    def insert_virtual_media(self, image, username, password, transfermethod, transferprotocoltype, inserted,
                             writeprotected):
        if self._driver_cfg_model.bmc_type == "idrac":
            obj = IdracBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
            try:
                return obj.insert_virtual_media(username, password, image, transfermethod, transferprotocoltype,
                                                inserted,
                                                writeprotected, managerid="iDRAC.Embedded.1",
                                                virtualmediaid="RemovableDisk")
            except Exception:
                raise DriverIOError("Insert virtual media failed.")
        self.session = requests.session()
        requests.urllib3.disable_warnings()
        try:
            url = (r'https://{0}/redfish/v1/Managers/bmc/VirtualMedia/Slot_3/Actions/VirtualMedia.InsertMedia'.format(self._driver_cfg_model.ip))
            auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
            data = {'Image': image, 'TransferProtocolType': 'HTTPS', 'UserName': username,
                    'Password': password}
            data = json.dumps(data)
            header = {'Content-type': 'application/json'}
            reps = self.session.post(url, auth=auth1, verify=False, headers=header, data=data)
            print(reps.status_code)
            if (reps.status_code == 200):
                self._log.info("Media Mount from Artifactory location IS successfull")
                return True,reps.status_code
            else:
                self._log.error("Error Media Mount Unsuccessfull from ATF")
                return False,reps.status_code
        except Exception as ex:
            self._log.error("Getting System Info Failed To Happen {0}".format(ex))
            raise

    def eject_virtual_media(self):
        if self._driver_cfg_model.bmc_type == "idrac":
            obj = IdracBmc(self._driver_cfg_model.ip, self._driver_cfg_model.username, self._driver_cfg_model.password)
        else:
            self.session = requests.session()
            requests.urllib3.disable_warnings()
            try:
                url = (
                    r'https://{0}/redfish/v1/Managers/bmc/VirtualMedia/Slot_3/Actions/VirtualMedia.EjectMedia'.format(self._driver_cfg_model.ip))
                auth1 = (self._driver_cfg_model.username, self._driver_cfg_model.password)
                data = {}
                data = json.dumps(data)
                header = {'Content-type': 'application/json'}
                reps = self.session.post(url, auth=auth1, verify=False,headers=header, data=data)
                self._log.info("Status Operation Response Code {0}".format(reps.status_code))
                if (reps.status_code == 200):
                    self._log.info("Media unmount Successfull from Artifactory location")
                    return True,reps.status_code
                else:
                    self._log.error("Unable to unMount Media From Given Artifactory Location")
                    return False,reps.status_code
            except Exception:
                raise DriverIOError("eject virtual media failed.")

    def get_platform_bmc_mac(self):
        ret=self._driver_cfg_model.bmc_mac

        if(ret == None):
            self._log.error("NO BMC MAC ID is Entered Manually in the System Configuration File")
            return False,"N/A"
        else:
            self._log.info("Entered BMC MAC ID {0}".format(ret))
            return True,ret
