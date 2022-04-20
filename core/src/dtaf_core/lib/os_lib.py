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
from __future__ import print_function
import six
from dtaf_core.lib.registry import MetaRegistry


class LinuxDistributions(object):
    ClearLinux = "ClearLinux"
    Fedora = "Fedora"
    SLES = "SLES"
    RHEL = "RHEL"
    Ubuntu = "Ubuntu"
    CentOS = "CentOS"


# Map of /etc/os-release ID to DTAF references
os_rel_map = {
    "clear-linux-os": LinuxDistributions.ClearLinux,
    "rhel": LinuxDistributions.RHEL,
    "ubuntu": LinuxDistributions.Ubuntu
}


class OsCommandResult(object):

    """Class that represents the result of running an operating system command."""

    def __init__(self, return_code, stdout, stderr):
        """
        Returns a new OsCommandResult object.

        :param return_code: Integer representing the exit code of the process.
        :param stdout: String containing all stdout of the executed process.
        :param stderr: String containing all stderr of the executed process.
        """
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr

    def cmd_failed(self):
        # type: () -> bool
        """
        Check if command failed based on return code (non-zero = fail).

        :return: True if command failed, False otherwise.
        """
        return self.return_code != 0

    def cmd_passed(self):
        # type: () -> bool
        """
        Check if command passed based on return code (zero = pass).

        :return: True if command passed, False otherwise.
        """
        return self.return_code == 0


@six.add_metaclass(MetaRegistry)
class Linux(object):
    """Container of constants for use with any Linux distribution."""
    BOOT_DIR = "/boot/"
    TEMP_DIR = "/tmp/"
    GRUB_CFG = "grub.cfg"
    ETC_GRUB_D_DIR = "/etc/grub.d/"
    GRUB_CONFIG_DIR = "/boot/grub/"

    class Commands(object):
        SHUTDOWN = "echo shutdown && sleep 5 && init 0 &"
        RESTART = "echo restarting && sleep 3 && reboot &"
        SHUTDOWN_RESTART = "shutdown -r &"


class RHEL(Linux):
    """Container of constants for use with Red Hat Enterprise Linux."""
    GRUB_CONFIG_DIR = "/boot/efi/EFI/redhat/"


class Fedora(Linux):
    """Container of constants for use with Fedora Linux."""
    GRUB_CONFIG_DIR = "/boot/efi/EFI/fedora/"


class SLES(Linux):
    """Container of constants for use with SUSE Enterprise Linux."""
    GRUB_CONFIG_DIR = "/boot/efi/efi/sles/"


class ClearLinux(Linux):
    """Container of constants for use with Clear Linux."""
    GRUB_CONFIG_DIR = None  # Clear doesn't use GRUB, force failure of TCs that need this


@six.add_metaclass(MetaRegistry)
class Windows(object):
    """Container of constants for use with Microsoft Windows."""

    class Commands(object):
        SHUTDOWN = "shutdown /f /s /t 0"
        RESTART = "shutdown /r /t 0"


@six.add_metaclass(MetaRegistry)
class ESXi(object):
    """Container of constants for use with VMWare ESXi."""
    class Commands(object):
        SHUTDOWN = "poweroff"
        RESTART = "reboot"


if __name__ == "__main__":
    # Demo of how OS constants work
    print("To use a ConstantContainer for OS constants, put common constants in the class matching the name of the")
    print("OS from ptv_constants.OperatingSystems. For constants that change depending on the subtype (for example,")
    print("Red Hat Linux vs Ubuntu), make it a subclass of the OS type and override common constants/add subtype")
    print("specific constants as necessary")
    print("You can make a constant reference generic by using the get_subtype_cls function of a ConstantContainer.")
    print("This will take a string and give you the subclass with the matching name.")
    print("For example, lets say you want a data structure with Linux constants. You can get this by calling")
    print("Linux.get_subtype_cls(\"RHEL\")")
    print("You can even override get_subtype_cls to customize how the subclass is found! For example, you could concat")
    print("the product name to get different constants for different products.")
    print("For example, here is the GRUB_CONFIG_DIR constant for Linux (generic), RHEL, and SLES.")
    rhel = Linux.get_subtype_cls("RHEL")
    sles = Linux.get_subtype_cls("SLES")
    print("Linux = " + Linux.GRUB_CONFIG_DIR)
    print("RHEL = " + rhel.GRUB_CONFIG_DIR)
    print("SLES = " + sles.GRUB_CONFIG_DIR)
    print("If you want to error out when the subtype class doesn't exist, there is a parameter called strict. If it")
    print("is set to False, it will just return the generic class. If it is True, it will raise an exception.")
    print("FAKE_LINUX doesn't exist, but calling Linux.get_subtype_cls(\"FAKE_LINUX\", False) won't fail.")
    print("Instead, it returns Linux, assuming that the subtype in use is one it has no knowledge of.")
    fake = Linux.get_subtype_cls("FAKE_LINUX", False)
    print("Fake = " + fake.GRUB_CONFIG_DIR)
    print("Fake is a " + str(fake))
