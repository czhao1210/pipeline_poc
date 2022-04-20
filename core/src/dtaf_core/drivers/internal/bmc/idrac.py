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


class IdracRequestError(Exception):
    pass


class IdracServerError(Exception):
    pass


class IdracUnexceptedException(Exception):
    pass


def check_status(status):
    if str(status)[0] in ["2"]:
        return
    elif str(status)[0] in ["4"]:
        raise IdracRequestError("Status: %s, request error." % (str(status)))
    elif str(status)[0] in ["5", "6"]:
        raise IdracServerError("Status: %s, server failure." % (str(status)))
    else:
        raise IdracUnexceptedException("Status: %s, unknown error." % (str(status)))


class IdracBmc:
    def __init__(self, ip, username, password):
        requests.urllib3.disable_warnings()
        self.session = requests.session()
        self.session.headers['Content-Type'] = 'application/json'
        self.__ip = ip
        self.__username = username
        self.__password = password

    def dc_power_on(self, computersystemid):
        data = {"ResetType": "On"}
        data = json.dumps(data)
        url = r'https://{0}/redfish/v1/Systems/{1}/Actions/ComputerSystem.Reset'.format(
            self.__ip, computersystemid)
        auth1 = (self.__username, self.__password)
        reps = self.session.post(url, auth=auth1, verify=False, data=data)
        check_status(reps.status_code)
        return True

    def dc_power_off(self, computersystemid):
        data = {"ResetType": "ForceOff"}
        data = json.dumps(data)
        url = r'https://{0}/redfish/v1/Systems/{1}/Actions/ComputerSystem.Reset'.format(
            self.__ip, computersystemid)
        auth1 = (self.__username, self.__password)
        reps = self.session.post(url, auth=auth1, verify=False, data=data)
        check_status(reps.status_code)
        return True

    def dc_power_state(self, computersystemid):
        url = r'https://{0}/redfish/v1/Systems/{1}'.format(self.__ip, computersystemid)
        auth1 = (self.__username, self.__password)
        reps = self.session.get(url, auth=auth1, verify=False)
        check_status(reps.status_code)
        return reps.json()['PowerState']

    def dc_power_reset(self, computersystemid):
        data = {"ResetType": "ForceRestart"}
        data = json.dumps(data)
        url = r'https://{0}/redfish/v1/Systems/{1}/Actions/ComputerSystem.Reset'.format(
            self.__ip, computersystemid)
        auth1 = (self.__username, self.__password)
        reps = self.session.post(url, auth=auth1, verify=False, data=data)
        check_status(reps.status_code)
        return True

    def clear_cmos(self, computersystemid):
        data = {}
        data = json.dumps(data)
        url = r'https://{0}/redfish/v1/Systems/{1}/Bios/Actions/Bios.ResetBios'.format(
            self.__ip, computersystemid)
        auth1 = (self.__username, self.__password)
        reps = self.session.post(url, auth=auth1, verify=False, data=data)
        check_status(reps.status_code)
        return True

    def get_bmc_version(self, managerid):
        url = r'https://{0}/redfish/v1/Managers/{1}'.format(self.__ip, managerid)
        auth1 = (self.__username, self.__password)
        reps = self.session.get(url, auth=auth1, verify=False)
        check_status(reps.status_code)
        return reps.json()["FirmwareVersion"]

    def flash_bmc(self, imageURI, username, password, transferprotocol):
        data = {"ImageURI": imageURI, "Username": username, "Password": password, "TransferProtocol": transferprotocol}
        pop_list = []
        for key in data.keys():
            if data[key] is None:
                pop_list.append(key)
        for key in pop_list:
            data.pop(key)
        data = json.dumps(data)
        url = r'https://{0}/redfish/v1/UpdateService/Actions/UpdateService.SimpleUpdate'.format(
            self.__ip)
        auth1 = (self.__username, self.__password)
        reps = self.session.post(url, auth=auth1, verify=False, data=data)
        check_status(reps.status_code)
        return True

    def flash_bios(self, imageURI, username, password, transferprotocol):
        data = {"ImageURI": imageURI, "Username": username, "Password": password, "TransferProtocol": transferprotocol}
        pop_list = []
        for key in data.keys():
            if data[key] is None:
                pop_list.append(key)
        for key in pop_list:
            data.pop(key)
        data = json.dumps(data)
        url = r'https://{0}/redfish/v1/UpdateService/Actions/UpdateService.SimpleUpdate'.format(
            self.__ip)
        auth1 = (self.__username, self.__password)
        reps = self.session.post(url, auth=auth1, verify=False, data=data)
        check_status(reps.status_code)
        return True

    def flash_cpld(self, imageURI, username, password, transferprotocol):
        data = {"ImageURI": imageURI, "Username": username, "Password": password, "TransferProtocol": transferprotocol}
        pop_list = []
        for key in data.keys():
            if data[key] is None:
                pop_list.append(key)
        for key in pop_list:
            data.pop(key)
        data = json.dumps(data)
        url = r'https://{0}/redfish/v1/UpdateService/Actions/UpdateService.SimpleUpdate'.format(
            self.__ip)
        auth1 = (self.__username, self.__password)
        reps = self.session.post(url, auth=auth1, verify=False, data=data)
        check_status(reps.status_code)
        return True

    def get_bios_version(self, computersystemid):
        url = r'https://{0}/redfish/v1/Systems/{1}'.format(self.__ip, computersystemid)
        auth1 = (self.__username, self.__password)
        reps = self.session.get(url, auth=auth1, verify=False)
        check_status(reps.status_code)
        return reps.json()['BiosVersion']

    def get_cpld_version(self, managerid, dellattributesid):
        url = r'https://{0}/redfish/v1/Managers/{1}/Oem/Dell/DellAttributes/{2}'.format(
            self.__ip, managerid, dellattributesid)
        auth1 = (self.__username, self.__password)
        reps = self.session.get(url, auth=auth1, verify=False)
        check_status(reps.status_code)
        return reps.json()["Attributes"]["Info.1.CPLDVersion"]

    def get_postcode(self, managerid, dellattributesid):
        url = r'https://{0}/redfish/v1/Managers/{1}/Oem/Dell/DellAttributes/{2}'.format(
            self.__ip, managerid, dellattributesid)
        auth1 = (self.__username, self.__password)
        reps = self.session.get(url, auth=auth1, verify=False)
        check_status(reps.status_code)
        return reps.json()["Attributes"]["SysInfo.1.POSTCode"]

    def change_bootorder(self, bootorder, FunctionEnabled, TimeoutAction, computersystemid):
        if not bootorder or not isinstance(bootorder, list):
            raise AttributeError("Wrong data format.")
        data = {"Boot": {"BootOrder": bootorder},
                "HostWatchdogTimer": {"FunctionEnabled": FunctionEnabled, "TimeoutAction": TimeoutAction}}
        data = json.dumps(data)
        url = r'https://{0}/redfish/v1/Systems/{1}'.format(self.__ip, computersystemid)
        auth1 = (self.__username, self.__password)
        reps = self.session.patch(url, auth=auth1, verify=False, data=data)
        check_status(reps.status_code)
        return True

    def get_bootorder(self, computersystemid):
        url = r'https://{0}/redfish/v1/Systems/{1}'.format(self.__ip, computersystemid)
        auth1 = (self.__username, self.__password)
        reps = self.session.get(url, auth=auth1, verify=False)
        check_status(reps.status_code)
        return reps.json()["Boot"]["BootOrder"]

    def insert_virtual_media(self, username, password, image, transfermethod, transferprotocoltype, inserted,
                             writeprotected, managerid, virtualmediaid):
        if not image:
            raise AttributeError("Image is required.")
        data = {"Image": image, "inserted": inserted, "Password": password, "TransferMethod": transfermethod,
                "TransferProtocolType": transferprotocoltype, "UserName": username,
                "WriteProtected": writeprotected}
        pop_list = []
        for key in data.keys():
            if data[key] is None:
                pop_list.append(key)
        for key in pop_list:
            data.pop(key)
        data = json.dumps(data)
        url = r'https://{0}/redfish/v1/Managers/{1}/VirtualMedia/{2}/Actions/VirtualMedia.InsertMedia'.format(
            self.__ip, managerid, virtualmediaid)
        auth1 = (self.__username, self.__password)
        reps = self.session.post(url, auth=auth1, verify=False, data=data)
        check_status(reps.status_code)
        return True

    def eject_virtual_media(self, managerid, virtualmediaid):
        data = {}
        data = json.dumps(data)
        url = r'https://{0}/redfish/v1/Managers/{1}/VirtualMedia/{2}/Actions/VirtualMedia.EjectMedia'.format(
            self.__ip, managerid, virtualmediaid)
        auth1 = (self.__username, self.__password)
        reps = self.session.post(url, auth=auth1, verify=False, data=data)
        check_status(reps.status_code)
        return True
