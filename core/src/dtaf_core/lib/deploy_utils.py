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
import subprocess
import os
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.provider_factory import ProviderFactory
from dtaf_core.providers.deployment import DeploymentProvider


class Deployment(object):
    def __init__(self, cfg_opts, logger):
        self.__cfg_opts = cfg_opts
        self.__logger = logger

    def provision(self, image_path, image_type, os_type, ingredients, software_path, timeout=5000):
        """
        Take Image, Software Package, Ingredient Information for OS Provisionning

        Currently it works on Whitley with soundwave control box. OS Installation will start at UEFIShell. In furture, Pxe will be supported.

        :param image_path: full path of OS image on ATF or local drive. If image type is integrated, it will include software package as well. Otherwise, it is supposed to be pure OS image.
        :param image_type: integrated / non-integrated. integrated indicates image is pure OS.
        :param os_type: Linux/Windows/VMWare
        :param ingredients: tuple of dictionary {name, path}. ingredients will be downloaded and update to SUT.
        :param software_path: full path of software package on ATF or local driver
        :param timeout: max time for provisioning

        :return: True / False
        """
        folder = os.path.dirname(os.path.abspath(__file__))
        script = os.path.join(folder, "private", "provision", "os_installation.py")
        sut_config = ConfigurationHelper.get_sut_config(self.__cfg_opts)
        deployment_cfg = ConfigurationHelper.get_provider_config(sut_config, "deployment")
        deploy = ProviderFactory.create(deployment_cfg, self.__logger) # type: DeploymentProvider
        image_loc = image_path
        if image_path.startswith("http"):
            image_loc = deploy.download(image_path)
        sw_loc = software_path
        if software_path.startswith("http"):
            sw_loc = deploy.download(software_path)
        usb_device_name = deploy.get_device_property("usb")
        harddisk_device_name = deploy.get_device_property("harddisk")
        command = [
            script, "--INITIALIZE_OS_PACKAGE", "True",
            "--LOCAL_OS_PACKAGE_MODE", "True",
            "--LOCAL_OS_PACKAGE_LOCATION", "\"" + image_loc + "\"",
            "--OSTYPE", "linux",
            "--INITIALIZE_SOFTWARE_PACKAGE", "true",
            "--LOCAL_SOFTWARE_PACKAGE_MODE", "true",
            "--LOCAL_SOFTWARE_PACKAGE_LOCATION", "\"" + sw_loc + "\"",
           #"--USB_SIZE", "16",
            "--USB_DEVICE_NAME", usb_device_name,
            "--HARDISK_DEVICE_NAME", harddisk_device_name
        ]
        ifwi_loc = "ifwi.zip"
        for ing in ingredients:
            for k, v in ing.items():
                if "IFWI" == k:
                    ifwi_loc = v
        ifwi_cmd = ["--ENABLEFLASHING no --LOCAL_IFWI_PACKAGE_MODE no --LOCAL_IFWI_IMG_PATH", "\"" + ifwi_loc + "\""]
        command.extend(ifwi_cmd)
        proc = subprocess.Popen("python " + " ".join(command))
        proc.wait(timeout)
        return True
