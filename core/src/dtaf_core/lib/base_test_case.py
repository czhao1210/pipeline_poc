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
import six
import logging
import argparse
import platform
import dtaf_core.lib.log_utils as log_utils
import dtaf_core.lib.registry as registry
from xml.etree import ElementTree
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.lib.test_context import TestContext
from dtaf_core.lib.dtaf_config_parser import DtafConfigParser


@six.add_metaclass(registry.AbstractMetaRegistry)
class BaseTestCase(object):
    """
     A class that takes contains base test case function definitions and test execution flow for all PIV test content.
    """

    # Test cases can override this with a list of TCF-compliant requirement specs. Before system allocation, the TCF
    # driver AND them together (and with 'pos_capable'). Other deploy frameworks can also inspect this if desired.
    # TODO: Determine if DTAF provides a translation for other formats. Could write our own config spec, but seems
    # TODO: easier to use the TCF solution if it will be the primary execution engine for DTAF.
    config_requirements = []
    _FAIL_INFO = "<Test Result: Test Failed>"
    _PASS_INFO = "<Test Result: Test Passed>"

    def __init__(self, test_log, arguments, cfg_opts):
        # type: (logging.Logger, argparse.Namespace, ElementTree.Element) -> None
        self._log = test_log
        self._args = arguments
        self._cfg = cfg_opts

    def prepare(self):
        # type: () -> None
        """Method called when a test is initiated to perform setup and initialization tasks"""
        pass

    def execute(self):
        # type: () -> bool
        """
        Method with the main test logic

        :return: True if test evaluation passed, False (or thrown exception) otherwise.
        """
        pass

    def cleanup(self, return_status):
        # type: (bool) -> None
        """Clean-up method called when a script ends"""
        if return_status:
            self._log.info(self._PASS_INFO)
        else:
            self._log.error(self._FAIL_INFO)

    @classmethod
    def add_arguments(cls, parser):
        # type: (argparse.ArgumentParser) -> None
        """
        Add class' arguments to parser.

        Sub-classes MUST call super.add_arguments(parser) or ensure config is overridden for required parameters.
        :param parser: ArgumentParser object which can have arguments added to it.
        :return: None
        """
        pass

    @classmethod
    def parse_arguments(cls, arg_source, cfg_file_default):
        # type: (list, str) -> argparse.Namespace
        """
        Parse command line arguments from sys.argv.

        :param arg_source: List of strings to pull arguments from. Will use sys.stdin if None.
        :param cfg_file_default: Path to the default configuration file (users can override if they so choose).
        :return: Parsed arguments from sys.argv.
        """
        # Create ArgumentParser and add default arguments
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('--cfg_file', default=cfg_file_default, help="Path to the system's config file.")
        arg_parser.add_argument('--project_dir', help="Override config file path to project directory")
        arg_parser.add_argument('--console_debug', action="store_true", default=False,
                                help="Enable debug output to console.")
        arg_parser.add_argument('--reset_defaults', default=True,
                                help="Enable/Disable Loadbiosdefaults for a test")

        # Add user-specified arguments
        cls.add_arguments(arg_parser)

        # Return parsed arguments in a Namespace object
        return arg_parser.parse_args(args=arg_source)

    @classmethod
    def parse_config_file(cls, test_args):
        """
        Parse configuration file and return configuration options object.

        :return: Parsed configuration file.
        """
        return ElementTree.parse(os.path.expanduser(test_args.cfg_file)).getroot()

    @classmethod
    def parse_config_sources(cls, test_args, config_sources):
        """
        Parse configuration file and return configuration options object.

        :return: Parsed configuration file.
        """
        if config_sources is None:
            config_sources = []
        if os.path.isfile(test_args.cfg_file):
            # DTAF bootstrap xml has the lowest priority, as DTAF has no configuration management built in and is not a
            # fully-featured execution framework.
            config_sources.append((os.path.splitext(test_args.cfg_file)[1].lstrip('.'),
                                   os.path.expanduser(test_args.cfg_file)))
        if not config_sources:
            raise RuntimeError("No configuration data was provided! "
                               "Ensure that the provided config file exists (or that the execution framework is "
                               "providing config info)!")
        return DtafConfigParser.get_config_opts(config_sources)

    @classmethod
    def main(cls, arg_source=None):
        # type: (list) -> bool
        """
        Main function called when a script is initiated

        :param arg_source: List of strings to pull arguments from. Will use sys.stdin if None (default)
        :return: True if test evaluation passed, False (or thrown exception) otherwise.
        """
        # Assign the config file path based on the current OS
        exec_os = platform.system()
        try:
            cfg_file_default = Framework.CFG_FILE_PATH[exec_os]
        except KeyError:
            print("Error - execution OS " + str(exec_os) + " not supported!")
            raise RuntimeError("Error - execution OS " + str(exec_os) + " not supported!")

        # Parse command line arguments (if any)
        arguments = cls.parse_arguments(arg_source, cfg_file_default)

        # Parse the test's configuration file
        config_parameters = cls.parse_config_file(arguments)

        test_result = False
        with TestContext():
            # Create a log file
            test_log = log_utils.create_logger(cls.__name__, arguments.console_debug,
                                               config_parameters)  # TODO: Replace with ProviderFactory
            log_dir = log_utils.get_log_file_dir(test_log)
            test_log.debug("Log dir: %s", log_dir)
            # Construct an instance of the test class
            try:
                tester = cls(test_log, arguments, config_parameters)
            except Exception as e:
                test_log.exception(str(e))
                test_log.error(cls._FAIL_INFO)
                log_utils.create_cc_failure_results_json(log_dir, [str(e)])
                raise

            # Setup test
            test_log.info("Executing test setup...")
            try:
                tester.prepare()
            except Exception as pe:
                exceptions = []
                test_log.exception(pe)
                test_log.info("Test preparation failed. Running cleanup...")
                exceptions.append(str(pe))
                try:
                    tester.cleanup(False)
                except Exception as e:
                    test_log.error("Error in cleanup: " + str(e))
                    exceptions.append(str(e))
                log_utils.create_cc_failure_results_json(log_dir, exceptions)
                raise

            # Execute test
            test_log.info("Test setup complete. Executing test...")
            try:
                test_result = tester.execute()
            except Exception as e:
                test_log.exception(e)
                log_utils.create_cc_failure_results_json(log_dir, [str(e)])
                raise
            finally:
                test_log.info("Test execution complete. Running cleanup...")
                try:
                    tester.cleanup(test_result)
                except Exception as e:
                    test_log.error("Error in cleanup: " + str(e))
                    log_utils.create_cc_failure_results_json(log_dir, [str(e)])
                    raise

        return test_result


if __name__ == '__main__':
    print("This module does not have any tests to execute.")
    sys.exit(Framework.TEST_RESULT_FAIL)
