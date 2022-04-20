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

import mock
from dtaf_core.providers.internal.usbblaster_physical_control_provider import UsbblasterPhysicalControlProvider
from xml.etree import ElementTree as ET
import pytest


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


log = _Log()
cfg_opts = ET.fromstring("""
            <usbblaster>
                            <cpld_application_path>C:\intelFPGA_pro\\18.1\qprogrammer\\bin64\</cpld_application_path>
                            <primary_image_path>C:\cpld_frimware\</primary_image_path>
                            <primary_image_name>main.pof</primary_image_name>
                            <secondary_image_path>C:\cpld_frimware\</secondary_image_path>
                            <secondary_image_name>second.pof</secondary_image_name>
                            <driver>
                                <usbblaster>
                                    <cpld_application_path>C:\intelFPGA_pro\\18.1\qprogrammer\\bin64\</cpld_application_path>
                                    <primary_image_path>C:\cpld_frimware\</primary_image_path>
                                    <primary_image_name>main.pof</primary_image_name>
                                    <secondary_image_path>C:\cpld_frimware\</secondary_image_path>
                                    <secondary_image_name>second.pof</secondary_image_name>
                                </usbblaster>
                            </driver>
                        </usbblaster>
""")


class TestSshSutOsProvider(object):
    @staticmethod
    def test_connect_usb_to_sut():
        with UsbblasterPhysicalControlProvider(log=log, cfg_opts=cfg_opts) as obj:
            try:
                obj.connect_usb_to_sut()
            except NotImplementedError:
                pass

    @staticmethod
    def test_connect_usb_to_host():
        with UsbblasterPhysicalControlProvider(log=log, cfg_opts=cfg_opts) as obj:
            try:
                obj.connect_usb_to_host()
            except NotImplementedError:
                pass

    @staticmethod
    def test_disconnect_usb():
        with UsbblasterPhysicalControlProvider(log=log, cfg_opts=cfg_opts) as obj:
            try:
                obj.disconnect_usb()
            except NotImplementedError:
                pass

    @staticmethod
    def test_set_clear_cmos():
        with UsbblasterPhysicalControlProvider(log=log, cfg_opts=cfg_opts) as obj:
            try:
                obj.set_clear_cmos()
            except NotImplementedError:
                pass

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.usbblaster_physical_control_provider.DriverFactory')
    def test_read_postcode(mocker):
        with UsbblasterPhysicalControlProvider(log=log, cfg_opts=cfg_opts) as obj:
            try:
                obj.read_postcode()
            except NotImplementedError:
                pass

    @staticmethod
    def test_read_s3_pin():
        with UsbblasterPhysicalControlProvider(log=log, cfg_opts=cfg_opts) as obj:
            try:
                obj.read_s3_pin()
            except NotImplementedError:
                pass

    @staticmethod
    def test_read_s4_pin():
        with UsbblasterPhysicalControlProvider(log=log, cfg_opts=cfg_opts) as obj:
            try:
                obj.read_s4_pin()
            except NotImplementedError:
                pass

    @staticmethod
    def test_program_jumper():
        with UsbblasterPhysicalControlProvider(log=log, cfg_opts=cfg_opts) as obj:
            try:
                obj.program_jumper('aaa', 'aaa')
            except NotImplementedError:
                pass

    @staticmethod
    def test_get_power_state():
        with UsbblasterPhysicalControlProvider(log=log, cfg_opts=cfg_opts) as obj:
            try:
                obj.get_power_state()
            except NotImplementedError:
                pass
