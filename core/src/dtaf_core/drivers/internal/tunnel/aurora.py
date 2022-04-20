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


class TunnelRequestError(Exception):
    pass


class TunnelServerError(Exception):
    pass


class TunnelUnexpectedError(Exception):
    pass


def check_status(status):
    if str(status)[0] in ["2"]:
        return
    elif str(status)[0] in ["4"]:
        raise TunnelRequestError("Status: %s, request error." % (str(status)))
    elif str(status)[0] in ["5", "6"]:
        raise TunnelServerError("Status: %s, server failure." % (str(status)))
    else:
        raise TunnelUnexpectedError("Status: %s, unknown error." % (str(status)))


class AuroraBMC:
    def __init__(self, bmc_address, username, password):
        requests.urllib3.disable_warnings()
        self.session = requests.session()
        self.session.headers['Content-Type'] = 'application/json'
        self.__bmc_addr = bmc_address
        self.__username = username
        self.__password = password

    def turn_on_bmc(self, blade):
        data = {"ResetType": "On"}
        data = json.dumps(data)
        url = f"https://{self.__bmc_addr}/redfish/v1/Chassis/{blade}/Actions/Chassis.Reset"
        auth1 = (self.__username, self.__password)
        try:
            reps = self.session.post(url, auth=auth1, verify=False, data=data)
            check_status(reps.status_code)
        except Exception as ex:
            return False
        return True

    def turn_off_bmc(self, blade):
        data = {"ResetType": "Off"}
        data = json.dumps(data)
        url = f"https://{self.__bmc_addr}/redfish/v1/Chassis/{blade}/Actions/Chassis.Reset"
        auth1 = (self.__username, self.__password)
        try:
            reps = self.session.post(url, auth=auth1, verify=False, data=data)
            check_status(reps.status_code)
        except Exception as ex:
            return False
        return True

    def get_bmc_power_state(self, blade):
        url = f"https://{self.__bmc_addr}/redfish/v1/"
        auth1 = (self.__username, self.__password)
        try:
            reps = self.session.get(url, auth=auth1, verify=False)
            check_status(reps.status_code)
        except Exception as ex:
            return False
        return True

class AuroraSUT:
    def __init__(self, bmc_address, username, password):
        requests.urllib3.disable_warnings()
        self.session = requests.session()
        self.session.headers['Content-Type'] = 'application/json'
        self.__bmc_addr = bmc_address
        self.__username = username
        self.__password = password

    def dc_power_on(self):
        data = {"ResetType": "ForceOn"}
        data = json.dumps(data)
        url = f"https://{self.__bmc_addr}/redfish/v1/Systems/system/Actions/ComputerSystem.Reset"
        auth1 = (self.__username, self.__password)
        try:
            reps = self.session.post(url, auth=auth1, verify=False, data=data)
            check_status(reps.status_code)
        except Exception as ex:
            return False
        return True

    def dc_power_off(self):
        data = {"ResetType": "ForceOff"}
        data = json.dumps(data)
        url = f"https://{self.__bmc_addr}/redfish/v1/Systems/system/Actions/ComputerSystem.Reset"
        auth1 = (self.__username, self.__password)
        try:
            reps = self.session.post(url, auth=auth1, verify=False, data=data)
            check_status(reps.status_code)
        except Exception as ex:
            return False
        return True

    def get_dc_power_state(self):
        url = f"https://{self.__bmc_addr}/redfish/v1/Systems/system/"
        auth1 = (self.__username, self.__password)
        reps = self.session.get(url, auth=auth1, verify=False)
        try:
            check_status(reps.status_code)
        except Exception as ex:
            return False
        b = reps.json()
        c = b["PowerState"]
        return c.lower() == "on"

    def is_bmc_alive(self):
        url = f"https://{self.__bmc_addr}/redfish/v1/Systems/system/"
        auth1 = (self.__username, self.__password)
        try:
            reps = self.session.get(url, auth=auth1, verify=False)
            check_status(reps.status_code)
        except Exception as ex:
            return False
        return True



# aurora = AuroraSUT(bmc_address=r"localhost:5443", username="admin", password="initial0")
# ret = aurora.get_dc_power_state()
# print(ret)
# aurora.turn_on_bmc(blade="Blade2")
#aurora.dc_power_on()
