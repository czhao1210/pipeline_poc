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
from abc import ABCMeta

from dtaf_core.providers.base_provider import BaseProvider
from six import add_metaclass


@add_metaclass(ABCMeta)
class SimicsProvider(BaseProvider):
    """
    Class used to deploy sut and host before testing

    This class cannot be used directly, instead, this interface is applied to the subclasses, with a different subclass
    communication (SOL, Serial) This makes the dependency on specific hardware setups easier to
    identify.
    """
    DEFAULT_CONFIG_PATH = "suts/sut/providers/deployment"

    def __init__(self, cfg_opts, log):
        """
        Create a new DeploymentProvider object

        :param self._log: Logger object to use for debug and info messages
        :param cfg_opts: Dictionary of configuration options for execution environment.
        """
        super(SimicsProvider, self).__init__(cfg_opts, log)

    def launch_simics(self, configuration, simics_script):
        """
        modify hardware configuration then launch simics instance

        :param configuration: dictionary to set hardware configuration in (key,value) format
            simics supports below info (see simics docs for more details)
            (bios, disk_image, n_cpu, n_threads, mem_config etc.)
            to launch simics succesfully, bios and image information is mandatory.

            in current simics package, $bios and $disk_image are required. Otherwise, simics can't be launched.

        :param simics_script: simics script to launch (e.g. golden script)
        :raise FileNotFound: if simics_script not found
        :raise ConnectionFailureException: if fail to connect simics

        :return:
            simics_instance: if successful
            None: if failed

        """
        raise NotImplementedError

    def shutdown_simics(self):
        # type: () -> None
        """
        shutdown simics instance (kill or terminate process)

        :param simics_instance: simics Instance created

        :return:
            None
        """
        raise NotImplementedError


    def run_simics_command(self, command_line, timeout, end_pattern=None):
        """
        run command in simics environment

        :param simics_instance: simics instance
        :param command_line: command line to input. it should not be empty
        :param timeout: timeout to return
        :raise FileNotFound: if simics_script not found
        :raise ConnectionFailureException: if fail to connect simics
        :raises OsCommandTimeoutException: If command fails to complete before the timeout elapses.
        :raises OsCommandException: If command fails to complete for a non-timeout reason.
                                    Note: This is not raised if the command fails, only if it fails to complete for some
                                    other reason, for example, if the environment has a problem or if the SUT's OS
                                    unexpectedly dies.
        :return: OsCommandResult instance with the command execution results.
        """
        raise NotImplementedError


    def run_simics_test_script(self, configuration, simics_script, end_pattern_list, timeout):
        """
        run command in simics environment


        :param configuration: dictionary to set hardware configuration in (key,value) format
            simics supports below info (see simics docs for more details)
            (bios, disk_image, n_cpu, n_threads, mem_config etc.)
            to launch simics succesfully, bios and image information is mandatory.

            in current simics package, $bios and $disk_image are required. Otherwise, simics can't be launched.
        :param simics_script: simics_script to execute. it should not be empty
        :param end_pattern_list: stop execution when any pattern in list matches
        :raise FileNotFound: if simics_script not found
        :raise ConnectionFailureException: if fail to connect simics
        :raises OsCommandTimeoutException: If command fails to complete before the timeout elapses.
        :raises OsCommandException: If command fails to complete for a non-timeout reason.
                                    Note: This is not raised if the command fails, only if it fails to complete for some
                                    other reason, for example, if the environment has a problem or if the SUT's OS
                                    unexpectedly dies.
        :return: OsCommandResult instance with the command execution results.
        """
        raise NotImplementedError


