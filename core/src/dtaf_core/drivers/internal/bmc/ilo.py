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
import json
import requests


class IlORequestError(Exception):
    pass


class IloServerError(Exception):
    pass


class IloUnexceptedException(Exception):
    pass


class IloBmc:
    def __init__(self, ip, username, password):
        requests.urllib3.disable_warnings()
        self.session = requests.session()
        self.session.headers['Content-Type'] = 'application/json'
        self.__ip = ip
        self.__username = username
        self.__password = password

    def dc_power_on(self, computersystemid):
        payload = {'ResetType': 'On'}
        headers = {'content-type': 'application/json'}
        url = (r'https://{0}/redfish/v1/Systems/{1}/Actions/ComputerSystem.Reset'.format(self.__ip, computersystemid))
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False,
                                 auth=(self.__username, self.__password))
        ret = response.content
        op = ["success", "power is on"]
        if any(x in str(ret).lower() for x in op):
            return True
        else:
            return False

    def dc_power_off(self, computersystemid):
        payload = {'ResetType': 'ForceOff'}
        headers = {'content-type': 'application/json'}
        url = (r'https://{0}/redfish/v1/Systems/{1}/Actions/ComputerSystem.Reset'.format(self.__ip,computersystemid))
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False,
                                 auth=(self.__username, self.__password))
        ret = response.content
        op = ["success", "power is off"]
        if any(x in str(ret).lower() for x in op):
            return True
        else:
            return False

    def dc_power_state(self, computersystemid):
        headers = {'content-type': 'application/json'}
        url = (r'https://{0}/redfish/v1/Systems/{1}'.format(self.__ip, computersystemid))
        reps = requests.get(url, data=None, headers=headers, verify=False,
                            auth=(self.__username, self.__password))
        b = reps.json()
        if (str(b["PowerState"]).find("On") != -1):
            flag = "On"
        elif (str(b["PowerState"]).find("Off") != -1):
            flag = "Off"
        return flag

    def dc_power_reset(self, computersystemid):
        payload = {'ResetType': 'ForceRestart'}
        headers = {'content-type': 'application/json'}
        url = (r'https://{0}/redfish/v1/Systems/{1}/Actions/ComputerSystem.Reset'.format(self.__ip, computersystemid))
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False,
                                 auth=(self.__username, self.__password))
        ret = response.content
        op = ["power is off"]
        op1 = ["success"]
        if any(x in str(ret).lower() for x in op):
            return "power off"
        elif any(x in str(ret).lower() for x in op1):
            return True

    def clear_cmos(self, computersystemid):
        data = {"ResetType": "ForceRestart"}
        headers = {'content-type': 'application/json'}
        url = (r'https://{0}/redfish/v1/Systems/{0}/Bios/Actions/Bios.ResetBios'.format(self.__ip, computersystemid))
        response = requests.post(url, data=json.dumps(data), headers=headers, verify=False,
                                 auth=(self.__username, self.__password))
        if (repsonse.status_code != 200):
            self._log.error(
                "post method response failed for Bios Default Cmd,{0} operation failed".format(response.status_code))
            return False
        else:
            self._log.debug(
                " Platform BIOS Factory Restoring Operation functionality Performed via BMC-Redfish Interface")
            self._log.info("Bios Default Setting Successful {0}".format(response.content))
            return True

    def get_bmc_version(self):
        raise NotImplementedError

    def flash_bmc(self, imageURI, username, password, transferprotocol):
        raise NotImplementedError

    def flash_bios(self, imageURI, username, password, transferprotocol):
        raise NotImplementedError

    def flash_cpld(self, imageURI, username, password, transferprotocol):
        raise NotImplementedError

    def get_bios_version(self):
        raise NotImplementedError

    def get_cpld_version(self):
        raise NotImplementedError

    def get_postcode(self):
        raise NotImplementedError

    def change_bootorder(self, bootorder, FunctionEnabled, TimeoutAction, computersystemid):
        headers = {'content-type': 'application/json'}
        if not bootorder or not isinstance(bootorder, list):
            raise AttributeError("Wrong data format.")
        data = {"Boot": {"BootOrder": bootorder},
                "HostWatchdogTimer": {"FunctionEnabled": FunctionEnabled, "TimeoutAction": TimeoutAction}}
        data = json.dumps(data)
        url = r'https://{0}/redfish/v1/Systems/{1}'.format(self.__ip, computersystemid)
        try:
            reps = request.patch(url,data=data, headers=headers,auth=(self.__username, self.__password), verify=False)
            if (reps.status_code != 200):
                self._log.error(
                    "PATCH To set Boot Order Failed,{0} operation failed".format(response.status_code))
                return False
            else:
                return True
        except Exception as ex:
            self._log.error("Failed to Change the BOOT Order {0}".format(ex))
            raise

    def get_bootorder(self, computersystemid):
        headers = {'content-type': 'application/json'}
        url = (r'https://{0}/redfish/v1/Systems/{1}'.format(self.__ip, computersystemid))
        reps = requests.get(url,data=None, headers=headers, verify=False,auth=(self.__username, self.__password))
        if(reps.status_code != 200):
            self._log.error(
                "get method failed to get boot order,{0} operation failed".format(response.status_code))
            return False
        else:
            return True,reps.json()["Boot"]["BootOrder"]

    def insert_virtual_media(self):
        raise NotImplementedError

    def eject_virtual_media(self):
        raise NotImplementedError
