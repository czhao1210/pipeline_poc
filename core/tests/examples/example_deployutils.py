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
"""
This is an example of RSC2 implemented AC Power Control Provider
"""

import sys
from xml.etree import ElementTree as eTree

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.deployment import DeploymentProvider
from dtaf_core.providers.provider_factory import ProviderFactory
from dtaf_core.lib.deploy_utils import Deployment
from xml.etree import ElementTree as ET

class DeploySystemTest(BaseTestCase):
    """
    Basic test case demonstrating the use of FlashProvider.

    Add the IFWI file you want to use to the working directory as IFWI.bin.
    This example test assumes 32MB flash and
    that the SUT is already powered-on and booted to the OS.
    This is designed to be triggered manually,
    and as such, is not marked as a system test for py test to pick up.
    """

    def __init__(self, test_log, arguments, cfg_opts):
        super(DeploySystemTest, self).__init__(test_log, arguments, cfg_opts)
        root = ET.parse("tests/system/data/provision_configuration.xml").getroot()
        sut_config = ConfigurationHelper.get_sut_config(root)
        deploy_cfg = ConfigurationHelper.get_provider_config(sut_config, "deployment")
        # self.__deploy = ProviderFactory.create(deploy_cfg, test_log)  # type: DeploymentProvider
        self.__deploy = Deployment(cfg_opts=root, logger=test_log)

    def verify_deploy(self):
        """
        This is the function to verify ac functionality of rsc2
        :return: None
        """
        # ret = self.__deploy.get_ingredient_info(kit_path=r"https://ubit-artifactory-sh.intel.com/artifactory/dcg-dea-srvplat-local/Kits/ICX-SRV-RHEL/ICX-SRV-RHEL-20.24.2.10483/",
        #                                   kit_name=r"ICX-SRV-RHEL-20.24.2.10483",
        #                                   ingredient_name="IFWI")
        #
        # ret = self.__deploy.download("https://ubit-artifactory-sh.intel.com/artifactory/owr-repos/Kits/ICX-SRV-RHEL/ICX-SRV-RHEL-20.24.2.10483/Firmware/IFWI/15.D85-v3/IFWI_15.D85.zip")
        # ret = self.__deploy.download("https://ubit-artifactory-or.intel.com/artifactory/one-windows-kits-local/BRMSTest/ICX-SRV-RHEL/ICX-SRV-RHEL-20.24.3.10751/Images/8.1.0-20191015.0-x86_64_ICX-SRV-RHEL-20.24.3.10751.zip")

        # print(self.__deploy.get_device_property("usb"))
        # print(self.__deploy.get_device_property("harddisk"))
        # print(ret)
        self.__deploy.provision(image_path=r"temp\\8.1.0-20191015.0-x86_64_ICX-SRV-RHEL-20.24.3.10751.zip",
                                image_type=r"integrated", os_type="Linux",
                                ingredients=(), software_path="swpath")
        # self._deploy.provision(
        #     image_path=r"https://ubit-artifactory-or.intel.com/artifactory/one-windows-kits-local/BRMSTest/ICX-SRV-ESXI/ICX-SRV-ESXI-20.16.6.5567/Images/ESXi_7.0.0-15525992.x86_64_ICX-SRV-ESXI-20.16.6.5567.zip",
        #     image_type="non-integrated",
        #     os_type="Linux",
        #     ingredients=(dict(name="IFWI", path="")),
        #     software_path=r"https://ubit-artifactory-or.intel.com/artifactory/one-windows-kits-local/BRMSTest/ICX-SRV-ESXI/ICX-SRV-ESXI-20.16.6.5567/Images/ICX-SRV-ESXI-20.16.6.5567_SWpackage.zip")

    def execute(self):
        """
        The entry of Test Case.
        :return:
        """
        self.verify_deploy()
        return True


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if DeploySystemTest.main() else Framework.TEST_RESULT_FAIL)
