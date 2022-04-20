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
import pytest
from time import sleep
from dtaf_core.lib.os_lib import OsCommandResult
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.provider_factory import ProviderFactory
from xml.etree import ElementTree as ET
import time
from dtaf_core.providers.physical_control import PhysicalControlProvider


class _Log(object):
    @classmethod
    def debug(cls, msg):
        print(msg)

    @classmethod
    def info(cls, msg):
        print(msg)

    @classmethod
    def warning(cls, msg):
        print(msg)

    @classmethod
    def error(cls, msg):
        print(msg)

    @classmethod
    def critical(cls, msg):
        print(msg)

    warn = warning
    fatal = critical


log = _Log()



class PhysicalTest(object):
    def __init__(self):
        bioscfg = ET.fromstring(
            """
            <physical_control>
                <driver>
                    <redfish>
                        <ip>10.239.181.138</ip>
                        <username>debuguser</username>
                        <password>0penBmc1</password>
                    </redfish>
                </driver>
                <timeout>
                    <usbswitch>4</usbswitch>
                    <clearcmos>3</clearcmos>>
                </timeout>
            </physical_control>
            """
        )
        self.phys = ProviderFactory.create(bioscfg, log)  # type:PhysicalControlProvider

    def test_physicalcontrol(self):
        self.verify_postcode()
        self.verify_voltages()
        self.verify_led()
        print("PASSED")

    def verify_postcode(self):
        print("get post code={}".format(self.phys.read_postcode()))

    def verify_voltages(self):
        print("get voltages={}".format(self.phys.get_voltages(None)))
        print("PASSED")


    def verify_led(self):
        print("get health={}".format(self.phys.platform_health_status()))
        print("PASSED")
PhysicalTest().test_physicalcontrol()
