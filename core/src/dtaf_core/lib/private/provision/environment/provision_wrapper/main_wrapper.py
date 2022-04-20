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
import argparse
import subprocess
from utils import pprint_dict
from input_parser import InputFilesParser
from output_parser import OutputCommandParser


def prepare_command():
    """ Prepare command to run the provisioning script. """

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--task', action='store', dest='task', help='Task to be performed')
    parser.add_argument('-c', action='store', dest='config_files', help='List of configuration files')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose the parameters')
    parser.add_argument('-o', help='Output path defined in test case scenario (unused in provision wrapper)')
    args = parser.parse_args()

    task = args.task
    verbose = args.verbose
    config_files = args.config_files

    print("Running main wrapper... Task: {}".format(task))

    if verbose:
        print("Input command: {}".format(' '.join(sys.argv)))

    if config_files:
        input_parser = InputFilesParser(config_files)
    else:
        print("ERROR: Missing configuration files list parameter: -c")
        sys.exit(5)

    if verbose:
        print("Parsed input parameters: \n{}".format(pprint_dict(input_parser.input_parameters)))

    output_parser = OutputCommandParser(task.lower(), input_parser.input_parameters)
    output_command = output_parser.output_command

    print("Output command for task {task}: \n{command}".format(task=task.upper(), command=output_command))
    return output_command


def call_provision_process(command):
    """ Execute the provisioning script. """
    result = subprocess.run(command, shell=True, check=False, cwd='..')
    return result.returncode


if __name__ == '__main__':
    provision_command = prepare_command()
    return_code = call_provision_process(provision_command)
    sys.exit(return_code)
