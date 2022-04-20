#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
INTEL CONFIDENTIAL
Copyright 2020 Intel Corporation All Rights Reserved.

The source code contained or described herein and all documents related to the source code
("Material") are owned by Intel Corporation or its suppliers or licensors. Title to the Material remains
with Intel Corporation or its suppliers and licensors. The Material contains trade secrets and
proprietary and confidential information of Intel or its suppliers and licensors. The Material is
protected by worldwide copyright and trade secret laws and treaty provisions. No part of the
Material may be used, copied, reproduced, modified, published, uploaded, posted, transmitted,
distributed, or disclosed in any way without Intel's prior express written permission.

No license under any patent, copyright, trade secret or other intellectual property right is granted to
or conferred upon you by disclosure or delivery of the Materials, either expressly, by implication,
inducement, estoppel or otherwise. Any license under such intellectual property rights must be
express and approved by Intel in writing.
"""
import sys
import json
import xml.etree.ElementTree as ET
from fnmatch import fnmatch
from posixpath import join as urljoin
import requests
# List of inline parameters which should be get from configuration files, example:
# CONFIG_PARAMS_MAP = {
#     'windows_installation': [
#         {'cfg_param': 'IPAddress', 'inline_param': 'dut_ip'},
#         {'cfg_param': 'CreationDate', 'inline_param': 'when_added'}
#     ]
# }

CONFIG_PARAMS_MAP = {
    'windows_installation': [],
    'linux_rhel_installation': [],
    'linux_centos_installation': [],
    'esxi_installation': [],
    'ifwi_flashing': [],
    'bmc_banino_flashing': [],
    'bmc_redfish_flashing': [],
    'cpld_flashing': []
}

# Dictionaries helpers


def find_by_key(obj: dict, key: str) -> str:
    """ Get dictionary value by the given key. """
    if key in obj:
        return obj[key]
    for k, v in obj.items():
        if isinstance(v, dict):
            item = find_by_key(v, key)
            if item is not None:
                return item.get('string', item) if isinstance(item, dict) else item
        elif isinstance(v, list):
            for list_item in v:
                item = find_by_key(list_item, key)
                if item is not None:
                    return item


def pprint_dict(parameters: dict) -> str:
    """ Pretty print dictionary object. """
    return json.dumps(parameters, indent=4)


def get_config_params(task: str, parameters: dict) -> str:
    """ Get parameters from configuration files and append arguments to the tasks commandline. """
    cmd = []
    try:
        for parameter in CONFIG_PARAMS_MAP[task]:
            cfg_param = parameter.get('cfg_param')
            inline_param = parameter.get('inline_param')
            cmd.append('--{parameter} {value}'.format(parameter=inline_param.upper(),
                                                      value=find_by_key(parameters, cfg_param)))
    except KeyError:
        print('Undefined task: {} in CONFIG_PARAMS_MAP.'.format(task.upper()))
    return ' '.join(cmd)


def serialize(parameters: dict) -> str:
    """ Format dictionary entries as commandline arguments. """
    cmd = []
    for k, v in parameters.items():
        cmd.append('--{parameter} "{value}"'.format(parameter=k.upper(), value=v))
    return ' '.join(cmd)


def merge_dicts(dict1: dict, dict2: dict) -> None:
    """ Update dict1 with dict2 entries (default update method failed with nested keys). """
    for k in dict2:
        if k in dict1 and isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
            merge_dicts(dict1[k], dict2[k])
        else:
            dict1[k] = dict2[k]


# XML helpers


def get_manifest(input_parameters: dict) -> str:
    """ Get products manifest XML file with Artifactory data etc. """
    product_manifest_path = find_by_key(input_parameters, 'TestedComponentBuildsLocalPaths')

    if product_manifest_path:
        try:
            tree = ET.parse(product_manifest_path)
            root = tree.getroot()
        except FileNotFoundError:
            print('ERROR: Product\'s XML manifest file not found.')
            sys.exit(5)
    else:
        print('ERROR: Product\'s XML manifest path not found.')
        sys.exit(5)
    return root


def get_pkg(pkg_type: str, input_parameters: dict) -> str:
    """
    Get the OS or firmware package from XML manifest (SWPackage has specific XML tag attribute: SWpackage).
    Windows image has the type attribute: WIM.
    Handled pkg_type: win_os (Windows), os (other OSes, Linux), sft (software packages).
    """
    manifest = get_manifest(input_parameters)
    try:
        if pkg_type == 'win_os':
            return [image.attrib.get('artifactory') for image in manifest.iter('image')
                    if image.attrib.get('type') == 'wim' and image.attrib.get('tag') != 'SWpackage'][0]
        else:
            tag = ''
            if pkg_type == 'sft':
                tag = 'SWpackage'
            return [image.attrib.get('artifactory') for image in manifest.iter('image')
                    if image.attrib.get('tag') == tag][0]
    except IndexError:
        print('ERROR: Image package was not found in XML manifest.')
        sys.exit(5)


def get_project_pkg(project: str, input_parameters: dict) -> str:
    """ Get the flashing package from XML manifest. """
    manifest = get_manifest(input_parameters)
    try:
        pkg_path = [product.attrib.get('artifactory')
                    for product in manifest.findall("project[@name='{project}']".format(project=project))][0]
        pkg_archive = get_project_pkg_archive(pkg_path)
        return urljoin(pkg_path, pkg_archive)
    except IndexError:
        print('ERROR: Artifactory package path for {} was not found in XML manifest.'.format(project))
        sys.exit(5)


def get_project_pkg_archive(pkg_path: str) -> str:
    """ Find the flashing package in Artifactory (7z or zip). """
    url = '{}?list&deep=1&listFolders=1'.format(pkg_path.replace('/artifactory/', '/artifactory/api/storage/'))
    headers = {'X-JFrog-Art-Api': 'AKCp8hyj3ZahzTN7ncNdvP2z5ZGd83jPMXVWxYu7JRkeJsRNAUZgxA1XBwQCSLbZcjPDXBXXb'}
    proxies = {
        'http': 'http://proxy-chain.intel.com:911',
        'https': 'https://proxy-chain.intel.com:912',
        'ftp': 'http://proxy-chain.intel.com:911'
    }

    archives_list = []
    try:
        print('Calling Artifactory API (get firmware package): {}'.format(url))
        response = requests.get(url, headers=headers, proxies=proxies)
        response.raise_for_status()
        result = json.loads(response.text.encode('utf8'))

        for package in result.get('files'):
            if any(fnmatch(package['uri'], pattern) for pattern in ['*.7z', '*.zip']):
                archives_list.append(package.get('uri').replace('/', ''))
    except (Exception, requests.exceptions.HTTPError) as err:
        print(err)
        sys.exit(5)

    if len(archives_list) == 0:
        print('ERROR: Firmware package (7z/zip) not found here: {}'.format(pkg_path))
        sys.exit(5)
    elif len(archives_list) == 1:
        return archives_list[0]
    else:
        print('ERROR: More than one firmware package (7z/zip) found here: {}'.format(pkg_path))
        sys.exit(5)
