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
import os
import sys
import time
import ntpath
import subprocess
import xml.etree.ElementTree as ET
from artifactory import ArtifactoryPath

try:
    if (sys.platform != 'win32'):
        tree = ET.parse('/home/Automation/system_configuration.xml')
    else:
        tree = ET.parse('C:\Automation\system_configuration.xml')
    root = tree.getroot()
    tool_path=""
    for child in root.iter('atf'):
        a = (child.attrib)
    try:
        atf_username= a['user']
        atf_password = a['password']
        program_name = a['program']
        xml_info_file = a['xmlfilename']
        program_xml_location = a['url_path']+str(program_name)+"/"+str(xml_info_file)
    except Exception as ex:
        print("COnfiguration Issue")
    try:
        for child in root.iter('sut_os'):
            a = (child.attrib)
            if(a['name'].lower()=="linux"):
                os_type="Linux"
            else:
                os_type="Windows"
    except Exception as ex:
        print("COnfiguration Issue")
except Exception as ex:
    print('Configuration FileNotFound')


def tool_url_extraction(tool_name=None,xml_file_download=None):
    """
    For Downloading the Tool From Artifactory
    internally used by API. not for direct user usage
    """
    if(xml_file_download == True):
        subprocess.check_output(
            "curl --silent -u " + str(atf_username) + ":" + str(atf_password) + " -X GET " + str(
                program_xml_location) + " --output " + str(xml_info_file), shell=True)
        return True
    else:
        subprocess.check_output(
            "curl --silent -u " + str(atf_username) + ":" + str(atf_password) + " -X GET " + str(
                program_xml_location) + " --output "+str(xml_info_file), shell=True)
        tree = ET.parse(xml_info_file)
        root = tree.getroot()
        tool_path = ""
        data=[]
        for child in root.iter():
            for key, value in child.items():
                data.append(value)
            a=(str(data).split('\n'))
        url=data.index(tool_name)
        out=data[url+1]
        if(str(out).find("https")!=-1):
            return True,out
        return False,"N/A"

def download_tool_to_host(tool_name=None,dest=None,all_tool=None):
    """
        tool_name :- name of the tool you wanted to download from the artifactory give the name mentioned in the xml_tool_info file
        dest :- destination of your tool to be downloaded by default /home/DPG_Automation/dtaf_content/src/lib/tools for Linux
                C:\DPG_Automation\dtaf_content\src\lib\tools for Windows
        all_tool :- True if passed it will download all the tools from artifactory of that project into the host machine location.
        return :- True Tool being Succesfull Downloaded
                  False Tool Failed to Download
    """
    if(dest == None):
        if (sys.platform != 'win32'):
            path = "/home/DPG_Automation/dtaf_content/src/lib/tools"
        else:
            path = r"C:\DPG_Automation\dtaf_content\src\lib\tools"
        if not os.path.exists(path):
            if (sys.platform == 'win32'):
                subprocess.check_output("mkdir "+str(path),shell=True)
            else:
                subprocess.check_output(r"mkdir "+str(path), shell=True)
    else:
        path=dest
        if not os.path.exists(dest):
            print("User Given Path in Host Doesn't Exists Do Check Destination path")
            sys.exit()
    if tool_name:
        ret = tool_url_extraction(tool_name)
        if (ret[0] == False):
            print("ATF TOOL XML Path Naming Issue")
            return False
        head, tool = ntpath.split(ret[1])
        start = time.time()
        subprocess.check_output(
            "curl --silent -u " + str(atf_username) + ":" + str(atf_password) + " -X GET " + str(
                ret[1]) + " --output " + str(path) + "\\" + str(tool), shell=True)
        end = time.time()
        zip_extract = (abs(start - end))
        zip_extract = ("{:05.2f}".format(zip_extract))
        print("Time Taken for This Tool >> {0} << TO Download {1} Seconds".format(tool_name, zip_extract))
        print("\nTool Downloaded Successfull to this Location {0}".format(path))
        return True
    else:
        if (tool_url_extraction(xml_file_download=True) == True):
            if(all_tool == True):
                tree = ET.parse(xml_info_file)
                root = tree.getroot()
                tool_path = ""
                data = []
                for child in root.iter():
                    for key, value in child.items():
                        data.append(value)
                start = time.time()
                for i in range(2, len(data), 2):
                    head, tool = ntpath.split(data[i])
                    #print(tool,data[i])
                    subprocess.check_output(
                        "curl --silent -u " + str(atf_username) + ":" + str(atf_password) + " -X GET " + str(
                            data[i]) + " --output " + str(path) + "\\" + str(tool), shell=True)
                end = time.time()
                zip_extract = (abs(start - end))
                zip_extract = ("{:05.2f}".format(zip_extract))
                print("Time Taken for All Tool >> {0} << TO Download {1} Seconds".format(tool_name, zip_extract))
                print("\n ALL Tool Downloaded Successfull to this Location {0}".format(path))
                sys.exit(0)

