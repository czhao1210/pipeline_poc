#! /usr/bin/python2
"""
TCF Driver to run DTAF test cases in-band on SUTs.
"""
import inspect
import os
import re

import six
import tcfl
import tcfl.pos

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.os_lib import LinuxDistributions
from dtaf_core.lib.private.driver_config.tcf_driver_config import TcfDriverConfig
from dtaf_core.lib.tcf.tcf_deploy import TcfDeploy


@tcfl.tc.interconnect('ipv4_addr')
@tcfl.tc.target('pos_capable')
class DTAFRemoteDriver(tcfl.pos.tc_pos0_base):
    """
    Driver to run DTAF testcases on a Linux SUT using the TCF client as the test host.

    dtaf_core/src (and dtaf_content if needed) should be in PYTHONPATH before running this.
    """

    # Use Clear Linux as the default execution OS.
    image_requested = os.environ.get("IMAGE", TcfDeploy.IMAGE_BASE_NAMES[LinuxDistributions.ClearLinux])

    # DTAF_CORE test case regex
    dtaf_core_python_tc_regex = re.compile(r"^.*/dtaf_core.*/tests.*\.py$")

    # DTAF_CONTENT test case regex
    dtaf_python_file_regex = re.compile(r"^.*/dtaf_content.*\.py$")

    def __init__(self, name, tc_file_path, origin, dtaf_tests):
        super(DTAFRemoteDriver, self).__init__(name, tc_file_path, origin)

        # Save test list for execution
        self.tests = dtaf_tests
        if len(self.tests) < 1:
            raise tcfl.tc.blocked_e("No DTAF test classes provided that inherit from "
                                    "dtaf_core.lib.base_test_case.BaseTestCase!")

    def eval_0(self, ic, target):
        """
        Run DTAF-specific setup and enable SSH on the SUT to prepare for running DTAF tests.

        :param ic: TCF target network object
        :param target: TCF target object
        :return: None
        """
        dtaf_prov = TcfDeploy.get_deploy_cls(self.image_requested.split(":")[0])
        dtaf_prov.setup_os(ic, target)

    def eval_1(self, ic, target):
        """
        Inject runtime settings into DTAF and execute all test cases found.

        :param ic: TCF target network object
        :param target: TCF target object
        :raises: tcfl.tc.failed_e if any test in the list fails
        :return: None
        """
        # Inject dynamic parameters that are static in DTAF
        dtaf_prov = TcfDeploy.get_deploy_cls(self.image_requested.split(":")[0])
        dtaf_prov.setup_target_attrs(ic, target)
        TcfDriverConfig._targets = [target]
        TcfDriverConfig._interconnects = [ic]

        # Execute DTAF tests found in module
        results = {}
        for test in self.tests:
            dtaf_args = []  # TODO: Capture command line args meant for dtaf
            results[test.__name__] = test.main(dtaf_args)

        if not all(test_result for test_result in results.values()):
            # TODO: Pull in fail log
            raise tcfl.tc.failed_e("Test case {} failed!".format(self.name), {"test_log": "See DTAF log for details"})

    @staticmethod
    def get_dtaf_module(module_name, file_path):
        """
        Attempts to import the file at file_path as a Python module and assign it the name module_name.

        :param module_name: Name to assign to the imported module
        :param file_path: Path to the file to import
        :return: Python module object imported from file_path
        """
        if six.PY2:
            import imp
            dtaf_tc_module = imp.load_source(module_name, file_path)
        else:  # TODO: TCF doesn't support Py3 yet - this code path can't be tested until it does.
            import importlib.machinery
            dtaf_tc_module = importlib.machinery.SourceFileLoader(module_name, file_path).load_module()
        return dtaf_tc_module

    @staticmethod
    def get_dtaf_tests(dtaf_module):
        """
        Get the DTAF test classes from the given Python module.

        :param dtaf_module: Arbitrary Python module to be scanned for DTAF tests.
        :return: List of Python classes from dtaf_module that inherit from dtaf_core.lib.base_test_case.BaseTestCase
        """
        dtaf_classes = []
        for cls_name, cls in inspect.getmembers(dtaf_module):
            if cls in BaseTestCase.SUBTYPES.values() and cls != BaseTestCase and not inspect.isabstract(cls):
                dtaf_classes.append(cls)
        return dtaf_classes

    @classmethod
    def is_testcase(cls, path, from_path, tc_name, subcases_cmdline):
        """
        Returns the list of DTAF test classes in the file at "path".

        A DTAF test class is defined as a Python class that inherits from dtaf_core.lib.base_test_case.BaseTestCase.
        This will only try to import modules in the dtaf_core and dtaf_content git repositories to minimize the chance
        of import mishaps.
        :param path: path and filename of the file that has to be examined; this is always a regular file (or link)
        :param from_path: source command line argument this file was found on
        :param tc_name: testcase name the core has determine based on the path and subcases specified
        :param subcases_cmdline: list of subcases the user has specified in the command line
        :return: list of testcases found in *path*, empty if none found or file not recognized / supported.
        """
        tc = []
        if cls.dtaf_python_file_regex.search(os.path.abspath(path)) or \
                cls.dtaf_core_python_tc_regex.search(os.path.abspath(path)):
            # Module is in a dtaf repo - import the module and get the tests
            dtaf_module = cls.get_dtaf_module("dtaf_tcf", os.path.abspath(path))
            dtaf_tests = cls.get_dtaf_tests(dtaf_module)
            tc = [] if len(dtaf_tests) < 1 else [cls(tc_name, path, from_path, dtaf_tests)]
        return tc
#import traceback
#traceback.print_stack()
tcfl.tc.tc_c.driver_add(DTAFRemoteDriver)
