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
import logging
import datetime
import json
from xml.etree import ElementTree
from dtaf_core.lib.test_context import TestContext
from dtaf_core.lib.dtaf_constants import Framework


def log_cleanup(logger_obj):
    # type: (logging.Logger) -> None
    for handler in logger_obj.handlers:
        handler.close()
        logger_obj.removeHandler(handler)


def create_logger(file_base_name, console_debug, cfg_opts):
    # type: (str, bool, ElementTree.Element) -> logging.Logger
    """Create logger object for the test to use."""
    log_dir_name = os.path.join(cfg_opts.find("log").attrib["path"],
                                file_base_name + "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S"))
    log_file_name = os.path.join(log_dir_name, "dtaf_log.log")
    if not os.path.exists(log_dir_name):
        os.makedirs(log_dir_name)

    test_log = logging.getLogger(file_base_name)
    test_log.setLevel(logging.DEBUG)

    # Define message format
    piv_log_fmt = logging.Formatter(
        fmt=u'%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        datefmt=u'%m/%d/%Y %I:%M:%S %p')

    # Create streams
    stdout_stream = logging.StreamHandler(sys.stdout)
    stdout_stream.setLevel(logging.DEBUG if console_debug else logging.INFO)
    stdout_stream.setFormatter(piv_log_fmt)
    file_stream = logging.FileHandler(log_file_name, mode='w', encoding='utf-8')
    file_stream.setLevel(logging.DEBUG)
    file_stream.setFormatter(piv_log_fmt)

    # Add handlers to logger
    test_log.addHandler(stdout_stream)
    test_log.addHandler(file_stream)

    # Push cleanup method onto the test context
    TestContext().callback(log_cleanup, test_log)
    test_log.info("Results are saved in %s", log_dir_name)
    # Return log object
    return test_log

def get_log_file_dir(log_obj):
    """Gets the file handler from logger object"""
    for handler in log_obj.handlers:
        if str(type(handler)) == "<class 'logging.FileHandler'>":
            return os.path.split(handler.baseFilename)[0]

def create_cc_failure_results_json(log_dir, reasons=None):
    """Creates the failure_results.json file for cc

    @param log_dir: log directory
    @param reasons: list of errors to create json file
    """
    if reasons:
        filename = Framework.RESULT_FAILURE_REASON_FILE if not log_dir else os.path.join(log_dir, Framework.RESULT_FAILURE_REASON_FILE)
        with open(filename, "w") as f:
            reasons_dict = []
            for reason in reasons:
                reasons_dict.append({"Message" : reason})
            f.write(json.dumps(reasons_dict, indent=4))
