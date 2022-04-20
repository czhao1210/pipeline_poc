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
from dtaf_core.lib.exceptions import DebuggerException, RegisterInconsistencyException, ReadBackException
from dtaf_core.providers.silicon_debug_provider import SiliconDebugProvider
from dtaf_core.lib.dtaf_constants import DebuggerInterfaceTypes
from dtaf_core.lib.silicon import CPUID
from time import sleep


class XdpSiliconDebugProvider(SiliconDebugProvider):
    """
    Class that communicates with the SUT's JTAG port using a DAL-compliant debug tool (ITPII or OpenIPC).
    """

    SUPPORTED_XDP_INTERFACES = [DebuggerInterfaceTypes.ITP, DebuggerInterfaceTypes.OPENIPC]

    def __init__(self, cfg_opts, log):
        super(XdpSiliconDebugProvider, self).__init__(cfg_opts, log)
        self._debugger_type = self._config_model.driver_cfg.debugger_type
        if self._debugger_type not in self.SUPPORTED_XDP_INTERFACES:
            raise RuntimeError("Unsupported XDP interface {}! Choices are {}.".format(self._debugger_type,
                                                                                      self.SUPPORTED_XDP_INTERFACES))

    def __enter__(self):
        # Establish connection to the ITP master frame when entering the test execution context
        if self._debugger_type == DebuggerInterfaceTypes.ITP:
            try:
                import itpii
            except ImportError:
                raise ImportError("ITPII Python library is not available! Please check configuration.")
            self.itp = itpii.baseaccess()

        elif self._debugger_type == DebuggerInterfaceTypes.OPENIPC:
            try:
                import ipccli
            except ImportError:
                raise ImportError("IPCCLI Python library is not available! Please check configuration.")
            # Use OpenIPC's DAL backwards compatibility
            self.itp = ipccli.baseaccess()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Terminate connection to the ITP master frame when exiting the test execution context
        try:
            if self.is_halted():
                self.go()
        except Exception:
            self._log.exception("Couldn't resume the CPU! System state could be corrupt.")
            raise
        finally:
            if self._debugger_type == DebuggerInterfaceTypes.ITP:
                self.itp.terminate()
            self.itp = None

    def is_halted(self):
        return bool(self.itp.cv.ishalted)

    def is_powered(self):
        return bool(self.itp.cv.targpower)

    def halt(self):
        self.itp.halt()

    def go(self):
        self.itp.go()

    def forcereconfig(self):
        self.itp.forcereconfig()

    def halt_and_check(self):
        """
        Attempt to halt the platform, and check if halted
        If some issues occur - attempt to recover with forcereconfig

        :param sdp_obj: the sdp object that queries or sets the msr

        """
        # Halt system
        itp_halt_delay_sec = 5
        try:
            self.halt()
            sleep(itp_halt_delay_sec)
            if not self.is_halted():
                self._log.info("Halt Failed - attempting forcereconfig()")
                self.forcereconfig()
                sleep(itp_halt_delay_sec)
                self.halt()
            else:
                self._log.info("Platform halted successfully")
        except Exception as ex:
            self._log.info("Running forcereconfig to attempt recovery from halt exception:{}".format(ex))
            self.forcereconfig()
            self.halt()

    def start_log(self, log_file_name, mode='w'):
        # type: () -> None
        """
        Invoke log function to start the logging for debug command outputs.
        TODO: this is work-around to overcome few cscript commands not returning output and rather they log the
        TODO: output to log file. Irrespective of debugger interface, logs are logged using IPCCLI log functions.

        :param log_file_name: log file path name where messages will be logged.
        :param mode: log mode 'w' (default) - overwrite, 'a' - append
        :raise: RuntimeError - If ipccli is not installed

        :return: None
        """
        try:
            from ipccli.stdiolog import log
            log(log_file_name, mode)
        except ImportError:
            raise ImportError("IPCCLI Python library is not available! Please check configuration.")

    def stop_log(self):
        # type: () -> None
        """
        Invoke log function to stop the logging for debug command outputs.

        :return: None
        """
        try:
            from ipccli.stdiolog import nolog
            nolog()
        except ImportError:
            raise ImportError("IPCCLI Python library is not available! Please check configuration.")

    def cpuid(self, setup_reg, leaf, subleaf=None, squash=False):
        if setup_reg not in CPUID.REGISTERS:
            raise ValueError("Register {} is not a valid CPU ID register.".format(setup_reg))
        if not self.is_halted():
            raise DebuggerException("Tried to execute CPUID instruction without halting!")

        cpuid_func_name = "cpuid_" + setup_reg
        cpuid_values = []
        for thread in self.itp.threads:
            if thread.device.isenabled:
                cpuid_func = getattr(thread, cpuid_func_name)
                cpuid_values.append(cpuid_func(leaf, subleaf))

        # If no threads were active, raise an exception
        if len(cpuid_values) == 0:
            raise DebuggerException("No CPUID values received! Please check the debug setup.")

        # Convert results to integers
        cpuid_values = list(map(int, cpuid_values))

        # If user requested a squashed value and the values weren't all the same, raise an exception
        if squash and cpuid_values.count(cpuid_values[0]) != len(cpuid_values):
            self._log.exception("CPUID values were not consistent across threads!")
            self._log.exception(
                "CPUID Reg {} Leaf {} Subleaf {}: {}".format(setup_reg, leaf, subleaf, cpuid_values))
            raise RegisterInconsistencyException("CPUID values were not consistent across threads!")
        elif squash:
            cpuid_values = cpuid_values[0]

        return cpuid_values

    def msr_read(self, msr_address, thread=None, squash=False):
        if not self.is_halted():
            raise DebuggerException("Tried to execute MSR instruction without halting!")
        msr_values = []
        if thread is None:
            for thread in self.itp.threads:
                if thread.device.isenabled:
                    msr_values.append(thread.msr(msr_address))
        else:
            if self.itp.threads[thread].device.isenabled:
                msr_values.append(self.itp.threads[thread].msr(msr_address))

        # If no threads were active, raise an exception
        if len(msr_values) == 0:
            self._log.exception("No MSR values received! Please check the ITP setup.")
            raise DebuggerException("No MSR values received! Please check the ITP setup.")

        # Convert result to integers
        msr_values = list(map(int, msr_values))

        # If user requested a squashed value and the values weren't all the same, raise an exception
        if squash and msr_values.count(msr_values[0]) != len(msr_values):
            self._log.exception("MSR values were not consistent across threads!")
            self._log.exception("MSR " + str(msr_address) + ": " + str(msr_values))
            raise RegisterInconsistencyException("MSR values were not consistent across threads!", msr_values)
        elif squash or len(msr_values) == 1:
            msr_values = msr_values[0]

        return msr_values

    def msr_write(self, msr_address, value, thread=None, no_readback=False):
        if not self.is_halted():
            raise DebuggerException("Tried to execute MSR instruction without halting!")
        if thread is None:
            self.itp.msr(msr_address, value)
        else:
            self.itp.threads[thread].msr(msr_address, value)

        # Confirm that write successfully completed across all active threads
        if not no_readback:
            try:
                read_back = self.msr_read(msr_address, thread=thread, squash=True)
            except RegisterInconsistencyException as e:
                self._log.exception(
                    "Write to MSR address {} failed! Threads had varying values: {}".format(msr_address, e))
                raise ReadBackException("Write to MSR address {} failed!".format(msr_address))
            if read_back != value:
                self._log.exception("Write to MSR address {} failed! Expected: {} Actual: {}".format(msr_address,
                                                                                                     value, read_back))
                raise ReadBackException("Write to MSR address {} failed!".format(msr_address))

        thread_log_str = "" if thread is None else " at thread {}".format(thread)
        self._log.debug("Wrote " + str(value) + " into address " + str(msr_address) + thread_log_str)

    def reset_break(self, state):
        self.itp.cv.resetbreak = 1 if state else 0

    def init_break(self, state):
        self.itp.cv.initbreak = 1 if state else 0

    def mem_read(self, address, size, thread_index=None):
        if not self.is_halted():
            raise DebuggerException("Tried to execute memory instruction without halting!")
        thread = self._get_first_active_thread() if thread_index is None else self.itp.threads[thread_index]
        if not thread.device.isenabled:
            raise DebuggerException("Specified thread is not active!")
        return int(thread.mem(address, size))

    def mem_write(self, address, size, data, thread_index=None, no_readback=False):
        if not self.is_halted():
            raise DebuggerException("Tried to execute memory instruction without halting!")
        # Write data into address and flush the cache to ensure it hits main memory
        thread = self._get_first_active_thread() if thread_index is None else self.itp.threads[thread_index]
        if not thread.device.isenabled:
            raise DebuggerException("Specified thread is not active!")
        thread.mem(address, size, data)
        self.flush_cache(thread_index)

        # Confirm that write successfully completed
        if not no_readback:
            read_back = self.mem_read(address, size, thread_index)
            if read_back != data:
                self._log.exception("Write to memory address " + str(address) + " failed! " +
                                    " Expected " + str(data) + " Actual: " + str(read_back))
                raise ReadBackException("Write to memory location {} failed!".format(address))

        self._log.debug("Wrote {} into {}".format(data, address))

    def flush_cache(self, thread_index=None):
        if not self.is_halted():
            raise DebuggerException("Tried to flush cache without halting!")
        thread = self._get_first_active_thread() if thread_index is None else self.itp.threads[thread_index]
        if not thread.device.isenabled:
            raise DebuggerException("Specified thread is not active!")
        thread.wbinvd()

    def reset_target(self):
        self.itp.resettarget()

    def pulse_pwr_good(self):
        self.itp.pulsepwrgood()

    def _get_first_active_thread(self):
        for thread in self.itp.threads:
            if thread.device.isenabled:
                return thread
        raise DebuggerException("No active threads found! Please check the debugger setup.")
