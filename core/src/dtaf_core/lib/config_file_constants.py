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


class ConfigFileParameters(object):
    """
    Base config file parameters.
    """

    # System host information
    HOST = "./host"
    # Host OS information
    HOST_OS = "host/os"
    ATTR_HOST_OS_NAME = "name"
    ATTR_HOST_OS_VERSION = "version"
    HOST_KERNEL = "./host/os/kernel"
    ATTR_HOST_KERNEL_VERSION = "version"

    # SUT information
    SUTS = "./suts"
    SUT = "./suts/sut"
    # SUT debug information
    SUT_DEBUG = "./silicon_debug"
    ATTR_SUT_DEBUG_TYPE = "type"
    # SUT OS information
    SUT_OS_INFO = "./os"
    SUT_OS_CREDS = "./credentials"
    SUT_OS_NET_PROTOCOL = "./network/protocol"
    SUT_OS_NET_IPV4 = "./ipv4"
    ATTR_SUT_OS_TYPE = "name"
    ATTR_SUT_OS_SUBTYPE = "subtype"
    ATTR_SUT_OS_VERSION = "version"
    ATTR_SUT_OS_KERNEL = "kernel"
    # Attrib of deployment
    ATTR_DEPLOYMENT_USER = "user"
    ATTR_DEPLOYMENT_PASSWORD = "password"

    # Deployment Provider Configuration
    XML_PATH_TO_DOWNLOAD_CRED = r"download/repo/credentials"
    XML_PATH_TO_LOCAL_ROOT = r"download/package_path"

    # AC Power Provider Configuration
    XML_PATH_TO_POWER_OFF_TIMEOUT = r"timeout/power_off"
    XML_PATH_TO_POWER_ON_TIMEOUT = r"timeout/power_on"

    # Physical control
    XML_PATH_TO_USB_SWITCH_TIMEOUT = r"timeout/usbswitch"
    XML_PATH_TO_CLEAR_CMOS_TIMEOUT = r"timeout/clearcmos"

    # soundwave2k
    XML_PATH_TO_THREHOLDS_MAIN_LOW = r"voltagethreholds/main_power/low"
    XML_PATH_TO_THREHOLDS_MAIN_HIGH = r"voltagethreholds/main_power/high"
    XML_PATH_TO_THREHOLDS_DSW_LOW = r"voltagethreholds/dsw/low"
    XML_PATH_TO_THREHOLDS_DSW_HIGH = r"voltagethreholds/dsw/high"
    XML_PATH_TO_THREHOLDS_MEM_LOW = r"voltagethreholds/memory/low"
    XML_PATH_TO_THREHOLDS_MEM_HIGH = r"voltagethreholds/memory/high"

    # raspberrypi
    XML_PATH_TO_AC_GPIO_PHASE = r"raspberrypi/ac_gpio_phase"
    XML_PATH_TO_AC_GPIO_NEUTRAL = r"raspberrypi/ac_gpio_neutral"
    XML_PATH_TO_AC_DETECTION_GPIO = r"raspberrypi/ac_detection_gpio"
    XML_PATH_TO_DC_POWER_GPIO = r"raspberrypi/dc_power_gpio"
    XML_PATH_TO_REBOOT_GPIO = r"raspberrypi/reboot_gpio"
    XML_PATH_TO_DC_DETECTION_GPIO = r"raspberrypi/dc_detection_gpio"
    XML_PATH_TO_CLEAR_CMOS_GPIO = r"raspberrypi/clear_cmos_gpio"
    XML_PATH_TO_USB_SWITCH_PHASE = r"raspberrypi/usb_switch_phase"
    XML_PATH_TO_USB_SWITCH_DATAPOS = r"raspberrypi/usb_switch_datapos"
    XML_PATH_TO_USB_SWITCH_DATANEG = r"raspberrypi/usb_switch_dataneg"
    XML_PATH_TO_S3_DETECTION_GPIO = r"raspberrypi/s3_detection_gpio"
    XML_PATH_TO_S4_DETECTION_GPIO = r"raspberrypi/s4_detection_gpio"
    XML_PATH_TO_RASPBERRYPI_IP= r"raspberrypi/raspberrypi_ip"

    # cscripts silicon reg provider
    SILICON_REG = "./silicon_reg"
    XML_PATH_TO_SILICON_REG_DEBUG_TYPE = r"debugger_interface_type"
    XML_PATH_TO_SILICON_UNLOCKER = r"unlocker"
    XML_PATH_TO_SILICON_CPU_FAMILY = r"silicon/cpu_family"
    XML_PATH_TO_SILICON_PCH_FAMILY = r"silicon/pch_family"

    # EM100 FlashProviderConfig
    ATTR_CHIP = "chip"
    ATTR_USB_PORTS = "usb_ports"
    ATTR_FLASH_DEVICE_NAME = "name"

    # pdu
    XML_PATH_TO_OUTLETS = r"outlet"
