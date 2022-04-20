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


class OperatingSystems(object):
    """Container/enum for operating systems supported to some degree by the framework"""
    # Most commonly used OSes for DPV server/workstation validation.
    WINDOWS = "Windows"
    LINUX = "Linux"
    ESXI = "ESXi"

    # OSes that have been POR on various server/workstation products but not widely included in DPV validation
    # (for now). No guarantee of support for these from providers and libraries, but if future content needs them,
    # the constants will be here.
    BSD = "BSD"
    MACOS = "MacOS"
    VXWORKS = "VxWorks"


class PowerState(object):
    AC_ON = "On"
    AC_OFF = "Off"
    S0 = "S0"
    S3 = "S3"
    S4 = "S4"
    S5 = "S5"
    G3 = "G3"
    Unknown = "Unknown"


class DebuggerInterfaceTypes(object):
    """Container/enum for supported hardware debugger interface types"""
    ITP = "ITP"
    OPENIPC = "IPC"
    INBAND = "inband"
    NONE = "None"


class PlatformTypes(object):
    """Container/enum for supported platform types"""
    COMMERCIAL = "commercial"
    REFERENCE = "reference"
    OXM = "oxm"


class ProductFamilies(object):
    """Container/enum for supported product families"""
    SKX = "SKX"  # Skylake-X
    SKM = "SKM"  # Sky Meadow
    CLX = "CLX"  # Cascadelake-X
    ICX = "ICX"  # Icelake-X
    SNR = "SNR"  # Snow Ridge/Jacobsville
    BDX = "BDX"  # Broadwell-X
    JKT = "JKT"  # Jaketown/Sandy Bridge
    IVT = "IVT"  # Ivytown/Ivy Bridge-EX
    CPX = "CPX"  # Cooperlake-X
    SPR = "SPR"  # Saphire Rapids
    SPRHBM = "SPRHBM"  #Saphire Rapids HBM
    ICXD = "ICXD"  # Icelake-X desktop
    RKL = "RKL"  # Tatlow/Rocket Lake
    GNR = "GNR"  #Granite Rapids

class MemoryTypes(object):
    """Container/enum for supported memory types"""
    DDR3 = "ddr3"
    DDR4 = "ddr4"
    DDR5 = "ddr5"
    DDRT = "ddrt"
    DDRT2 = "ddrt2"

# Base paths for the framework. Set outside of the class to prevent scoping issues.
_CFG_BASE = {OperatingSystems.WINDOWS: "C:\\Automation\\", OperatingSystems.LINUX: "/opt/Automation/", OperatingSystems.ESXI:"C:\\Automation\\" }

class Framework(object):
    """Container of constants related to the framework/infrastructure"""
    # Framework core constants
    TEST_RESULT_PASS = 0
    TEST_RESULT_FAIL = 1
    DEFAULT_AUTOMATION_USER = "root"
    DEFAULT_AUTOMATION_PASSWORD = "password"
    BMC_USER = "root"
    BMC_PASSWORD = "superuser"
    RESULT_FAILURE_REASON_FILE = "result_failure_reason.json"

    class ExecutionStyles(object):
        """Container/enum for execution style definitions"""
        LOCAL = "local"
        REMOTE = "remote"
        RACKSCALE = "rackscale"
        SIMICS = "simics"
        SUPPORTED_STYLES = [LOCAL, REMOTE, RACKSCALE, SIMICS]

    # Base paths for configuration files. This is pulled in from an external reference due to scoping issues.
    CFG_BASE = _CFG_BASE

    # Paths to configuration files for each supported OS.
    CFG_FILE_PATH = {os: _CFG_BASE[os] + "system_configuration.xml"
                     for os in [OperatingSystems.WINDOWS, OperatingSystems.LINUX, OperatingSystems.ESXI]}

    class LogLevel(object):
        """Enum for setting the log level"""
        DEBUG = "debug"
        INFO = "info"
        WARNING = "warning"
        ERROR = "error"
        EXCEPTION = "exception"