def download_tool_to_sut(tool_name=None,dest=None,all_tool=None):
    """
    tool_name :- name of the tool you wanted to download from the artifactory give the name mentioned in the xml_tool_info file
    dest :- destination of your tool to be downloaded by default /opt/APP/tools for Linux
            C:\BKC_PKG\tools for Windows
    all_tool :- Download all the tools under the project specified to a prefered location in the sut
    return :- cmd line that needs to be inserted into sut os ssh/serial provider along with timeout.
    """
    if (tool_url_extraction(xml_file_download=True) == True):
        if (all_tool == True):
            tree = ET.parse(xml_info_file)
            root = tree.getroot()
            tool_path = ""
            data = []
            for child in root.iter():
                for key, value in child.items():
                    data.append(value)
            start = time.time()
            sut_os = "curl --silent -u " + str(atf_username) + ":" + str(atf_password) + " -X GET "
            for i in range(2, len(data), 2):
                head, tool = ntpath.split(data[i])
                print(data[i])
                if dest:
                    if (os_type == 'Linux'):
                        sut_os += " -o "+str(dest)+"//"+str(tool)+" "+data[i]
                    else:
                        sut_os += " -o "+str(dest)+r"\\"+str(tool)+" "+data[i]
                else:
                    if (os_type == 'Linux'):
                        dest = "/opt/APP/tools"
                        sut_os +=  str(dest)
                    else:
                        dest = r"C:\BKC_PKG\tools"
                        sut_os += "\\"+str(dest)
                sut_os = str(sut_os)
            return sut_os
        else:
            ret = tool_url_extraction(tool_name)
            if (ret[0] == False):
                print("ATF TOOL XML Path Naming Issue")
            else:
                head, tool = ntpath.split(ret[1])
                if (dest == None):
                    if (os_type == 'Linux'):
                        dest = "/opt/APP/tools"
                        sut_os = "curl --silent -u " + str(atf_username) + ":" + str(atf_password) + " -X GET " + str(
                            ret[1]) + " --output " + str(dest) + "/" + str(tool)
                    else:
                        dest = r"C:\BKC_PKG\tools"
                        sut_os = "curl --silent -u " + str(atf_username) + ":" + str(atf_password) + " -X GET " + str(
                            ret[1]) + " --output " + str(dest) + "\\" + str(tool)
                else:
                    if (os_type == 'Linux'):
                        sut_os = "curl --silent -u " + str(atf_username) + ":" + str(atf_password) + " -X GET " + str(
                            ret[1]) + " --output " + str(dest) + "\\" + str(tool)
                    else:
                        sut_os = "curl --silent -u " + str(atf_username) + ":" + str(atf_password) + " -X GET " + str(
                            ret[1]) + " --output " + str(dest) + "/" + str(tool)
                return sut_os

def __download_file(path, dest=None):
    # type: (ArtifactoryPath,str) -> None
    """The file will save to your destination"""
    file_name = str(path).split('/')[-1]
    if file_name == '':
        file_name = str(path).split('/')[-2]
    if not dest:
        # If destination is appoint, use it
        dest = file_name
    if os.path.isdir(dest):
        dest = os.path.join(dest, file_name)
    with path.open() as fd:
        with open(dest, 'wb') as out:
            out.write(fd.read())

def __download_dir(path, dest=None):
    # type: (ArtifactoryPath,str) -> None
    """The directory will save to your destination"""
    if not dest:
        # If destination is not appoint, use its default name as destination
        dest = str(path).split('/')[-1]
        if dest == '':
            dest = str(path).split('/')[-2]
    if not os.path.exists(dest):
        os.mkdir(dest)

    for p in path:
        sub_name = str(p).split('/')[-1]
        if sub_name == '':
            sub_name = str(p).split('/')[-2]
        if p.is_dir():
            __download_dir(p, dest=os.path.join(dest, sub_name))
        else:
            __download_file(p, os.path.join(dest, sub_name))


def __upload_file(source, path, props=dict(), change=False):
    # type: (str,ArtifactoryPath,dict,bool) -> None
    """The file of destination will save to artifactory repository where your path points"""
    if not path.exists():
        path.mkdir()
        # If it is created by this operation, change its properties
        change = True
    if props and change:
        path.properties = props
    path.mkdir(exist_ok=True)
    path.deploy_file(source)


def __upload_dir(source, path, username, password, props=dict(), change=False):
    # type: (str,ArtifactoryPath,str,str,dict,bool) -> None
    """The directory of destination will save to artifactory repository where your path points"""
    if not path.exists():
        path.mkdir()
        change = True
    if props and change:
        path.properties = props
    path.mkdir(exist_ok=True)
    dir_list = os.listdir(source)
    url = str(path)
    if url[-1] != '/':
        url += '/'
    url += source.replace('\\', '/').split('/')[-1]
    path = ArtifactoryPath(url, auth=(username, password))
    for i in dir_list:
        sub_source = os.path.join(source, i)
        if os.path.isdir(sub_source):
            # Because it isn't root path, so change its properties
            __upload_dir(sub_source, path, username, password, props=props, change=True)
        else:
            __upload_file(os.path.join(source, i), path, props=props, change=True)


def download(url, username, password, dest=None):
    # type: (str,str,str,str) -> None
    """
    download artifact from Artifactory repo

    :param url: Artifact URL, it is mandatory. Both directory and file are accepted.
    :param username: user name used to login artifactory
    :param password: password for login
    :param dest: if dest is None, the artifact will be downloaded to the current folder and keep the original name. If dest is specified, the artifact will be saved in the specified folder.
    :raise Exception: if any error
    :return None: if the artifact is downloaded successfully
    """
    path = ArtifactoryPath(url, auth=(username, password))
    if path.is_dir():
        __download_dir(path, dest=dest)
    else:
        __download_file(path, dest=dest)

def upload(source, url, username, password, props=dict()):
    # type: (str,str,str,str,dict) -> None
    """
    upload artifact to Artifactory repo

    :param source: local artifact. both file and folder are accepted.
    :param url: Artifact URL, it is mandatory. Both directory and file are accepted.
    :param username: user name used to login artifactory
    :param password: password for login
    :param props: dict to save the properties of folder.
    :raise Exception: if any error
    :return None: if the artifact is uploaded successfully
    """
    path = ArtifactoryPath(url, auth=(username, password))
    if os.path.isdir(source):
        # If it is root path, don't change its properties
        __upload_dir(source, path, username, password, props=props, change=False)
    else:
        __upload_file(source, path, props=props, change=False)
