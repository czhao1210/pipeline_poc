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
import six
from typing import Union
from abc import ABCMeta, abstractmethod
from dtaf_core.providers.base_provider import BaseProvider


@six.add_metaclass(ABCMeta)
class SiliconDebugProvider(BaseProvider):
    """
    Interfaces with the SUT's JTAG debug port to abstract the various debug APIs (DAL, OpenIPC, etc).

    This class is for basic debugging only. See the SiliconRegProvider for more sophisticated DFx access.
    """

    DEFAULT_CONFIG_PATH = "suts/sut/providers/silicon_debug"

    def __init__(self, cfg_opts, log):
        super(SiliconDebugProvider, self).__init__(cfg_opts, log)

    def __enter__(self):
        return super(SiliconDebugProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(SiliconDebugProvider, self).__exit__(exc_type, exc_val, exc_tb)

    @abstractmethod
    def is_halted(self):
        # type: () -> bool
        """
        Check if SUT is halted (probe mode active).

        :return: True if the SUT is halted, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def is_powered(self):
        # type: () -> bool
        """
        Check if SUT is powered on from the perspective of the debugger (not in S5, G3, etc.).

        :return: True if the SUT has power, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def halt(self):
        # type: () -> None
        """
        Halt and enter probe mode on all threads.

        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def go(self):
        # type: () -> None
        """
        Exit probe mode and resume execution across all threads.

        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def forcereconfig(self):
        # type: () -> None
        """
        reset ITP XDP interface

        :return: None
        """
        raise NotImplementedError


    @abstractmethod
    def start_log(self, log_file_name, mode='w'):
        # type: (str, str) -> None
        """
        Invoke log function to start the logging for debug command outputs.
        TODO: this is work-around to overcome few cscript commands not returning output and rather they log the
        TODO: output to log file. Irrespective of debugger interface, logs are logged using IPCCLI log functions.

        :param log_file_name: Path to log file name where debug commands output will be logged.
        :param log_file_name: log file path name where messages will be logged.
        :param mode: log mode 'w' (default) - overwrite, 'a' - append
        :raise: RuntimeError - If ipccli is not installed

        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def stop_log(self):
        # type: () -> None
        """
        Invoke log function to stop the logging for debug command outputs.

        :raise: RuntimeError - If ipccli is not installed
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def cpuid(self, register, leaf, subleaf=None, squash=False):
        # type: (str, int, int, bool) -> Union[list, int]
        """
        Execute the CPUID instruction from the debugger.

        See dtaf_core.lib.silicon.CPUID for available registers.

        :raises RegisterInconsistencyException: If squash is True and the CPUID value is not the same across all threads
        :param register: String which specifies the register with the base opcode (eax, ebx, etc).
        :param leaf: CPUID leaf value
        :param subleaf: CPUID subleaf value
        :param squash: If True, will check that all threads returned the same value, and return that single value.
                       Otherwise, a list of each thread's result will be returned.
        :return: Result of the CPUID command (list if squash is False, int if squash is True)
        """
        raise NotImplementedError

    @abstractmethod
    def msr_read(self, msr_address, squash=False):
        # type: (int, bool) -> Union[list, int]
        """
        Read MSR values at the specified address across all threads.

        If the MSR is package level, consider using msr_read_and_verify, which will return a single value and raise an
        exception if the value is not consistent across all threads.

        :raises RegisterInconsistencyException: If squash is True and the MSR value is not the same across all threads
        :param msr_address: Integer with the address of the MSR to read
        :param squash: If True, will check that all threads returned the same value, and return that single value.
                       Otherwise, a list of each thread's result will be returned.
        :return: Dictionary mapping threads to the read values of the MSR
        """
        raise NotImplementedError

    @abstractmethod
    def msr_write(self, msr_address, value, thread=None, no_readback=False):
        # type: (int, int, int, bool) -> None
        """
        Write MSR value into the specified thread.

        :raises ReadBackException: If no_readback is False and data doesn't match MSR value after writing it.
        :param msr_address: Integer with the address of the MSR to write
        :param value: Integer with the value to write into the specified MSR
        :param thread: Index to write "value" into. Default is all threads.
        :param no_readback: If True, will not read the value of the MSR back to verify that write occurred.
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def reset_break(self, state):
        # type: (bool) -> None
        """
        Enable or disable reset break on all threads

        :param state: If True, will enable reset break. Will disable reset break otherwise.
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def init_break(self, state):
        # type: (bool) -> None
        """
        Enable or disable init break on all threads

        :param state: If True, will enable init break. Will disable init break otherwise.
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def mem_read(self, address, size, thread_index=None):
        # type: (str, int, int) -> int
        """
        Read the value stored in memory at the given address.

        :param address: Hex string conforming to the DAL/OpenIPC address format.
        :param size: Size in bytes (up to 8) of the value at address.
        :param thread_index: Thread index to use to read memory. If None, uses the first active thread (recommended)
        :return: Value contained at address.
        """
        raise NotImplementedError

    @abstractmethod
    def mem_write(self, address, size, data, thread_index=None, no_readback=False):
        # type: (str, int, int, int, bool) -> None
        """
        Write data to memory at the given address.

        :raises ReadBackException: If no_readback is False and data is not found at address after writing it.
        :param address: Hex string conforming to the DAL/OpenIPC address format.
        :param size: Size in bytes (up to 8) of the value at address.
        :param data: Data to write into memory.
        :param thread_index: Thread index to use to write memory. If None, uses the first active thread (recommended)
        :param no_readback: if true, don't check for a match after writing data to memory
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def flush_cache(self, thread_index=None):
        # type: (int) -> None
        """
        Flush the cache of the specified thread (default is first active thread).

        :param thread_index: If specified with an integer, will target a specific thread for cache flushing.
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def reset_target(self):
        # type: () -> None
        """
        Reset the SUT using the debugger.

        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def pulse_pwr_good(self):
        # type: () -> None
        """
        Reset the SUT by using the debugger to force the PWRGOOD signal to momentarily de-assert.

        :return: None
        """
        raise NotImplementedError
