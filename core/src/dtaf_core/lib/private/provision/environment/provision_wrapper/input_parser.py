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
import os
import fnmatch
import json
import xmltodict
from utils import find_by_key, merge_dicts

# The list of configuration files which should not be parsed, ex. to avoid overriding (asterisks are supported).
CONFIGS_BLACKLIST = []


class Config:
    """
    Superclass that represents configuration file from input (XML or JSON).
    """
    parameters = {}

    def __init__(self, config_file):
        self.config_file = config_file

    @property
    def _is_config_allowed(self) -> bool:
        for config in CONFIGS_BLACKLIST:
            if fnmatch.fnmatch(os.path.basename(self.config_file), config):
                return False
        return True

    def parse(self) -> None:
        """ Dispatch input parameter class parser according to its type."""
        if not self._is_config_allowed:
            print('Skipping config: {}'.format(self.config_file))
            return

        _, filetype = os.path.splitext(self.config_file)
        if filetype == '.xml':
            config = XMLConfig(self.config_file)
            self.parameters = config.parse(node='anyType')
        elif filetype == '.json':
            config = JSONConfig(self.config_file)
            self.parameters = config.parse()


class XMLConfig(Config):
    """
    Subclass that represents XML configuration file.
    """
    def parse(self, node=None) -> str:
        msg = 'Parsing config: {}'.format(self.config_file)
        if node:
            msg += ' (node: {})'.format(node)
        print(msg)

        with open(self.config_file) as cfg:
            doc = xmltodict.parse(xml_input=cfg.read(), encoding='utf-8', xml_attribs=False)
        if node:
            return find_by_key(doc, node)
        return doc


class JSONConfig(Config):
    """
    Subclass that represents JSON configuration file.
    """
    def parse(self) -> dict:
        print('Parsing config: {}'.format(self.config_file))
        with open(self.config_file) as cfg:
            data = json.load(cfg)
        return data


class InputFilesParser:
    """
    Creates the union of all configuration files as a dictionary.
    Overrides oldest key value if exists.
    """

    files_separator = ';'
    input_parameters = {}

    def __init__(self, config_files: str) -> None:
        print("Running configuration files parser...")
        for config_file in config_files.split(self.files_separator):
            config = Config(config_file)
            config.parse()
            merge_dicts(self.input_parameters, config.parameters)
