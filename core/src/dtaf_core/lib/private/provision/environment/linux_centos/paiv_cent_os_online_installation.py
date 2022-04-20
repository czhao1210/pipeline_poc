"""
#Author Suresh Sakthi

version 1.0 05-june-2020 :- Created Os Installation Script

"""
import re
import os
import six
import sys
import time
import glob
import ntpath
import os.path
import zipfile
import platform
import subprocess
from os import path
from subprocess import Popen, PIPE, STDOUT
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.providers.flash_provider import FlashProvider
from dtaf_core.providers.sut_os_provider import SutOsProvider
from dtaf_core.providers.bios_menu import BiosBootMenuProvider
from dtaf_core.providers.ac_power import AcPowerControlProvider
from dtaf_core.providers.bios_menu import BiosSetupMenuProvider
from dtaf_core.providers.provider_factory import ProviderFactory
from dtaf_core.providers.physical_control import PhysicalControlProvider
from src.environment.os_prerequisites import OsPreRequisitesLib


class Os_Installation(BaseTestCase):
    def __init__(self, test_log, arguments, cfg_opts):
        super(Os_Installation, self).__init__(test_log, arguments, cfg_opts)
        flash_cfg = cfg_opts.find(FlashProvider.DEFAULT_CONFIG_PATH)
        self._flash = ProviderFactory.create(flash_cfg, test_log)
        ac_cfg = cfg_opts.find(AcPowerControlProvider.DEFAULT_CONFIG_PATH)
        self._ac = ProviderFactory.create(ac_cfg, test_log)
        phy_cfg = cfg_opts.find(PhysicalControlProvider.DEFAULT_CONFIG_PATH)
        self._phy = ProviderFactory.create(phy_cfg, test_log)
        sut_os_cfg = cfg_opts.find(SutOsProvider.DEFAULT_CONFIG_PATH)
        self._os = ProviderFactory.create(sut_os_cfg, test_log)
        self._os_pre_req_lib = OsPreRequisitesLib(test_log, cfg_opts)
        setupmenu_cfg = cfg_opts.find(BiosSetupMenuProvider.DEFAULT_CONFIG_PATH)
        self.setupmenu = ProviderFactory.create(setupmenu_cfg, test_log)
        bootmenu_cfg = cfg_opts.find(BiosBootMenuProvider.DEFAULT_CONFIG_PATH)
        self.bootmenu = ProviderFactory.create(bootmenu_cfg, test_log)
        self.os_params = self._os_pre_req_lib.get_sut_inventory_data("centos")
        self._imagetype = arguments.IMAGETYPE  # ignore without os
        self._os_install = arguments.only_os_install  # for flashing ifwi image alone

        self._atf_username = arguments.atf_user
        self._atf_password = arguments.atf_password

        # self._ostype = arguments.OSTYPE
        self._ostype = "RHEL"
        self._basepath = arguments.BASEPATH

        self._enable_ifwi_flashing = arguments.ENABLE_IFWI_FLASHING
        self._ifwipath = arguments.IFWIPATH
        self._ifwifile = arguments.IFWIFILE

        self._driverpkgpath = arguments.DRIVERPKGPATH  # sft_path
        self._driverfile = arguments.DRIVERFILE  # sft_filename

        self._imagepath = arguments.OS_IMAGEPATH
        self._imagefile = arguments.OS_IMAGEFILE

        # download and extract the image
        # self._ifwi_dnd_extract = arguments.img_dnd_extract    #True or Flase by default True
        self._direct_ifwi_pkg_download = arguments.direct_ifwi_download  # whether to download ifwi from ATF given by user #True or False
        self._direct_atf_ifwi_path = arguments.atf_ifwi_path  # full atf ifwi_pkg path along with file name extension usually .zip
        # target location where it needs to be copied
        self._local_ifwi_host_mode = arguments.pre_downloaded_ifwi_pkg_mode
        self._local_ifwi_host_path = arguments.ifwi_img_dwnd_host_path  # In this passed location ifwi package resides pre-downloaded
        # host machine is linux or Windows
        self._host = arguments.host
        self._format_pendrive = arguments.format_pendrive
        if arguments.usb_size is None:
            self._usb_size = self.os_params[1]
        else:
            self._usb_size = arguments.usb_size
        self._curl_server = arguments.curl_server

        # software package
        self._initialize_sft_pkg = True  # True or Flase to initialize software package
        self._direct_sft_pkg_download = True  # whether to download os image given by user #True or False
        self._direct_sft_img_path = arguments.atf_sft_pkg_path  # full atf software_pkg path along with file name extension
        self._usr_given_local_sft_mode = arguments.pre_downloaded_sft_pkg_mode  # local drive #True or by default none
        self._local_drive_sft_pkg = arguments.pre_downloaded_sft_local_location  # path is from Local location in hostmachine #full path to be given Also With FileName # where the .zip sft pkg is present in local drive

        # os package
        self._initialize_os_pkg = True  # True  to initialize os package download or further choose reuse
        self._direct_os_download = True # whether to download os image given by user #True by default none
        self._direct_os_img_path = arguments.atf_baseos_path  # full atf os location path along with file name extension
        self._usr_given_local_os_mode = arguments.pre_downloaded_os_pkg_mode  # local drive #True or by default none
        self._local_drive_os_pkg = arguments.pre_downloaded_os_pkg_location  # path in location computer the hostmachine #full path to be given Also With FileName # where the .zip os img is present in local drive

        # extraction
        self._extract_sft_package = arguments.extract_sft_package_to_usb
        self._extract_os_package = arguments.extract_os_package_to_usb

        # bios
        if arguments.usb_drive_name is None:
            self._usb_drive_name = self.os_params[0]  # USB Device Name from Which OS Needed To Be Installed From
        else:
            self._usb_drive_name = arguments.usb_drive_name

        ########## New code starts -- Navee

        if self._usb_drive_name:
            usb_new = ""
            usb_split = self._usb_drive_name.split()
            for word in usb_split:
                if len(word) > 16:
                    usb_new = usb_new + "[\s\S]*"
                    break
                else:
                    usb_new = usb_new + " " + word

            self._usb_drive_name = usb_new.strip()

        if self._usb_drive_name is None:
            self._usb_drive_name = self.os_params[0]

        self._log.info("Shows the usb name is a Regex or direct name --> {}".format(self._usb_drive_name))

        ########## New code Ends -- Navee

        if arguments.hardisk_drive_name is None:
            self._hardisk_drive_name = self.os_params[2]  # name of the Hard Disk in Which Os Needs To Be Loaded
        else:
            self._hardisk_drive_name = arguments.hardisk_drive_name
        self._bios_path = arguments.boot_order_change_path  # Bios Path To Change Boot-Order "xxxx,xxx,xxx"
        self._boot_select_path = arguments.boot_select_path  # Select Boot Path For Selecting USB Drive "xxxx,xxx,xxx"
        self._save_knob_name = arguments.save_knob_path  # Select Boot Path For Selecting USB Drive "xxxx,xxx,xxx"

        ##automation enabler
        self._rhel_cfg_file_name = arguments.post_os_automation_enabler_rhel
        self._centos_cfg_file_name = arguments.post_os_automation_enabler_centos

        self._boot_select_path += "," + str(self._usb_drive_name)

    def prepare(self):
        # validation on IFWI package mode
        if ((str(self._local_ifwi_host_mode)).lower() in ["true", "yes", "on", "enable"]):
            self._local_ifwi_host_mode = True
            if (self._local_ifwi_host_mode and self._direct_ifwi_pkg_download):
                self._log.error(
                    "Either Already Available Package or Newly Download From Artifactory Either one option can be Made True")
                return False
            if not self._local_ifwi_host_path:
                self._log.error("Give In The lOCATION OF Pre-Downloaded ifwi ZIP LOCATION")
                return False

        if ((str(self._direct_ifwi_pkg_download)).lower() in ["true", "yes", "on", "enable"]):
            self._direct_ifwi_pkg_download = True
            if not self._direct_atf_ifwi_path:
                self._log.error("Give Artifactory Location of Ifwi ZIP url")
                return False

        # validation on software package mode
        if (self._initialize_sft_pkg):
            if (self._direct_sft_pkg_download and self._usr_given_local_sft_mode):
                self._log.error(
                    "Either Already Available Package or Newly Download From Artifactory Either one option can be Made True")
                return False
        if (self._initialize_os_pkg):
            if (self._direct_os_download and self._usr_given_local_os_mode):
                self._log.error(
                    "Either Already Available OS Package in Local Drive or Newly Download From Artifactory Either one option can be Made True")
                return False
        if not self._ostype:
            self._log.error("Do Mention Which OS --OSTYPE you are trying to Download for more info --help")
            return False
        if ((str(self._ostype)).lower() in ["rhel", "rhel-8.1", "rhel8.1", "linux", "centos", "fedora", "suseos",
                                            "ubuntu", "oss_windows", "without_os"]):
            self._ostype = "Linux"
        if ((str(self._ostype)).lower() in ["wim", "windows_wim", "win", "windows", "windwos2019", "windows_serveros"]):
            self._ostype = "Windows_Wim"
        if ((str(self._ostype)).lower() in ["vm_os", "vmware", "esxi", "hypervisor"]):
            self._ostype = "ESXI"
        self._stf_pkg_name = "sft.zip"
        self._base_os_name = "os.zip"
        self._ifwi_pkg_name = "ifwi.zip"
        if ((str(self._os_install)).lower() in ["true", "yes", "on", "ok"]):
            self._os_install = True
        if ((str(self._format_pendrive)).lower() in ["true", "yes", "on"]):
            self._format_pendrive = True
        elif ((str(self._format_pendrive)).lower() in ["false", "no", "off"]):
            self._format_pendrive = None  # giving the option to user just to extract and replace in package alone in already formatted USB
        if ((str(self._initialize_sft_pkg)).lower() in ["true", "yes", "on"]):
            self._initialize_sft_pkg = True
        if ((str(self._direct_sft_pkg_download)).lower() in ["true", "yes", "on"]):
            self._direct_sft_pkg_download = True
        if ((str(self._usr_given_local_sft_mode)).lower() in ["true", "yes", "on"]):
            self._usr_given_local_sft_mode = True
        if ((str(self._initialize_os_pkg)).lower() in ["true", "yes", "on"]):
            self._initialize_os_pkg = True
        if ((str(self._direct_os_download)).lower() in ["true", "yes", "on"]):
            self._direct_os_download = True
        elif ((str(self._usr_given_local_os_mode)).lower() in ["true", "yes", "on"]):
            self._usr_given_local_os_mode = True

        if ((str(self._extract_sft_package)).lower() in ["yes", "true", "on"]):
            self._extract_sft_package = True
            if not self._usb_size:
                self._log.error(
                    "Extract To USB Paramter by Default is True,Please Enter usb Size --USB_SIZE ,If Package Extraction Not required provide --EXTRACT_SOFTWARE_TO_USB false")
                return False
            elif not self._format_pendrive:
                self._log.error(
                    "Fromatting USB is Made False In,It will replace content in Pendrive It will Not Format USB")
                self._format_pendrive = False
        if (str(self._usb_size) in ["64", "128", "256", "500", "1000"]):
            if (self._ostype == "Linux"):
                self._log.error(
                    "Due To Software and FileSize Limitation FAT32 Format Connect only 32gb or less For Linux OS Installation.")
                return False
        if ((str(self._extract_os_package)).lower() in ["true", "yes", "on"]):
            self._extract_os_package = True
            if not self._usb_size:
                if self._os_install == True:
                    self._log.error(
                        "Extract To USB Paramter by Default is True,Please Enter usb Size --USB_SIZE ,If Package Extraction Not required provide --EXTRACT_SOFTWARE_TO_USB false")
                    return False
        if ((str(self._extract_sft_package)).lower() in ["no", "false", "off"]):
            self._extract_sft_package = False
            self._log.info("EXtraction Of Software Package and formatting USB is Skipped")
            self._format_pendrive = False
        if ((str(self._extract_os_package)).lower() in ["no", "false", "off"]):
            self._extract_os_package = False
            self._log.info("EXtraction Of OS Package and formatting USB is Skipped")
            self._format_pendrive = False

    @classmethod
    def add_arguments(cls, parser):
        super(Os_Installation, cls).add_arguments(parser)
        # caf based throw and fetch approach
        ostype = os.environ.get("OSTYPE")
        ifwipath = os.environ.get("IFWIPATH")
        ifwifile = os.environ.get("IFWIFILE")
        imagetype = os.environ.get("IMAGETYPE")
        driverpkgpath = os.environ.get("DRIVERPKGPATH")
        driverfile = os.environ.get("DRIVERFILE")
        imagepath = os.environ.get("IMAGEPATH")
        imagefile = os.environ.get("IMAGEFILE")
        enableflashing = os.environ.get("ENABLEFLASHING")
        basepath = os.environ.get("BASEPATH")
        # host path Fixed or parameter can change them
        if not enableflashing:
            enableflashing = False
        if (str(platform.architecture()).find("WindowsPE") != -1):
            host = "windows_host"
            ifwi_img_hostpath = "C:\IFWI_Image\\"
            sft_and_baseos = "C:\OS\\"
            # host sanity check for folders
            if (path.exists("C:\IFWI_Image") != True):
                subprocess.check_output("mkdir C:\IFWI_Image", shell=True)
            if (path.exists("C:\os") != True):
                subprocess.check_output("mkdir C:\os", shell=True)
        elif (str(platform.architecture()).find(r"ELF") != -1):
            host = "rpi_linux_host"
            ifwi_img_hostpath = "/home/pi/Public/firmware/chipwrite/"

        parser.add_argument('--ATF_USERNAME', action="store", dest="atf_user", default="sys_degsi1",
                            help="Inorder To Download From Other Artifactory Location give correct UserName by Default sys_degsi1 username")
        parser.add_argument('--ATF_PASSWORD', action="store", dest="atf_password", default="czhfi20$",
                            help="Inorder To Download From Other Artifactory Location give correct password by Default czhfi20$ password")
        parser.add_argument('--OSTYPE', action="store", dest="OSTYPE", default=ostype,
                            help="Which Flavor Of OS Distribution It is Linux|Windows|ubuntu|centos|suse|oss_windows|without_os|esxi")
        parser.add_argument('--IMAGEPATH', action="store", dest="OS_IMAGEPATH", default=imagepath,
                            help="Base OS_Image ATF_Path this bah will be appended to Base parent path")
        parser.add_argument('--IMAGEFILE', action="store", dest="OS_IMAGEFILE", default=imagefile,
                            help="Base_OS File Name Integrated windows .wim or windows or Rhel base os url name xxxx.zip,ww56.wim")
        parser.add_argument('--IMAGETYPE', action="store", dest="IMAGETYPE",
                            default=imagetype)  # not required with or without oss
        parser.add_argument('--BASEPATH', action="store", dest="BASEPATH", default=basepath,
                            help="BasePath parent Surl Structure OWR Trigger https://ubit-artifactory-ba.intel.com/artifactory/dcg-dea-srvplat-local/Kits/")
        parser.add_argument('--DRIVERPKGPATH', action="store", dest="DRIVERPKGPATH", default=driverpkgpath)
        parser.add_argument('--DRIVERFILE', action="store", dest="DRIVERFILE",
                            default=driverfile)  # only linux since for windows only wim
        ##IFWI PACKAGE
        # --------------------- Whether To Download and Use ALready Existing IFWI Package
        parser.add_argument('--ENABLEFLASHING', action="store", dest="ENABLE_IFWI_FLASHING", default=enableflashing,
                            help="Incase IFWI .bin Needs To Be Flashed On Platform Give True By Default False it WIll Be False")
        parser.add_argument('--IFWIPATH', action="store", dest="IFWIPATH", default=ifwipath)  # owr
        parser.add_argument('--IFWIFILE', action="store", dest="IFWIFILE", default=ifwifile)  # owr
        # --------------------- FOR DIRECT Download of IFWI PACKAGE
        parser.add_argument('--DIRECT_IFWI_PACKAGE_DOWNLOAD_MODE', action="store", dest="direct_ifwi_download",
                            default=False,
                            help="InOrder TO Directly Download Ifwi-Package From ATF Make It True,by Default False")
        parser.add_argument('--ATF_PATH_IFWI_PKG', action="store", dest="atf_ifwi_path", default=None,
                            help="InOrder TO Directly Download Ifwi-Package From ATF Make It True,by Default False")
        # --------------------- FOR Custom RE-Use of IFWI PACKAGE In Local Machine
        parser.add_argument('--LOCAL_IFWI_PACKAGE_MODE', action="store", dest="pre_downloaded_ifwi_pkg_mode",
                            default=None,
                            help="Inorde TO Make Use Of Already Existing Predownloaded IFWI Package From Local Hostmachine, Make It True, By Default it will be False")  # true will fetch the image location along sft img_name passed by user
        parser.add_argument('--LOCAL_IFWI_IMG_PATH', action="store", dest="ifwi_img_dwnd_host_path",
                            default=ifwi_img_hostpath,
                            help="Incase already Exisitng IFWI Image on Local Drive Needs To Be Used Give Full ifwi path Location")  # offline flashing
        # parser.add_argument('--DND_EXTRACT', action = "store", dest = "img_dnd_extract",default = True,help="Extract IFWI Image TO USB,By Default It will be True")
        parser.add_argument('--HOST', action="store", dest="host", default=host,
                            help="Autoamtically it Recognizes IT's Windwos or Linux Host Machien")
        ##USB FORMAT
        parser.add_argument('--FORMAT_USB', action="store", dest="format_pendrive", default=True,
                            help="Formatting USB is by Default Enabled, Give false in-case you don't want to format")  # formating pendrive
        parser.add_argument('--USB_SIZE', action="store", dest="usb_size", default=None,
                            help="USB Pendrive Size For Selecting The Connect USB in From Host-MACHINE CURRENTLY Supported Size 8/16/32/64 GB and for linux less than 32gb Pendrive is only prefered due to OS File size Limitation 0f fat32")
        parser.add_argument('--USB_WIM', action="store", dest="usb_wim", default=False,
                            help="Format's Pendrive Into 2 Partition with 3GB FAT32 size and remaining With NTFS Format Size")
        parser.add_argument('--CURL_SERVER', action="store", dest="curl_server",
                            default="bdcspiec010.gar.corp.intel.com",
                            help="Curl Based Flask Server To Download Autoamtion package and WIMtool")

        ##SOFTWARE PACKAGE
        # --------------------- Whether To Download and Use ALready Existing SOFTWARE Package
        parser.add_argument('--INITIALIZE_SOFTWARE_PACKAGE', action="store", dest="initialize_sft_pkg", default=None,
                            help="Inorder To Download From ARTIFACTORY or Reuse Software-Package Available in Hostmachine Local Drive, by Default is False")
        # --------------------- FOR DIRECT Download of SOFTWARE PACKAGE
        parser.add_argument('--DIRECT_SOFTWARE_PACKAGE_DOWNLOAD_MODE', action="store", dest="direct_sft_download",
                            default=None,
                            help="InOrder TO Downloaded Software-Package From Artifactory Directly Make It True,by Default False")
        parser.add_argument('--ATF_PATH_SFT_PKG', action="store", dest="atf_sft_pkg_path", default=None,
                            help="Full path along with file name of Software_pkg in Arifactory has To be Given including")  # full path for the base sft_pkg to be given
        # --------------------- FOR Custom RE-Use of SOFTWARE PACKAGE In Local Machine
        parser.add_argument('--LOCAL_SOFTWARE_PACKAGE_MODE', action="store", dest="pre_downloaded_sft_pkg_mode",
                            default=None,
                            help="Inorde TO Make Use Of Already Existing Predownloaded Sfotware Packe From Local Hostmachine, Make It True, By Default it will be False")  # true will fetch the image location along sft img_name passed by user
        parser.add_argument('--LOCAL_SOFTWARE_PACKAGE_LOCATION', action="store",
                            dest="pre_downloaded_sft_local_location", default=None,
                            help="Software Pre-Downlaoded Local Package Path eg: c:\path\sft_pkg.zip")  # c:\path\sft_pkg.zip

        ##BASE OR WIM KIT DOWNLOAD
        # --------------------- Whether To Download or Use ALready Existing OS Package
        parser.add_argument('--INITIALIZE_OS_PACKAGE', action="store", dest="initialize_os_pkg", default=None,
                            help="Inorder To Download or Reuse OS-Package, by Default is False")
        # --------------------- FOR DIRECT Download of OS PACKAGE
        parser.add_argument('--DIRECT_OS_PACKAGE_DOWNLOAD_MODE', action="store", dest="direct_os_download",
                            default=None,
                            help="InOrder TO Make Use Of Direct Artifactory Download Of OS-Package From Local HostMachine Make It True,by Default False")
        parser.add_argument('--ATF_PATH_OS_PKG', action="store", dest="atf_baseos_path", default=None,
                            help="Provide Artifactory URL Link For Os Image Path With File Extension")
        # --------------------- FOR Custom RE-Use of OS PACKAGE In Local Machine
        parser.add_argument('--LOCAL_OS_PACKAGE_MODE', action="store", dest="pre_downloaded_os_pkg_mode", default=False,
                            help="InOrder TO Make Use Of Pre-Downloaded OS-Package From Local HostMachine Make It True,by Default False")
        parser.add_argument('--LOCAL_OS_PACKAGE_LOCATION', action="store", dest="pre_downloaded_os_pkg_location",
                            default=None,
                            help="Incase Already Downloaded OS Image Is Available then Give Full Path With Os Package Filename Extension needs to be given")

        # EXTRACTION
        parser.add_argument('--EXTRACT_SOFTWARE_TO_USB', action="store", dest="extract_sft_package_to_usb",
                            default=True,
                            help="For Avoiding Extraction of Downloaded Software Package To USB, Incase Already Software Package Content Is Available No Need To Extract Again Give False by Default It Will Be True")
        parser.add_argument('--EXTRACT_OS_TO_USB', action="store", dest="extract_os_package_to_usb", default=True,
                            help="For Avoiding Extraction of Downloaded OS Image To USB, Incase Already OS Content Is Available No Need To Extract Again Give False by Default It Will Be True")

        # BIOS Selection and Change
        parser.add_argument('--USB_DEVICE_NAME', action="store", dest="usb_drive_name", default=None,
                            help="Name of the USB Drive How it Appears in BIOS")
        parser.add_argument('--HARDISK_DEVICE_NAME', action="store", dest="hardisk_drive_name", default=None,
                            help="Name of the Hard Drive How it Appears in BIOS")
        parser.add_argument('--BIOS_BOOT_ORDER_PATH', action="store", dest="boot_order_change_path",
                            default="Boot Maintenance Manager,Boot Options, Change Boot Order",
                            help="Provide Bios Path To Change Boot-Order \"xxxx,xxx,xxx\" by Default Boot Maintenance Manager,Boot Options,Change Boot Order,Commit Changes and Exit")
        parser.add_argument('--BIOS_BOOT_SELECT_PATH', action="store", dest="boot_select_path",
                            default="Boot Manager Menu",
                            help="Provide USB Boot Path \"xxxx,xxx\" For Selecting USB Drive For Os Installation by Default Boot Manager Menu")
        parser.add_argument('--SAVE_KNOB_NAME', action="store", dest="save_knob_path",
                            default="Commit Changes and Exit",
                            help="Save Knob Name by Default This is the Knob Commit Changes and Exit")
        # --IFWIFILE Name of the IFWI Image with .bin Extension
        # For Direct Parameter passing no need of Artifactory usage  --IFWI_IMG_PATH xxxxx --IFWIFILE xxxxx --Dnd_Extract False

        # OS install
        parser.add_argument('--OS_INSTALLATION', action="store", dest="only_os_install", default=True,
                            help="Incase Os Image Alone needs to be Flashed to platform")

        # POST OS Automation Enabler
        parser.add_argument('--CENTOS_CFG_FILE_NAME', action="store", dest="post_os_automation_enabler_centos",
                            default="centOS8-auto.cfg",
                            help="CFG file in Software Package will be Additionally Added with AutomationEnabler Functionality, Please Give the correct CFG file,by default it is centOS8-manual.cfg for CENTOS")
        parser.add_argument('--RHEL_CFG_FILE_NAME', action="store", dest="post_os_automation_enabler_rhel",
                            default="rh8.2-uefi.cfg",
                            help="CFG file in Software Package will be Additionally Added with AutomationEnabler Functionality ,Please Give the correct CFG file,by default is fc31-uefi-ks.cfg for RHEL")

    def format_usb_drive(self, size, format_usb=None, wim=None):
        """
        :- size Pendrive Size accepted size values are 8,16,32,64
           wim for windwos installation it requires a special format of the pendrive into 2 partion, pass yes or True if os that needs to be copied into pendrive is .wim
        return True
        following the action of True, formats the pendrive assigns letter S and renames the usb_drive to OS
        """
        size = str(size)
        if (str(platform.architecture()).find("WindowsPE") != -1):
            try:
                p = Popen(["diskpart"], stdin=PIPE, stdout=PIPE)
                if six.PY2:
                    ret = p.stdin.write(b'rescan \n')
                    ret = p.stdin.write(b'list disk \n')
                    ret = p.stdin.write(b'exit \n')
                    ret = p.stdout.read()
                    a = ret.split(",")
                    a = str(a).strip()
                    a = " ".join(a.split())
                elif six.PY3:
                    ret = p.stdin.write(bytes("rescan \n", encoding='utf-8'))
                    time.sleep(2)
                    ret = p.stdin.write(bytes("list disk \n", encoding='utf-8'))
                    time.sleep(2)
                    ret = p.stdin.write(bytes("exit \n", encoding='utf-8'))
                    ret = p.communicate()
                    a = str(ret).split(",")
                    a = str(a).strip()
                    a = " ".join(a.split())
                try:
                    if (size == "8"):
                        for i in ("7 GB", "7.8 GB", "7.5 GB", "6 GB", "6.5 GB", "6.8 GB"):
                            try:
                                if (a.index(str(i)) != -1):
                                    index = a.index(str(i))
                                    self._log.info(
                                        "Usb Available Size That was Found {0} {1}".format(a[index:index + 2], "GB"))
                                    data = (a[index - 19:index + 2])
                                    break
                            except:
                                continue
                    elif (size == "16"):
                        for i in ("14 GB", "14.5 GB", "13 GB", "12.5 GB", "13.5 GB"):
                            try:
                                if (a.index(str(i)) != -1):
                                    index = a.index(str(i))
                                    self._log.info(
                                        "Usb Available Size That was Found {0} {1}".format(a[index:index + 2], "GB"))
                                    data = (a[index - 20:index + 2])
                                    break
                            except:
                                continue
                    elif (size == "32"):
                        for i in ("27 GB", "27.5 GB", "28 GB", "28.5 GB", "28.8 GB", "28.7 GB","28.9 GB", "29 GB", "29.5 GB"):
                            try:
                                if (a.index(str(i)) != -1):
                                    index = a.index(str(i))
                                    self._log.info(
                                        "Usb Available Size That was Found {0} {1}".format(a[index:index + 2], "GB"))
                                    data = (a[index - 20:index + 2])
                                    break
                            except:
                                continue
                    elif (size == "64"):
                        for i in ("57 GB", "57.5 GB","56 GB", "56.5 GB", "56.8 GB", "57.8 GB", "58 GB", "58.5 GB", "59.5 GB"):
                            try:
                                if (a.index(str(i)) != -1):
                                    index = a.index(str(i))
                                    self._log.info(
                                        "Usb Available Size That was Found {0} {1}".format(a[index:index + 2], "GB"))
                                    data = (a[index - 20:index])
                                    break
                            except:
                                continue
                    else:
                        self._log.error(
                            "Please Ensure that pendrive size is Correct and Connected To Host-Machine Supported size of USb 8,16,32,64gb {0}".format(
                                ret))
                        return False
                    mb = (int(a[index:index + 2]) * 1000)
                    ntfs = (mb - 4000)
                    fat_size = 3000
                except Exception as ex:
                    self._log.error(
                        "Please Ensure that pendrive size is Correct and Connected To Host-Machine Supported size of USb 8,16,32,64gb {0}".format(
                            ex))
                    return False
                a = ["Disk 1", "Disk 2", "Disk 3", "Disk 4"]
                for i in range(0, 10):
                    if (a[i] in data):
                        pendrive_disk = a[i]
                        self._log.info("This {0} is USB_Device".format(pendrive_disk))
                        break
                if ((str(wim)).lower() in ["true", "yes", "on"]):
                    time.sleep(10)
                    try:
                        if six.PY2:
                            p = Popen([b'diskpart'], stdin=PIPE)
                            res1 = p.stdin.write(b'list vol \n')
                            time.sleep(4)
                            p.stdin.flush()
                            res1 = p.stdin.write(b'rescan \n')
                            time.sleep(4)
                            p.stdin.flush()
                            res1 = p.stdin.write(b'list disk \n')
                            time.sleep(1)
                            p.stdin.flush()
                            res1 = p.stdin.write(b'select ' + str(pendrive_disk) + ' \n')
                            time.sleep(1)
                            p.stdin.flush()
                            try:
                                res4 = p.stdin.write(b'clean \n')
                                time.sleep(5)
                                p.stdin.flush()
                            except:
                                res4 = p.stdin.write(b'clean \n')
                                time.sleep(5)
                                p.stdin.flush()
                            res1 = p.stdin.write(b'rescan \n')
                            time.sleep(5)
                            p.stdin.flush()
                            res1 = p.stdin.write(b'select ' + str(pendrive_disk) + ' \n')
                            time.sleep(2)
                            p.stdin.flush()
                            res5 = p.stdin.write(b"create partition primary SIZE=" + str(ntfs) + " \n")
                            time.sleep(3)
                            p.stdin.flush()
                            res6 = p.stdin.write(b"FORMAT FS=NTFS Label=UsbWIMs QUICK \n")
                            time.sleep(6)
                            p.stdin.flush()
                            res7 = p.stdin.write(b"assign letter=S\n")
                            time.sleep(2)
                            p.stdin.flush()
                            res8 = p.stdin.write(b"active \n")
                            time.sleep(2)
                            p.stdin.flush()
                            res6 = p.stdin.write(b"create partition primary SIZE=" + str(fat_size) + " \n")
                            time.sleep(3)
                            p.stdin.flush()
                            res6 = p.stdin.write(b"FORMAT FS=fat32 Label=WIMAGERUSB QUICK \n")
                            time.sleep(6)
                            p.stdin.flush()
                            res7 = p.stdin.write(b"assign letter=H \n")
                            time.sleep(2)
                            p.stdin.flush()
                            res8 = p.stdin.write(b"active \n")
                            time.sleep(2)
                            p.stdin.flush()
                            res8 = p.stdin.write(b"exit \n")
                            time.sleep(2)
                            p.stdin.flush()
                        elif six.PY3:
                            p = Popen(['diskpart'], stdin=PIPE)
                            res1 = p.stdin.write(bytes('list vol \n', encoding='utf8'))
                            time.sleep(4)
                            p.stdin.flush()
                            res1 = p.stdin.write(bytes('rescan \n', encoding='utf8'))
                            time.sleep(2)
                            p.stdin.flush()
                            res1 = p.stdin.write(bytes('list disk \n', encoding='utf8'))
                            time.sleep(2)
                            p.stdin.flush()
                            res1 = p.stdin.write(bytes('select ' + str(pendrive_disk) + ' \n', encoding='utf8'))
                            time.sleep(2)
                            p.stdin.flush()
                            try:
                                res4 = p.stdin.write(bytes('clean \n', encoding='utf8'))
                                time.sleep(8)
                                p.stdin.flush()
                            except:
                                res1 = p.stdin.write(bytes('rescan \n', encoding='utf8'))
                                time.sleep(3)
                                p.stdin.flush()
                                res1 = p.stdin.write(bytes('select ' + str(pendrive_disk) + ' \n', encoding='utf8'))
                                time.sleep(2)
                                p.stdin.flush()
                                res4 = p.stdin.write(bytes('clean \n', encoding='utf8'))
                                time.sleep(8)
                                p.stdin.flush()

                            res1 = p.stdin.write(bytes('select ' + str(pendrive_disk) + ' \n', encoding='utf8'))
                            time.sleep(2)
                            p.stdin.flush()
                            res5 = p.stdin.write(
                                bytes("create partition primary SIZE=" + str(ntfs) + "\n", encoding='utf8'))
                            time.sleep(3)
                            p.stdin.flush()
                            res6 = p.stdin.write(bytes("FORMAT FS=NTFS Label=UsbWIMs QUICK \n", encoding='utf8'))
                            time.sleep(6)
                            p.stdin.flush()
                            res7 = p.stdin.write(bytes("assign letter=S\n", encoding='utf8'))
                            time.sleep(2)
                            p.stdin.flush()
                            res8 = p.stdin.write(bytes("active \n", encoding='utf8'))
                            time.sleep(2)
                            p.stdin.flush()
                            res6 = p.stdin.write(
                                bytes("create partition primary SIZE=" + str(fat_size) + " \n", encoding='utf8'))
                            time.sleep(3)
                            p.stdin.flush()
                            res6 = p.stdin.write(bytes("FORMAT FS=fat32 Label=WIMAGERUSB QUICK \n", encoding='utf8'))
                            time.sleep(6)
                            p.stdin.flush()
                            res7 = p.stdin.write(bytes("assign letter=H \n", encoding='utf8'))
                            time.sleep(2)
                            p.stdin.flush()
                            res8 = p.stdin.write(bytes("active \n", encoding='utf8'))
                            time.sleep(2)
                            p.stdin.flush()
                            res8 = p.stdin.write(bytes("exit \n", encoding='utf8'))
                            time.sleep(2)
                            p.stdin.flush()
                        # Downloading Wim-imager
                        # cwd = os.getcwd()
                        cwd = r"C:\os_package\wimimager.zip"
                        if (str(platform.architecture()).find("WindowsPE") != -1):
                            if not os.path.exists(cwd):
                                self._log.info("Wim_Imager Tool is Being Downloaded")
                                opt = subprocess.Popen(
                                    "curl -X GET " + str(self._curl_server) + "/files/wimimager.zip --output wimimager.zip",
                                    cwd=r"C:\os_package", stdin=PIPE, stdout=PIPE, stderr=STDOUT, shell=True)
                                opt = opt.stdout.read()
                                if (str(opt).find(r"100") != -1):
                                    self._log.info("Wim_Imager Tool Downloaded")
                                else:
                                    self._log.error("Curl_Server Down DOWNLAOD fAILED")
                            else:
                                self._log.info("Wim_Imager Tool already available in the folder -> '{}".format(cwd))
                        else:
                            print("NOT yet Implemented for Linux")
                        # Extracting Wim-Imager
                        self._log.info("Wim_Imager Tool Extraction To Pendrive In-Progress")
                        #cwd = os.getcwd()
                        cwd = r"C:\os_package"
                        if (str(platform.architecture()).find("WindowsPE") != -1):
                            path_to_zip_file = cwd + str("\wimimager.zip")
                            Target_path = "H:"
                            with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
                                zip_ref.extractall(Target_path)
                            self._log.info("Wim_Imager Tool Extraction To Pendrive Successfull")
                            return True
                        elif (str(platform.architecture()).find(r"ELF") != -1):
                            path_to_zip_file = cwd + str("/wimimager.zip")
                            Target_path = r"/home/pi/Desktop/linuxashost"
                            with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
                                zip_ref.extractall(Target_path)
                            self._log.info("Wim_Imager Tool Extraction To Pendrive Successfull")
                            return True
                    except Exception as ex:
                        self._log.error("Issues Encounterd While Formatting Pendrive: {0}".format(ex))
                        return False
                else:  # non-wimager that is normal usb flashing single drive
                    time.sleep(10)
                    try:
                        if six.PY3:
                            p = Popen(['diskpart'], stdin=PIPE)
                            res1 = p.stdin.write(bytes("list vol \n", encoding='utf8'))
                            time.sleep(4)
                            p.stdin.flush()
                            res1 = p.stdin.write(bytes("rescan \n", encoding='utf8'))
                            time.sleep(1)
                            p.stdin.flush()
                            res1 = p.stdin.write(bytes("list disk \n", encoding='utf8'))
                            time.sleep(1)
                            p.stdin.flush()
                            res1 = p.stdin.write(bytes("select " + str(pendrive_disk) + " \n", encoding='utf8'))
                            time.sleep(1)
                            p.stdin.flush()
                            try:
                                res4 = p.stdin.write(bytes("clean \n", encoding='utf8'))
                                time.sleep(5)
                                p.stdin.flush()
                            except:
                                res1 = p.stdin.write(bytes('rescan \n', encoding='utf8'))
                                time.sleep(3)
                                p.stdin.flush()
                                res1 = p.stdin.write(bytes('select ' + str(pendrive_disk) + ' \n', encoding='utf8'))
                                time.sleep(2)
                                p.stdin.flush()
                                res4 = p.stdin.write(bytes('clean \n', encoding='utf8'))
                                time.sleep(8)
                                p.stdin.flush()

                            res1 = p.stdin.write(bytes('select ' + str(pendrive_disk) + ' \n', encoding='utf8'))
                            time.sleep(2)
                            p.stdin.flush()
                            res5 = p.stdin.write(bytes("create partition primary \n", encoding='utf8'))
                            time.sleep(3)
                            p.stdin.flush()
                            res8 = p.stdin.write(bytes("FORMAT FS=FAT32 Label=OS QUICK \n", encoding='utf8'))
                            time.sleep(10)
                            p.stdin.flush()
                            res7 = p.stdin.write(bytes("assign letter=S \n", encoding='utf8'))
                            time.sleep(2)
                            p.stdin.flush()
                            res8 = p.stdin.write(bytes("active \n", encoding='utf8'))
                            time.sleep(2)
                            p.stdin.flush()
                            res8 = p.stdin.write(bytes("exit \n", encoding='utf8'))
                            time.sleep(2)
                            p.stdin.flush()
                            return True
                        elif six.PY2:
                            p = Popen(['diskpart'], stdin=PIPE)
                            res1 = p.stdin.write(b'list vol \n')
                            time.sleep(4)
                            p.stdin.flush()
                            res1 = p.stdin.write(b'rescan \n')
                            time.sleep(1)
                            p.stdin.flush()
                            res1 = p.stdin.write(b'list disk \n')
                            time.sleep(1)
                            p.stdin.flush()
                            res1 = p.stdin.write(b'select ' + str(pendrive_disk) + ' \n')
                            time.sleep(1)
                            p.stdin.flush()
                            try:
                                res4 = p.stdin.write(b'clean \n')
                                time.sleep(5)
                                p.stdin.flush()
                            except:
                                res4 = p.stdin.write(b'clean \n')
                                time.sleep(5)
                                p.stdin.flush()
                            res1 = p.stdin.write(b'rescan \n')
                            time.sleep(5)
                            p.stdin.flush()
                            res1 = p.stdin.write(b'rescan \n')
                            time.sleep(3)
                            p.stdin.flush()
                            res5 = p.stdin.write(b"create partition primary \n")
                            time.sleep(3)
                            p.stdin.flush()
                            res8 = p.stdin.write(b"FORMAT FS=FAT32 Label=OS QUICK \n")
                            time.sleep(10)
                            p.stdin.flush()
                            res7 = p.stdin.write(b"assign letter=S \n")
                            time.sleep(2)
                            p.stdin.flush()
                            res8 = p.stdin.write(b"active \n")
                            time.sleep(2)
                            p.stdin.flush()
                            res8 = p.stdin.write(b"exit \n")
                            time.sleep(2)
                            p.stdin.flush()
                            return True
                    except Exception as ex:
                        self._log.error("Issues Encounterd While Formatting Pendrive {0}".format(ex))
                        return False
            except Exception as ex:
                self._log.info("Runas Administrator Priveillage Needs To Be Given {0}".format(ex))
                return False
        elif (str(platform.architecture()).find(r"ELF") != -1):
            self._log.error("Not yet Implemented for LINUX Hostmachines")

    def download_extract_os_image(self, Extract=None, Format_usb=None):
        """
        :param Extract:
        :param Format_usb:
        :return True or False with Error
        This Function is to Download and Extract the Base OS IMage Into Pendrive For Os Installation.
         it has 3 methods Direct Artifactory Download, Offline Pre-Downloaded OS Image, OWR IDF Jenkins Trigger Support.
         it can be customized According to User Requirement.
        """
        if (self._initialize_os_pkg == True):
            if (self._direct_os_download == True):
                try:
                    self._log.info(
                        "Method -1 Direct Download Of OS Package From Artifactory Location Given By User{0}".format(
                            self._direct_os_img_path))
                    head, tail = ntpath.split(self._direct_os_img_path)
                    self._base_os_name = tail
                    self._log.info("OS PACKAGE NAME >>> {0} <<<".format(self._base_os_name))
                    subprocess.check_output("curl --silent -u " + str(self._atf_username) + ":" + str(
                        self._atf_password) + " -X GET " + str(self._direct_os_img_path) + " --output " + str(
                        self._base_os_name), shell=True)
                    time.sleep(5)
                except Exception as ex:
                    self._log.error(
                        "{0} Artifactory Path Is Not Given Properly and Please Check ATF Usernme {1} and Password {2}".format(
                            self._direct_os_img_path, self._atf_username, self._atf_password))
                    return False
            elif (self._usr_given_local_os_mode == True):  # for making use of already #pre downlaoded package
                try:
                    self._log.info("Method - 2 Pre-Downloaded OS in Local Machine Path Given By User {0}".format(
                        self._local_drive_os_pkg))
                    head, tail = ntpath.split(self._local_drive_os_pkg)
                    self._base_os_name = tail
                    self._log.info("OS PACKAGE NAME >>> {0} <<<".format(self._base_os_name))
                    if (self._ostype == "Linux"):
                        if (zipfile.is_zipfile(self._local_drive_os_pkg) == True):
                            self._log.info("This Is the location of Predownloaded Linux OS Package {0}".format(
                                self._local_drive_os_pkg))
                        elif (str(".wim") in self._base_os_name):
                            self._log.error(
                                "This is Windows Image change the --OSTYPE to windows, Mistached Image Given for OSTYPE")
                            return False
                        else:
                            self._log.error("Improper Download Check File Name Not a valid Format")
                            return False
                    elif (self._ostype == "ESXI"):
                        if (zipfile.is_zipfile(self._local_drive_os_pkg) == True):
                            self._log.info("This Is the location of Predownloaded ESXI OS Package {0}".format(
                                self._local_drive_os_pkg))
                        elif (str(".wim") in self._base_os_name):
                            self._log.error(
                                "This is Windows Image change the --OSTYPE to windows, Mistached Image Given for OSTYPE")
                            return False
                        else:
                            self._log.error("Improper Download Check File Name Not a valid Format")
                            return False
                    elif (self._ostype == "Windows_Wim"):
                        wim_size = os.stat(self._local_drive_os_pkg).st_size
                        if (str(wim_size) >= "3000000000"):
                            if (str(".wim") in self._local_drive_os_pkg):
                                self._log.info("This Is the location of Predownloaded Windows .wim Package {0}".format(
                                    self._local_drive_os_pkg))
                            else:
                                self._log.error("In-approprite Package Set for Different ostype, Change Accordingly")
                                return False
                        else:
                            self._log.error(
                                "In-approprite Package Set for Different ostype, Change Accordingly, This --OS_TYPE is Meant for .wim windows")
                            return False
                    else:
                        self._log.error("--OS_TYPE can Either be Linux or Windows or ESXI , Unknown OS Type Given")
                        return False
                except Exception as ex:
                    self._log.error(
                        "Path needs to given along with package_name eg:- c:\\xxx\\os_pkg.zip or opt//os_pkg.zip {0}".format(
                            ex))
                    return False
            else:  # owr based trigger
                try:
                    self._log.info("Method -3 OWR Triggerd and Downloaded OS Package FROM Artifactory")
                    Atf_os_base_pkg_path = str(self._basepath) + str(self._imagepath) + str(self._imagefile)
                    self._log.info(
                        "This Is the location of Base 0S Package Artifactory Location {0}".format(Atf_os_base_pkg_path))
                    self._base_os_name = self._imagefile
                    self._log.info("OS PACKAGE NAME >>> {0} <<<".format(self._base_os_name))
                    ret = subprocess.check_output("curl --silent -u " + str(self._atf_username) + ":" + str(
                        self._atf_password) + " -X GET " + str(Atf_os_base_pkg_path) + " --output " + str(
                        self._imagefile), shell=True)
                except Exception as ex:
                    self._log.info("Path Given By User Doesn't Exists {0}".format(ex))
                    return False
            self._log.info("Verifying Downloaded OS Image")
            if (self._usr_given_local_os_mode == True):
                Dnd_img_path = self._local_drive_os_pkg
            else:
                cwd = os.getcwd()
                if (self._host == "windows_host"):
                    Dnd_img_path = cwd + "\\" + str(self._base_os_name)
                else:
                    Dnd_img_path = cwd + "//" + str(self._base_os_name)

            if (path.exists(Dnd_img_path) == True):
                if (self._ostype == "Linux"):
                    if (zipfile.is_zipfile(Dnd_img_path) == True):
                        self._log.info("Downloaded Image {0} Verified Successfull".format(Dnd_img_path))
                    else:
                        self._log.error(
                            "Downloaded File Is Not A ZIP Image File,Artifactory Path Is Not Given Properly and Please Check ATF Usernme and Password")
                        return False
                elif (self._ostype == "ESXI"):
                    if (zipfile.is_zipfile(Dnd_img_path) == True):
                        self._log.info("Downloaded Image {0} Verified Successfull".format(Dnd_img_path))
                    else:
                        self._log.error(
                            "Downloaded File Is Not A ZIP Image File,Artifactory Path Is Not Given Properly and Please Check ATF Usernme and Password")
                        return False
                elif (self._ostype == "Windows_Wim"):
                    wim_size = os.stat(Dnd_img_path).st_size
                    if (str(wim_size) >= "3000000000"):
                        if (str(".wim") in Dnd_img_path):
                            self._log.info(
                                "Downloaded Windows .wim Image {0} Verified Successfull ".format(Dnd_img_path))
                        else:
                            self._log.error(
                                "Failed, Downloaded Windows .wim Image {0} Failed To Verify ".format(Dnd_img_path))
                            return False
                    else:
                        self._log.error(
                            "Failed, Windows .wim Image Size is Below Expected Broken Image {0} Failed To Verify ".format(
                                Dnd_img_path))
                        return False
                else:
                    self._log.error("Unspecified OS Type")
                    return False
                if (Extract == True):
                    if (Format_usb == True):
                        if (self._ostype == "Windows_Wim"):
                            for i in range(0, 10):
                                ret_windows = self.format_usb_drive(self._usb_size, wim=True)
                                if (ret_windows == True):
                                    self._log.info(
                                        "USB Disk Partitioned Into two Partition Disk WITH FAT32 and NTFS format")
                                    self._log.info("USB Disk Partitioning Verification of S and H Drive")
                                    # create a file in S and H drive
                                    drive_file = [r"S:\s_drive.txt", r"H:\h_drive.txt"]
                                    usb_formatted_correct = []
                                    try:
                                        for drive_path in drive_file:
                                            with open(drive_path, "x") as fh:
                                                fh.write(drive_path)
                                                self._log.info("File has been created under {}..".format(drive_path))

                                            if os.path.exists(drive_path):
                                                usb_formatted_correct.append(True)
                                                os.remove(drive_path)
                                            else:
                                                usb_formatted_correct.append(False)
                                        if all(usb_formatted_correct):
                                            self._log.info(
                                                "Successfully verified USB Disk Partitioning of S and H Drive.. "
                                                "Proceeding further")
                                            break
                                    except:
                                        continue
                                elif(i>=2):
                                    return False
                                else:
                                    continue
                        elif (self._ostype == "Linux" or "ESXI"):
                            for i in range(0, 10):
                                ret_linux = self.format_usb_drive(self._usb_size)
                                if (ret_linux == True):
                                    self._log.info("USB Disk Partioned Into One Single Partition Disk WITH FAT32 format")
                                    self._log.info("USB Disk Partitioning Verification of S Drive")
                                    # create a file in S drive
                                    drive_file = r"S:\s_drive.txt"
                                    try:
                                        with open(drive_file, "x") as fh:
                                            fh.write(drive_file)
                                            self._log.info("File has been created under {}..".format(drive_file))

                                        if os.path.exists(drive_file):
                                            os.remove(drive_file)
                                            self._log.info(
                                                "Successfully verified USB Disk Partitioning of S Drive.. "
                                                "Proceeding further")
                                            break
                                    except:
                                        continue
                                elif (i >= 2):
                                    return False
                                else:
                                    continue

                    self._log.info("OS Packages are about To Be Extracted and Copied To USB")
                    try:
                        if (self._ostype == "Linux"):
                            start = time.time()
                            print("start to extract {}".format(Dnd_img_path))
                            with zipfile.ZipFile(Dnd_img_path, 'r') as zip_ref:
                                zip_ref.extractall("S:")
                            end = time.time()
                            zip_extract = (abs(start - end))
                            zip_extract = ("{:05.2f}".format(zip_extract))
                            self._log.info(
                                "Base OS Image {0} Packages Extract To USB Successfull Time Taken >> {1} Seconds".format(
                                    self._base_os_name, zip_extract))
                            return True
                        elif (self._ostype == "ESXI"):
                            start = time.time()
                            print("start to extract {}".format(Dnd_img_path))
                            with zipfile.ZipFile(Dnd_img_path, 'r') as zip_ref:
                                zip_ref.extractall("S:")
                            end = time.time()
                            zip_extract = (abs(start - end))
                            zip_extract = ("{:05.2f}".format(zip_extract))
                            self._log.info(
                                "Base ESXI OS Image {0} Packages Extract To USB Successfull Time Taken >> {1} Seconds".format(
                                    self._base_os_name, zip_extract))
                            return True
                        elif (self._ostype == "Windows_Wim"):
                            if (self._host == "windows_host"):
                                start = time.time()
                                subprocess.check_output("echo Y|copy " + str(Dnd_img_path) + " S:", shell=True)
                                end = time.time()
                                wim_copy = (abs(start - end))
                                wim_copy = ("{:05.2f}".format(wim_copy))
                                #  Fix if more than one HDD connected, assigned drive letter accordingly.
                                no_of_ssds = self._os_pre_req_lib.get_ssd_names_config()

                                dict_ssds = {1: 'E', 2: 'F', 3: 'G', 4: 'H'}
                                if no_of_ssds == 0 or no_of_ssds is None:
                                    self._log.error("Failed to get the SSD information, reasons could be are listed "
                                                    "below, \n 1. Seems there are no SSDs connected to the SUT. \n "
                                                    "2. If Manual - SUT Inventory config file is not updated correctly"
                                                    "with all the connected information..\n "
                                                    "3. If Auto - ITP has failed to get the correct SSD information,"
                                                    "please check the ITP connection")
                                    raise RuntimeError

                                with open("H:\WimagerUsbCommands.xml", "r+") as f:
                                    text = f.read()
                                    try:
                                        text = re.sub("sample.wim",
                                                      r"{}:\\".format(dict_ssds[no_of_ssds]) + str(self._base_os_name),
                                                      text)
                                    except Exception as ex:
                                        self._log.error("Either there are no hard disk found or more than 4 hard disks"
                                                        "are connected, please connect only 4 or less and try again..")
                                        raise ex
                                    f.seek(0)
                                    f.write(text)
                                    f.truncate()
                                self._log.debug("Wim Name Change Confirmed In USB, For Auto-Install")
                                self._log.info(
                                    "OS Image-Kit {0} Packages Copy To USB Successfull Time Taken >> {1} Seconds".format(
                                        self._base_os_name, wim_copy))
                                return True
                            else:
                                self._log.debug("Not Yet Implemented for Linux HostMachine")
                    except  Exception as ex:
                        self._log.error("Error In OS Packages Extraction {0}".format(ex))
                        return False
                else:
                    self._log.info("Extract To USB and Format USB is Given False")
                    return True
            else:
                self._log.error("OS Image File is Not Getting Downloaded, Check Given Path Properly")
                return False
        else:
            self._log.info("Download OS Package Parameter is Given as False, OS Package Download Will not Happen")
            return True

    def automation_post_installation_enabler(self):
        if (os.path.isfile("S:\\" + str(self._rhel_cfg_file_name)) == True):
            print("This is RHEL OS")

            with open("S:\\" + str(self._rhel_cfg_file_name), 'r') as file:
                filedata = file.read()
                time.sleep(4)

            # filedata = filedata.replace('nvme-cli', 'nvme-cli' + "\n" + ("python2*"))
            filedata = filedata.replace('firewall --disabled',
                                        'firewall --disabled' + "\n" + (
                                            "network  --bootproto=dhcp --device=enp1s0 --onboot=on --ipv6=auto") + "\n" + (
                                            "network  --bootproto=dhcp --device=enp2s0 --onboot=on --ipv6=auto") + "\n" + (
                                            "network  --bootproto=dhcp --device=enp3s0 --onboot=on --ipv6=auto") + "\n" + (
                                            "network  --bootproto=dhcp --device=enp4s0 --onboot=on --ipv6=auto")
                                        )
            filedata = filedata.replace("touch /etc/rc.d/postinstall.sh", "touch /etc/rc.d/postinstall.sh" + "\n" + (
                "ln -s /usr/bin/python3.6 /usr/bin/python"))
            with open("S:\\" + str(self._rhel_cfg_file_name), 'w', encoding="utf-8") as file1:
                file1.write(filedata)

            # replacement strings
            WINDOWS_LINE_ENDING = b'\r\n'
            UNIX_LINE_ENDING = b'\n'

            file_path = "S:\\" + str(self._rhel_cfg_file_name)

            with open(file_path, 'rb') as open_file:
                content = open_file.read()

            content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)

            with open(file_path, 'wb') as open_file:
                open_file.write(content)

        else:
            self._log.error("This Is Not Rhel8.2 OS")
        if (os.path.isfile("S:\\" + str(self._centos_cfg_file_name)) == True):
            self._log.info("This is Fedora OS")
            with open("S:\\" + str(self._centos_cfg_file_name), 'r') as file:
                filedata = file.read()
                time.sleep(4)
            # filedata = filedata.replace('nvme-cli', 'nvme-cli' + "\n" + ("python2*"))
            filedata = filedata.replace('firewall --disabled',
                                        'firewall --disabled' + "\n" + (
                                            "network  --bootproto=dhcp --device=enp1s0 --onboot=on --ipv6=auto") + "\n" + (
                                            "network  --bootproto=dhcp --device=enp2s0 --onboot=on --ipv6=auto") + "\n" + (
                                            "network  --bootproto=dhcp --device=enp3s0 --onboot=on --ipv6=auto") + "\n" + (
                                            "network  --bootproto=dhcp --device=enp4s0 --onboot=on --ipv6=auto")
                                        )
            filedata = filedata.replace("touch /etc/rc.d/postinstall.sh", "touch /etc/rc.d/postinstall.sh" + "\n" + (
                "ln -s /usr/bin/python3.6 /usr/bin/python"))
            with open("S:\\" + str(self._centos_cfg_file_name), 'w', encoding="utf-8") as file1:
                file1.write(filedata)
            # replacement strings
            WINDOWS_LINE_ENDING = b'\r\n'
            UNIX_LINE_ENDING = b'\n'
            file_path = "S:\\" + str(self._centos_cfg_file_name)
            with open(file_path, 'rb') as open_file:
                content = open_file.read()
            content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)
            with open(file_path, 'wb') as open_file:
                open_file.write(content)
        else:
            self._log.error("This Is Not Fedora OS")
        cwd = os.getcwd()
        if (self._ostype == "Linux"):
            try:
                opt = subprocess.Popen(
                    "curl -X GET " + str(self._curl_server) + "/files/xmlcli.zip --output xmlcli.zip",
                    stdin=PIPE, stdout=PIPE, stderr=STDOUT, shell=True)
                opt = opt.stdout.read()
                if (str(opt).find(r"100") != -1):
                    self._log.info("XMLCLI Tool Downloaded")
                else:
                    self._log.error("Failed To Download From Curl Server")
                    return False
                if (str(platform.architecture()).find("WindowsPE") != -1):
                    path_to_zip_file = cwd + str("\\xmlcli.zip")
                    Target_path = "S:\APP"
                    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
                        zip_ref.extractall(Target_path)
                    self._log.info("XMLCLI Tool Extraction To Pendrive Successfull")
                    return True
                else:
                    self._log.error("Need To Code For lINUX Hostmachine Environment")
            except Exception as ex:
                self._log.error("Xmlcli Tool Failed To Download {0}".format(ex))
                return False
        elif (self._ostype == "ESXI"):
            self._log.error("Xmlcli Tool Can't Get Copied since It's An ESIX Image")
            return "Integrated_wim_image"
        else:
            self._log.error("Xmlcli Tool Can't Get Copied since It's An Integrated Image")
            return "Integrated_wim_image"

    def download_extract_sft_package(self, Extract=None, Format_usb=None):
        ##linux sft package download
        if (self._initialize_sft_pkg == True):
            self._log.info("Extracting_Package TO USB IS {0}".format(Extract))
            if (self._direct_sft_pkg_download == True):
                try:
                    self._log.info("Method-1 Direct Download Of Software Package From Artifactory {0}".format(
                        self._direct_sft_pkg_download))
                    self._log.info("This Is the location of Software Package Artifactory Location {0}".format(
                        self._direct_sft_img_path))
                    head, tail = ntpath.split(self._direct_sft_img_path)
                    self._stf_pkg_name = tail
                    self._log.info("SOFTWARE-KIT PACKAGE NAME >>> {0} <<<".format(self._stf_pkg_name))
                    subprocess.check_output(
                        "curl -u " + str(self._atf_username) + ":" + str(self._atf_password) + " -X GET " + str(
                            self._direct_sft_img_path) + " --output " + str(self._stf_pkg_name), shell=True)
                    self._log.info("Direct Download Of Software Package From Artifactory Successfull")
                except Exception as ex:
                    self._log.error(
                        "{0} Artifactory Path Is Not Given Properly and Please Check ATF Usernme {1} and Password {2} {3}".format(
                            self._direct_sft_img_path, self._atf_username, self._atf_password, ex))
                    return False
            elif (self._usr_given_local_sft_mode == True):  # for making usee of already #pre downlaoded package
                try:
                    self._log.info("Method-2 Pre-Downloaded Software Package in Local Machine {0}".format(
                        self._local_drive_sft_pkg))
                    head, tail = ntpath.split(self._local_drive_sft_pkg)
                    self._stf_pkg_name = tail
                    self._log.info("SOFTWARE-KIT PACKAGE NAME >>> {0} <<<".format(self._stf_pkg_name))
                    if (zipfile.is_zipfile(self._local_drive_sft_pkg) == True):
                        self._log.info("This Is the location of Predownloaded Software Package {0}".format(
                            self._local_drive_sft_pkg))
                    else:
                        self._log.error("File Name IS Not Correct")
                        return False
                except Exception as ex:
                    self._log.error(
                        "Path needs to given along with package_name eg:- c:\\xxx\\sft_pkg.zip or opt//sft_pkg.zip {0}".format(
                            ex))
                    return False
            else:
                self._log.info("Method -3 OWR Triggerd and Downloaded Software Package FROM Artifactory")
                Atf_os_sft_pkg_path = str(self._basepath) + str(self._driverpkgpath) + str(self._driverfile)
                self._log.info(
                    "This Is the location of Software Package Artifactory Location {0}".format(Atf_os_sft_pkg_path))
                try:
                    ret = subprocess.check_output(
                        "curl -u " + str(self._atf_username) + ":" + str(self._atf_password) + " -X GET " + str(
                            Atf_os_sft_pkg_path) + " --output " + str(self._driverfile), shell=True)
                    self._log.info("Method -3 OWR Trigger Download Of Software Package From Artifactory Successfull")
                    self._stf_pkg_name = self._driverfile
                    self._log.info("SOFTWARE-KIT PACKAGE NAME >>> {0} <<<".format(self._stf_pkg_name))
                except Exception as ex:
                    self._log.error("FULL Artifactory Path needs to given along with package_name with .zip".format(ex))
                    return False
            if (self._usr_given_local_sft_mode == True):
                Dnd_sft_path = self._local_drive_sft_pkg
            else:
                cwd = os.getcwd()
                if (self._host == "windows_host"):
                    Dnd_sft_path = cwd + "\\" + str(self._stf_pkg_name)
                else:  # linus host
                    Dnd_sft_path = cwd + "//" + str(self._stf_pkg_name)
            head, tail = ntpath.split(Dnd_sft_path)
            pkg_name = tail
            self._log.info("Path Of Software Package {0}".format(Dnd_sft_path))
            if (path.exists(Dnd_sft_path) == True):
                if (zipfile.is_zipfile(Dnd_sft_path) == True):
                    self._log.info("Verified Software Package {0} Verification Successfull".format(pkg_name))
                else:
                    self._log.error(
                        "{0} File Is Not A Proper ZIP Image File,Package {1} Artifactory Path Is Not Given Properly and Please Check ATF Usernme {2} and Password {3}".format(
                            pkg_name, Dnd_sft_path, self._atf_username, self._atf_password))
                    return False
                if (Extract == True):
                    self._log.info("Software Packages are about To Be Extracted and Copied To USB")
                    try:
                        self._log.info("Software Package {0}".format(Dnd_sft_path))
                        with zipfile.ZipFile(Dnd_sft_path, 'r') as zip_ref:
                            zip_ref.extractall("S:")
                        self._log.info("Software {0} Packages Extraction To USB Successfull".format(Dnd_sft_path))
                        ret = self.automation_post_installation_enabler()
                        if (ret in [True, "Integrated_wim_image"]):
                            return True
                        else:
                            return False
                    except Exception as ex:
                        self._log.error("Error In Software Packages Extraction {0}".format(ex))
                        return False
                else:
                    self._log.info(
                        "Software Package Extract To USB is set has False Only Downlaoded The Software Package")
            else:
                self._log.error("Software Package is Not Getting Downloaded check, Given Path Properly")
                return False
        else:
            self._log.info(
                "Download Software Package Parameter is Given as False, Software Package Download Will not Happen")
            return True

    def platform_ifwi_flashing(self):
        if ((str(self._enable_ifwi_flashing)).lower() in ["true", "yes", "on"]):
            # Downloading and Extracting IFWI-Image Alone
            if (self._direct_ifwi_pkg_download == True):  # ifwi DOWNLAOD from ATF
                try:
                    self._log.info("Method-1 Direct Download Of IFWI Package From Artifactory {0}".format(
                        self._direct_ifwi_pkg_download))
                    self._log.info("This Is the location of IFWI Package Artifactory Location {0}".format(
                        self._direct_atf_ifwi_path))
                    head, tail = ntpath.split(self._direct_atf_ifwi_path)
                    self._ifwi_pkg_name = tail
                    '''
                    #Checking and Removing Older version of same name if any
                    try:
                        if(self._host == "windows_host"):
                            subprocess.check_output("del /f "+str(self._local_ifwi_host_path)+str(self._ifwi_pkg_name),shell=True)
                        elif(self._host == "rpi_linux_host"):
                            subprocess.check_output("sudo rm -rf "+str(self._local_ifwi_host_path)+str(self._ifwi_pkg_name),shell=True)
                    '''
                    if (self._host == "windows_host"):
                        ret = subprocess.check_output("cd " + str(self._local_ifwi_host_path) + "&& curl -u " + str(
                            self._atf_username) + ":" + str(self._atf_password) + " -X GET " + str(
                            self._direct_atf_ifwi_path) + " --output " + str(self._ifwi_pkg_name), shell=True)
                    else:
                        ret = subprocess.check_output("cd " + str(self._local_ifwi_host_path) + "; curl -u " + str(
                            self._atf_username) + ":" + str(self._atf_password) + " -X GET " + str(
                            self._direct_atf_ifwi_path) + " --output " + str(self._ifwi_pkg_name), shell=True)
                    self._log.info("Direct Download Of IFWI Package From Artifactory Successfull")
                except Exception as ex:
                    self._log.error(
                        "{0} Artifactory Path Is Not Given Properly and Please Check ATF Usernme {1} and Password {2} {3}".format(
                            self._direct_ifwi_pkg_download, self._atf_username, self._atf_password, ex))
                    return False
            elif (self._local_ifwi_host_mode == True):  # for making usee of already #pre downlaoded package
                self._log.info(
                    "Method-2 Pre-Downloaded IFWI Package in Local Machine {0}".format(self._local_ifwi_host_path))
                head, tail = ntpath.split(self._local_ifwi_host_path)
                self._ifwi_pkg_name = tail
                if (".bin" in self._ifwi_pkg_name):
                    if (path.exists(self._local_ifwi_host_path) == True):
                        self._log.info("User Has Given Extracted IFWI-zip and Given Direct .bin Image {0}".format(
                            self._ifwi_pkg_name))
                        self._ifwifile = self._ifwi_pkg_name
                    else:
                        self._log.error(
                            "User-Given Location {0} IFWI File Deosn't Exists, Provide Correct Location Of IFWI Image".format(
                                self._local_ifwi_host_path))
                        return False
                elif (".zip" in self._ifwi_pkg_name):
                    self._log.info("User Has Given IFWI Image Zip File Directly {0}".format(self._ifwi_pkg_name))
                    if (path.exists(self._local_ifwi_host_path) == True):
                        with zipfile.ZipFile(str(self._local_ifwi_host_path), 'r') as zip_ref:
                            zip_ref.extractall(head)
                        if (self._host == "windows_host"):
                            latest_ifwi_file = str(head) + "\*.bin"
                        else:
                            latest_ifwi_file = str(head) + "/*.bin"
                        latest_ifwi_img = glob.glob(latest_ifwi_file)
                        self._ifwifile = max(latest_ifwi_img, key=os.path.getctime)
                        head, file_name = ntpath.split(self._ifwifile)
                        self._ifwifile = file_name
                        self._local_ifwi_host_path = head
                        self._log.info("IFWI Image Method-2 {0} ".format(self._ifwifile))
                    else:
                        self._log.error(
                            "User-Given Location {0} IFWI File Deosn't Exists, Provide Correct Location Of IFWI Image".format(
                                self._local_ifwi_host_path))
                        return False
                else:
                    self._log.error(
                        "User Has Given only the file location {0} No specific file was Given, Please Given Full File path also with the File Name".format(
                            self._local_ifwi_host_path))
                    return False
                self._log.info("Pre-Downloaded IFWI From Local Computer {0}".format(self._ifwi_pkg_name))
            else:
                # Download Begins For IFWI IMG
                self._log.info("Method -3 OWR Triggerd and Downloaded Software Package FROM Artifactory")
                Atf_img_path = str(self._basepath) + str(self._ifwipath) + str(
                    self._ifwifile)  # if future IFWI path Change is Required
                self._log.info("This Is the location of IFWI Artifactory Location {0}".format(Atf_img_path))
                try:
                    if (self._host == "windows_host"):
                        ret = subprocess.check_output("cd " + str(self._local_ifwi_host_path) + "&& curl -u " + str(
                            self._atf_username) + ":" + str(self._atf_password) + " -X GET " + str(
                            Atf_img_path) + " --output " + str(self._ifwifile), shell=True)
                    else:
                        ret = subprocess.check_output("cd " + str(self._local_ifwi_host_path) + "; curl -u " + str(
                            self._atf_username) + ":" + str(self._atf_password) + " -X GET " + str(
                            Atf_img_path) + " --output " + str(self._ifwifile), shell=True)
                    self._ifwi_pkg_name = self._ifwifile
                except:
                    self._log.error("Failed Due To Path From Artifactory Not Given {0}".format(sys.exc_info()[0]))
                    return False
            time.sleep(5)
            Dnd_img_path = str(self._local_ifwi_host_path) + str(self._ifwi_pkg_name)
            if (self._local_ifwi_host_mode != True):
                self._log.info(Dnd_img_path)
                if (path.exists(Dnd_img_path) == True):
                    if (zipfile.is_zipfile(Dnd_img_path) == True):
                        self._log.info("IFWI Image Download Successfull")
                    else:
                        self._log.error(
                            "Downloaded File Is Not A IFWI ZIP Image File,Artifactory Path Is Not Given Properly")
                        return False
                else:
                    self._log.error("Download Didn't Happen, File DoesNot Exists")
                    return False
                time.sleep(5)
                with zipfile.ZipFile(Dnd_img_path, 'r') as zip_ref:
                    zip_ref.extractall(str(self._local_ifwi_host_path))

                # Deleting the zip after extracting
                if (self._host == "windows_host"):
                    try:
                        subprocess.check_output("del /f " + str(Dnd_img_path), shell=True)
                    except:
                        self._log.error("IFWI Zip Couldn't Be Delted After Extraction {0}".format(sys.exc_info()[0]))
                        return False
                elif (self._host == "rpi_linux_host"):
                    try:
                        subprocess.check_output("sudo rm -rf " + str(Dnd_img_path), shell=True)
                    except:
                        self._log.error("IFWI Zip Couldn't Be Delted After Extraction")
                        return False
                else:
                    self._log.error(
                        "Currently Supported Host Machines Are Microsoft Based OS and Debian Raspberry pi OS")
                self._log.info("IFWI Zip Image Deleted After Extraction")
                latest_ifwi_img = glob.glob(str(self._local_ifwi_host_path) + "*.bin")
                self._ifwifile = max(latest_ifwi_img, key=os.path.getctime)
                head, tail = ntpath.split(self._ifwifile)
                self._ifwifile = tail
            self._log.info("IFWI Image {0} Is Going To Get Flashed On Platform".format(self._ifwifile))

            if (self.platform_ac_power_off() != True):
                self._log.error("Failed To Platform Ac-Power OFF")
                return False

            # Detecting The Chip Flash Chip
            if (self._flash.chip_identify() != True):
                self._log.error("Unable to Identify Flash Chip")
                return False

            # Flashing Image
            if (self._flash.flash_image(self._local_ifwi_host_path, self._ifwifile) == True):
                self._log.info("IFWI Image {0} Flashing Successfull".format(self._ifwifile))
            else:
                self._log.info("Unable To Do Flashing IFWI Image")
                return False
            if (self.platform_ac_power_on() != True):
                self._log.error("Failed To Platform Ac-Power OFF")
                return False

            if (self.enter_into_bios() != True):
                self._log.error(
                    "IFWI Image Flashed But Didn't Enter Into Bios_Setup Page,Check Com Port already Open or Post-code")
                return False
            return True
        else:
            return "Flashing_Disabled"

    def platform_ac_power_off(self):

        if self._ac.ac_power_off() == True:
            self._log.info("Platfor(SUT) AC-power TURNED OFF")
        else:
            self._log.error("Failed TO Do AC-power OFF")
            return False
        # Making Sure Platform AC-Power is Turned OFF
        if self._ac.get_ac_power_state() == False:
            self._log.info("Platform(SUT) AC-power TURNED-OFF Confrimed")
            time.sleep(3)
            return True
        else:
            self._log.error("Platform(SUT) AC-power TURNED-Off Confrimation failed")
            return False

    def platform_ac_power_on(self):
        if self._ac.ac_power_on() == True:
            self._log.info("Platfor(SUT) AC-power TURNED ON")
        else:
            self._log.error("Failed TO Do AC-power ON")
            return False
        time.sleep(4)
        if self._ac.get_ac_power_state() == True:
            self._log.info("Platform(SUT) AC-power TURNED-ON Confrimed")
            time.sleep(5)
            return True
        else:
            self._log.error("Failed To Platform(SUT) AC-power TURNED-Off Confrimation")
            return False

    def switch_usb_to_target(self):  # changed
        if (self._phy.connect_usb_to_sut() != True):
            self._log.error("USB Switching To SUT Failed")
            return False
        return True

    def switch_usb_to_host(self):  # changed
        if (self._phy.connect_usb_to_host() != True):
            self._log.error("USB Switching To Host Failed")
            return False
        return True

    def bios_path_navigation(self, path):
        path = path.split(',')
        try:
            for i in range(len(path)):
                time.sleep(10)
                ret = self.setupmenu.get_page_information()
                ret = self.setupmenu.select(str(path[i]), None, True, 60)
                print(self.setupmenu.get_selected_item().return_code)
                self.setupmenu.enter_selected_item(ignore=False, timeout=10)
                self._log.info("Entered into {0} ".format(path[i]))
            return True
        except Exception as ex:
            self._log.error("{0} Issues Observed".format(ex))
            return False

    def enter_into_bios(self):
        if self.setupmenu.wait_for_entry_menu(1000):
            for i in range(0, 3):
                f2_state = self.setupmenu.press(r'F2')
                time.sleep(0.3)
                if f2_state:
                    self._log.info("Entry Menu Detected")
                    break
            ret = self.setupmenu.wait_for_bios_setup_menu(30)
            self._log.info("Entered Into Bios Menu")
            return True
        else:
            self._log.error("Failed To Enter Into Bios Menu Page,Close COM Port if opened in Putty")
            return False

    def execute(self):

        main_timer = time.time()
        start = time.time()
        self._log.info("{0} {1} {2} {3} {4}".format(self._ostype, self._ifwipath, self._ifwifile, self._imagetype,
                                                    self._driverpkgpath))
        self._log.info(
            "{0} {1} {2} {3} {4}".format(self._enable_ifwi_flashing, self._imagefile, self._local_ifwi_host_path,
                                         self._driverfile, self._basepath))
        if (self.prepare() != False):
            # Flashing IFWI Image
            ret = self.platform_ifwi_flashing()
            if (ret == True):
                self._log.info("IFWI_Image Flashing TO Platform Was Succesful")
            elif (ret == "Flashing_Disabled"):
                self._log.info("IFWI-Flashing Parameter is Given as False, IFWI_Image Flashing Will not Happen")
            else:
                return False

            # Mandatory for USB To Be Connect To Host
            if (self.switch_usb_to_host() != True):
                self._log.error("USB_DRIVE Is Not Connected To HostMachine")
                return False
            time.sleep(5)  # Mandatory Sleep
            ##linux ans windows base os and .wim downlaod
            if (self.download_extract_os_image(self._extract_os_package, self._format_pendrive) != True):
                self._log.error("Os Package Extraction TO USB Failed")
                return False

            # Downlaoding And Extracting OS Image to USB_DRIVE
            if (self.download_extract_sft_package(self._extract_sft_package, self._format_pendrive) != True):
                self._log.error("Software Package Extraction TO USB Failed")
                return False

            if (self._os_install == True):
                # Mandatory for USB To Be Connect To SUT
                if (self.switch_usb_to_target() != True):
                    self._log.error("USB_DRIVE Is Not Connected To Platform(SUT)")
                    return False

                if (self.platform_ac_power_off() != True):
                    self._log.error("Failed To Platform Ac-Power OFF")
                    return False

                if (self.platform_ac_power_on() != True):
                    self._log.error("Failed To Platform Ac-Power ON")
                    return False

                # Enter Into bios and change boot order and select USB for Installation
                self._log.info("Entering Into Bios SETUP Page of Target Platform")
                if (self.enter_into_bios() != True):
                    self._log.error("Didn't Enter Into Bios_Setup Page")
                    return False

                self._log.info(
                    "Entering Into Bios SETUP Page To Change BIOS BOOTORDER AND Select USB For OS-Installation")
                if (self.bios_path_navigation(path=self._bios_path) == True):
                    self.setupmenu.change_order([str(self._usb_drive_name)])
                    time.sleep(5)
                    self.setupmenu.change_order([str(self._hardisk_drive_name)])
                    self._log.info("BOOT Order Change Done {0} First Boot Order".format(self._hardisk_drive_name))
                    if (self.bios_path_navigation(path=self._save_knob_name) == True):
                        self._log.info("Changing and Saving Boot-Order Successful")
                        self.setupmenu.back_to_root(10, False)
                    else:
                        self._log.error("Unable To Change or Find BootOrder")
                        return False
                    if (self.bios_path_navigation(path=self._boot_select_path) == True):
                        self._log.info("Selecting USB To Proceed with Boot Successful")
                    else:
                        self._log.error("Unable To Enter Into Bios SETUP Page")
                        False
                else:
                    self._log.error("Unable To Change Boot-Order and FAILED To Proceed With OS Installation")
                    return False

                self._log.info("OS-Installation In Progress Will Taken Some Time")
                # verifying OS installation
                for i in range(0, 200):
                    try:
                        time.sleep(60)
                        if (self._os.is_alive() == True):
                            self._log.info("Booted Os And Entered Into OS Successfully")
                            return True
                        elif (i == 120):
                            self._log.info("Os Installation Had Issues")
                            return False
                        else:
                            self._log.debug("OS Installation Is IN-Progress")
                    except:
                        continue
            else:
                self._log.info("OS Installation was Given False, It Will Not Install OS")
        else:
            self._log.error("Preparing OS-Installation and Wrong-Parameter-Input Given")
            return False
        return True


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if Os_Installation.main() else Framework.TEST_RESULT_FAIL)
