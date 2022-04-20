#!/usr/bin/env python
#################################################################################
# INTEL CONFIDENTIAL
# Copyright Intel Corporation All Rights Reserved.
#
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material may contain trade secrets and proprietary
# and confidential information of Intel Corporation and its suppliers and
# licensors, and is protected by worldwide copyright and trade secret laws and
# treaty provisions. No part of the Material may be used, copied, reproduced,
# modified, published, uploaded, posted, transmitted, distributed, or disclosed
# in any way without Intel's prior express written permission.
#
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
#################################################################################

import xml
from collections import defaultdict

import xmltodict
from xml.etree.ElementTree import Element, tostring

from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig


class SimicsDriverConfig(BaseDriverConfig):
    extra_attr = defaultdict(dict)

    def __init__(self, cfg_opts, log):
        super(SimicsDriverConfig, self).__init__(cfg_opts, log)
        cfg_dict = dict(cfg_opts)
        if xml.etree.ElementTree.iselement(cfg_opts):
            cfg_dict = xmltodict.parse(tostring(cfg_opts))
        self.__serial_port = int(cfg_dict["simics"]["serial_port"])
        try:
            self.__host = cfg_dict["simics"]["host"]["name"]
        except KeyError as e:
            self.__host = "localhost"
        if self.__host != "localhost":
            self.__host_port = int(cfg_dict["simics"]["host"]["port"])
            self.__host_username = cfg_dict["simics"]["host"]["username"]
            self.__host_password = cfg_dict["simics"]["host"]["password"]
        else:
            self.__host_port = -1
            self.__host_username = ""
            self.__host_password = ""
        try:
            self.__mode_real_time = bool(cfg_dict["simics"]["mode"]["real-time"])
        except Exception as ex:
            pass
        self.__mode_real_time = False
        self.__service_port = int(cfg_dict["simics"]["service_port"])

        self.__app = cfg_dict["simics"]["app"]
        self.__project = cfg_dict["simics"]["project"]
        self.__script = cfg_dict["simics"]["script"]
        self.__simics_os = cfg_dict["simics"].get('os')
        self.__simics_network = cfg_dict['simics'].get('network')
        if self.__simics_network:
            self.__dhcp_pool_ip = self.__simics_network.get('dhcp_pool_ip') or '192.168.1.150'
            try:
                self.__network_user = self.__simics_network['user']
                self.__network_password = self.__simics_network['password']
            except KeyError as ex:
                raise AttributeError('Xml config is Error')
        else:
            self.__network_user = 'root'
            self.__network_password = None
            self.__dhcp_pool_ip = None

        self._retry_cnt = cfg_dict["simics"].get("retry_cnt") or 1

    @property
    def mode_real_time(self):
        return self.__mode_real_time

    @property
    def serial_port(self):
        return self.__serial_port

    @property
    def service_port(self):
        return self.__service_port

    @property
    def host(self):
        return self.__host

    @property
    def app(self):
        return self.__app

    @property
    def project(self):
        return self.__project

    @property
    def script(self):
        return self.__script

    @property
    def host_port(self):
        return self.__host_port

    @property
    def host_username(self):
        return self.__host_username

    @property
    def host_password(self):
        return self.__host_password

    @property
    def dhcp_pool_ip(self):
        return self.__dhcp_pool_ip

    @property
    def simics_os(self):
        return self.__simics_os

    @property
    def network_password(self):
        return self.__network_password

    @property
    def network_user(self):
        return self.__network_user

    @property
    def simics_network(self):
        return self.__simics_network

    @property
    def retry_cnt(self):
        return self._retry_cnt

    @property
    def os_port(self):
        return self.extra_attr.get(f'{self.host}:{self.host_port}')['os_port']
