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

import urllib.request

import requests
import xml.dom.minidom
from dtaf_core.lib.private.provider_config.deployment_provider_config import DeploymentProviderConfig
from dtaf_core.providers.deployment import DeploymentProvider
from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.drivers.internal.onebkc_driver import OnebkcDriver
import os


class OnebkcDeploymentProvider(DeploymentProvider):
    def __enter__(self):
        return super(OnebkcDeploymentProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(OnebkcDeploymentProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def __init__(self, cfg_opts, log):
        self._config_model = None # type: DeploymentProviderConfig
        self.__driver = DriverFactory.create(cfg_opts=cfg_opts.find("driver/*"), logger=log)  # type: OnebkcDriver
        super(OnebkcDeploymentProvider, self).__init__(cfg_opts, log)

    def download(self, package_url):
        filename = os.path.basename(package_url)
        dest = os.path.join(self._config_model.local_root, filename)
        self.__download(src_url=package_url,
                        dest_path=self._config_model.local_root,
                        user=self._config_model.repo_user,
                        password=self._config_model.repo_password)
        return dest

    def get_ingredient_info(self, kit_path, kit_name, ingredient_name):
        manifest_url = "/".join((kit_path, "Documents", "{}.xml".format(kit_name)))
        manifest = self.__download(
                        manifest_url,
                        self._config_model.local_root,
                        self._config_model.repo_user,
                        self._config_model.repo_password)
        return self.__driver.parse_ingredient_info_from_manifest(manifest=manifest, ingredient_name=ingredient_name)

    def __download(self, src_url, dest_path, user, password):
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        base_name = os.path.basename(src_url)
        dest = os.path.join(dest_path, base_name)

        passwdmgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

        passwdmgr.add_password(None, src_url, user, password)

        handler = urllib.request.HTTPBasicAuthHandler(passwdmgr)

        opener = urllib.request.build_opener(handler)

        urllib.request.install_opener(opener)

        request = urllib.request.Request(src_url)

        request.get_method = lambda: 'HEAD'

        response = opener.open(request)

        url_total = response.headers['content-length']

        try:
            f = urllib.request.urlopen(src_url)
            outf = open(dest, 'wb')
            c = 0
            while True:
                s = f.read(1024 * 32)
                if len(s) == 0:
                    break
                print('CURRENT PROGRESS: %.2f%%\r' % (100.0 * c / int(url_total)))
                outf.write(s)
                c += len(s)
            outf.close()
            print("ok")
        except Exception as ex:
            print("no")
            return ""
        return dest

    def get_device_property(self, name):
        try:
            return self._cfg.find("device/{}".format(name)).text.strip()
        except AttributeError as error:
            self._log.warn(error)
            return ""




