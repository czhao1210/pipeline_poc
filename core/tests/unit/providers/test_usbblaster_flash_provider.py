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

from xml.etree import ElementTree as ET

import pytest
from dtaf_core.providers.internal.usbblaster_flash_provider import UsbblasterFlashProvider


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
    @pytest.mark.parametrize('target_value',
                             ['cpld1', 'cpld2', ''])
    def test_flash_image(target_value):
        with UsbblasterFlashProvider(log=log, cfg_opts=cfg_opts) as obj:
            try:
                obj.flash_image(target=target_value)
            except:
                pass
            try:
                obj.flash_image(target=target_value, path='aaa', image_name='aaa')
            except:
                pass

    @staticmethod
    def test_chip_identify():
        with UsbblasterFlashProvider(log=log, cfg_opts=cfg_opts) as obj:
            try:
                obj.chip_identify()
            except NotImplementedError:
                pass

    @staticmethod
    def test_read():
        with UsbblasterFlashProvider(log=log, cfg_opts=cfg_opts) as obj:
            try:
                obj.read()
            except NotImplementedError:
                pass

    @staticmethod
    def test_write():
        with UsbblasterFlashProvider(log=log, cfg_opts=cfg_opts) as obj:
            try:
                obj.write()
            except NotImplementedError:
                pass

    @staticmethod
    def test_current_bmc_version_check():
        with UsbblasterFlashProvider(log=log, cfg_opts=cfg_opts) as obj:
            try:
                obj.current_bmc_version_check()
            except NotImplementedError:
                pass

    @staticmethod
    def test_flash_image_bmc():
        with UsbblasterFlashProvider(log=log, cfg_opts=cfg_opts) as obj:
            try:
                obj.flash_image_bmc()
            except NotImplementedError:
                pass

    @staticmethod
    def test_current_bios_version_check():
        with UsbblasterFlashProvider(log=log, cfg_opts=cfg_opts) as obj:
            try:
                obj.current_bios_version_check()
            except NotImplementedError:
                pass
