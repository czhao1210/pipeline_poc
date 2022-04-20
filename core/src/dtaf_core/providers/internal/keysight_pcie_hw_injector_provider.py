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
import time
import win32com.client as client
from dtaf_core.providers.pcie_hw_injector_provider import PcieHwInjectorProvider


class KeysightPcieHwInjectorProvider(PcieHwInjectorProvider):
    """
    Class that provides PCIe hardware injectors using the Keysight API.
    This class support Keysight Gen 3 card only.
    """
    def __init__(self, cfg_opts, log):
        super(KeysightPcieHwInjectorProvider, self).__init__(cfg_opts, log)
        self._platform_dir = self._config_model.driver_cfg.platform_dir
        self._exerciser_dir = self._config_model.driver_cfg.exerciser_dir
        self._module = self._config_model.driver_cfg.module
        self._port = self._config_model.driver_cfg.port

    def __enter__(self):
        self._sessionMgr = client.Dispatch("Agt.AgtSessionManager.1")
        self.close_session()
        self.open_session()
        self.check_link_speed()
        return super(KeysightPcieHwInjectorProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_session()
        return super(KeysightPcieHwInjectorProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def open_session(self):
        """
        Open a Keysight session.
        """
        print("Open Keysight session from port: {} {}".format(self._module, self._port))
        try:
            sessionHandle = self._sessionMgr.OpenSession("PCIEExerciserGen3", client.constants.AGT_SESSION_ONLINE)

            self._log.info("\tHandle\tType\t\t\tLabel")
            self._log.info("\t------\t----\t\t\t-----")
            sessionList = self._sessionMgr.ListOpenSessions(None, None)[1]
            for session in sessionList:
                sessionType = self._sessionMgr.GetSessionType(session)
                sessionLable = self._sessionMgr.GetSessionLabel(session)
                self._log.info("\t{}\t{}\t{}".format(session, sessionType, sessionLable))

            self._sessionPtr = self._sessionMgr.GetSessionInterface(sessionHandle)
            self._exerciser = self._sessionPtr.GetInterfaceByName("AgtPCIEExerciser")

            portSelector = self._sessionPtr.GetInterfaceByName("AgtPortSelector")
            self._portHandle = portSelector.AddPort(self._module, self._port)

            # specify the data rate capability of the Exerciser. 
            # Value = 4, generation 3 (8.0 Gb/s) data rate as well as generation 1 and generation 2 data rates supported
            self._exerciser.ExerciserSet(self._portHandle, client.constants.PCIE_EXERCISER_DATA_RATE, 4)
            self._exerciser.LinkUp(self._portHandle)
            LINKUP_DELAY_SEC = 5
            time.sleep(LINKUP_DELAY_SEC)
        except Exception as ex:
            log_err = "An Exception Occurred while attempting to open Keysight Session : {}".format(ex)
            self._log.error(log_err)
            raise RuntimeError(log_err)

    def close_session(self):
        """
        Close all Keysight sessions.
        """
        self._log.info("Closing all active Keysight sessions")
        try:
            sessionList = self._sessionMgr.ListOpenSessions(None, None)[1]
            if sessionList:
                for session in sessionList:
                    self._sessionMgr.CloseSession(session)
        except Exception as ex:
            log_err = "An Exception Occurred while attempting to close Keysight Session : {}".format(ex)
            self._log.error(log_err)
            raise RuntimeError(log_err)

    def check_link_speed(self):
        """
        Get link speed and width info.
        """
        width = self._exerciser.DataLinkStateRead(self._portHandle)
        if width == 0:
            self._log.info("The link is not active")
            return
        self._log.info("The link width is x {}".format(width))

        speed = self._exerciser.ExerciserStatusRead(self._portHandle, client.constants.PCIE_EXERCISERSTATUS_LINKSPEED)
        dict_gen = {1: "GEN1",
                    2: "GEN2",
                    4: "GEN3"}
        if speed in dict_gen.keys():
            self._log.info("The Link is Active at {}".format(dict_gen[speed]))
        else:
            self._log.info("The link is not active")

    def inject_bad_lcrc_err(self):
        """
        Inject bad lcrc error.
        """
        self._log.info("sending a config read with a Bad LCRC")

        self._exerciser.SiDefaultSet(self._portHandle)
        # Configure the tlp to send.
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_FMT, 0)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_TYPE, 4)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_CFG_REGNUM, 0)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_LASTDWBE, 0x0)
        # The packet will have an incorrect LCRC.
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_BUSERROR, 32)

        self._exerciser.SiSend(self._portHandle)

    def inject_bad_tlp_err(self):
        """
        This method replace packet's sequence number.
        """
        raise NotImplementedError
        """
        self._log.info("Sending config read that replaces the packets sequence number by offset of 1")

        self._exerciser.SiDefaultSet(self._portHandle)

        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_FMT, 0)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_TYPE, 4)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_CFG_REGNUM, 0)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_LEN, 0x10)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_TC, 0x1)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_LASTDWBE, 0x0)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_MEM64_ADDRLO, 0xead0)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_MEM64_ADDRHI, 0x1)

        self._exerciser.DllPhySet(self._portHandle, client.constants.PCIE_DLLPHY_SEQNO_OFFSET, 1)

        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_BUSERROR, 64)

        self._exerciser.SiSend(self._portHandle)
        self._log.info("Finished")
        """

    def inject_bad_dllp_err(self):
        raise NotImplementedError

    def inject_completer_abort_err(self):
        raise NotImplementedError
        """
        self._log.info("Replace completion code with 'Completer Abort' ")
        self._exerciser.BlockDefaultSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_LEN, 16)
        # Type and FMT can be changed to create reads or writes, or config rd/wr or IO rd/wr
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_TYPE, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_FMT, 1)
        # Change the following line to enter the address you would like to read from, this could be amended in a loop to cover multiple addresses

        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_MEM32_ADDR, 0x10003504)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_MEM64_ADDRHI, 0x1)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_INTADDR, 0x20000)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_REPEAT, 5)

        self._exerciser.BlockGenSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, client.constants.PCIE_BLOCKGEN_REPEAT, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_REQBEH_LEN, 1024)

        # Invoke uncorrectable completion behavior set
        self._exerciser.CompBehDefaultSet(self._portHandle, client.constants.PCIE_COMPQUEUE_0, 0)
        self._exerciser.CompBehSet(self._portHandle, client.constants.PCIE_COMPQUEUE_0, 0, client.constants.PCIE_COMPBEH_COMPSTATUS, 4)

        self._exerciser.Run(self._portHandle)

        # After 1 seconds
        time.sleep(1)

        self._exerciser.Stop(self._portHandle)

        self._log.info("finished")
        """
    def inject_cto_err(self):
        raise NotImplementedError
        """
        self._log.info("Send Request packet and discarding the the completions.")
        self._exerciser.BlockDefaultSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_LEN, 16)
        # Type and FMT can be changed to create reads or writes, or config rd/wr or IO rd/wr
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_TYPE, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_FMT, 1)
        # Change the following line to enter the address you would like to read from, this could be amended in a loop to cover multiple addresses

        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_MEM32_ADDR, 0x10003504)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_MEM64_ADDRHI, 0x1)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_INTADDR, 0x20000)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_REPEAT, 5)

        self._exerciser.BlockGenSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, client.constants.PCIE_BLOCKGEN_REPEAT, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_REQBEH_LEN, 1024)

        # Invoke uncorrectable completion behavior set
        self._exerciser.CompBehDefaultSet(self._portHandle, client.constants.PCIE_COMPQUEUE_0, 0)
        self._exerciser.CompBehSet(self._portHandle, client.constants.PCIE_COMPQUEUE_0, 0, client.constants.PCIE_COMPBEH_DISCARD, 1)

        self._exerciser.Run(self._portHandle)

        # After 15 seconds 15s
        time.sleep(15)

        self._exerciser.Stop(self._portHandle)

        self._log.info("finished")

        self._log.info("Telling the exerciser it is OK to reply to completions again.")

        time.sleep(0.5)

        self._exerciser.CompBehDefaultSet(self._portHandle, client.constants.PCIE_COMPQUEUE_0, 0)
        """
    def ack(self):
        raise NotImplementedError

    def nak(self):
        raise NotImplementedError

    def inject_ur_err(self):
        raise NotImplementedError
        """
        self._log.info("Replace completion code with 'Unsupported Request' ")
        self._exerciser.BlockDefaultSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_LEN, 16)
        # Type and FMT can be changed to create reads or writes, or config rd/wr or IO rd/wr
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_TYPE, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_FMT, 1)
        # Change the following line to enter the address you would like to read from, this could be amended in a loop to cover multiple addresses

        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_MEM32_ADDR, 0x10003504)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_MEM64_ADDRHI, 0x1)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_INTADDR, 0x20000)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_REPEAT, 5)

        self._exerciser.BlockGenSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, client.constants.PCIE_BLOCKGEN_REPEAT, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_REQBEH_LEN, 1024)

        # Invoke uncorrectable completion behavior set
        self._exerciser.CompBehDefaultSet(self._portHandle, client.constants.PCIE_COMPQUEUE_0, 0)
        self._exerciser.CompBehSet(self._portHandle, client.constants.PCIE_COMPQUEUE_0, 0, client.constants.PCIE_COMPBEH_COMPSTATUS, 1)

        self._exerciser.Run(self._portHandle)

        # After 1 seconds
        time.sleep(1)

        self._exerciser.Stop(self._portHandle)

        self._log.info("finished")
        """
    def bad_ecrc(self):
        raise NotImplementedError
        """
        sptCommon = self._sessionPtr.GetInterfaceByName("AgtSptCommon")
        if sptCommon.SWPackageCheck(self._portHandle, "U4305BU-022") == 0:
            self._log.error("Error: ECRC SW License Not Installed. Please see Ordering Guide in the tool kit documentation")
            return

        self._log.info("Generating Bad ECRC with Digest Bit = 1")
        # START OF Bad ECRC
        # ECRC is a BASE RAS Type

        # Apply button pressed for Traffic Setup page
        # Stop all functions button pressed
        self._exerciser.Stop(self._portHandle)
        self._exerciser.RxErrorStop(self._portHandle)
        # --------------------------------------------------------------------------------
        # Apply button pressed for Traffic Setup page
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_LEN, 2)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_RSVD023, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_ATTR, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_RSVD013, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_TC, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_RSVD017, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_TYPE, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_FMT, 2)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_RSVD007, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_1STDWBE, 15)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_LASTDWBE, 15)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_MEM32_ADDR, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_RESOURCE, 1)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_REPEAT, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_PATTERN_TERM, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_WAITREPEAT, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_INTADDR, 0)
        self._exerciser.BlockGenSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, client.constants.PCIE_BLOCKGEN_STARTLINE, 0x0)
        self._exerciser.BlockGenSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, client.constants.PCIE_BLOCKGEN_STOPLINE, 0x0)
        self._exerciser.BlockGenSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, client.constants.PCIE_BLOCKGEN_ENABLED, 0x1)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_EP, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_TD, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_INCORRECT_LCRC, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_NULLIFIED_TLP, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_WRONG_PYLD_SIZE, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_INCORRECT_DISP, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_AUTOTAG, 1)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_TAG, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_GAP, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_LEN, 1024)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_REPEAT, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_REPLACE_STP, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_REPLACE_END, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_REPLACE_SEQNO, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_INSERT_TD, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_INCORRECT_ECRC, 0)
        self._exerciser.ReqBehGenSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, client.constants.PCIE_REQBEHGEN_STARTLINE, 0x0)
        self._exerciser.ReqBehGenSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, client.constants.PCIE_REQBEHGEN_STOPLINE, 0x0)
        self._exerciser.BlockGenSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, client.constants.PCIE_BLOCKGEN_REPEAT, 0x1)
        # --------------------------------------------------------------------------------
        # Apply button pressed for Traffic Setup page
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_LEN, 2)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_RSVD023, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_ATTR, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_RSVD013, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_TC, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_RSVD017, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_TYPE, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_FMT, 2)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_RSVD007, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_1STDWBE, 15)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_LASTDWBE, 15)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_MEM32_ADDR, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_RESOURCE, 1)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_REPEAT, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_PATTERN_TERM, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_WAITREPEAT, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_BLOCK_INTADDR, 0)
        self._exerciser.BlockGenSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, client.constants.PCIE_BLOCKGEN_STARTLINE, 0x0)
        self._exerciser.BlockGenSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, client.constants.PCIE_BLOCKGEN_STOPLINE, 0x0)
        self._exerciser.BlockGenSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, client.constants.PCIE_BLOCKGEN_ENABLED, 0x1)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_EP, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_TD, 1)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_INCORRECT_LCRC, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_NULLIFIED_TLP, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_WRONG_PYLD_SIZE, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_INCORRECT_DISP, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_AUTOTAG, 1)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_TAG, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_GAP, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_LEN, 1024)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_REPEAT, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_REPLACE_STP, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_REPLACE_END, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_REPLACE_SEQNO, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_INSERT_TD, 1)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x0, client.constants.PCIE_REQBEH_INCORRECT_ECRC, 1)
        self._exerciser.ReqBehGenSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, client.constants.PCIE_REQBEHGEN_STARTLINE, 0x0)
        self._exerciser.ReqBehGenSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, client.constants.PCIE_REQBEHGEN_STOPLINE, 0x0)

        # --------------------------------------------------------------------------------
        # Start Function A button pressed
        self._exerciser.RunFunctions(self._portHandle, 0x1)
        # --------------------------------------------------------------------------------
        # ### END OF Bad ECRC ###
        """
    def poisoned_tlp(self, addy=0x00100000, data=[0xde, 0xad, 0xbe, 0xef], reqid=0x4b00):
        """
        Inject poisoned tlp error by sending a memory write request.
        
        :param addy: The address of the memory to write.
        :param data: The list of data to write to the memory specified above.
        :param reqid: Requester id, 16bit BDF for the Keysight requester.
                      bit 0-7 for bus, 8-11 for device and 12-15 for function.
                      example: ab:0c.d translate to 0xabcd. 
        """
        self._log.info("writing {} to {} with req id {}".format([hex(i) for i in data],\
                                                                hex(addy), hex(reqid)))

        self._exerciser.SiDefaultSet(self._portHandle)
        # Configuration space set up.
        self._exerciser.ConfRegWrite(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x4, 0x100007)
        self._exerciser.ConfRegMaskWrite(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0x4, 0x0)
        # Memory-write tlp headers. 
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_FUNCTION_SELECTED, 0x0)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_LEN, 0x1)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_RSVD023, 0x0)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_ATTR, 0x0)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_RSVD013, 0x0)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_TC, 0x0)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_RSVD017, 0x0)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_TYPE, 0x0)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_FMT, 0x2)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_RSVD007, 0x0)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_1STDWBE, 0xF)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_LASTDWBE, 0x0)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_REQID, reqid)
        # Set memory address
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_MEM32_ADDR, addy)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_RESOURCE, 0x0)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_INTADDR, 0x0)
        # Set payload 
        self._exerciser.SiReqMemSet(self._portHandle, 0x4, data)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_TAG, 0x0)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_TD, 0x0)
        # Set Error
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_EP, 0x1)

        self._exerciser.SiSend(self._portHandle)

    def stop_ack(self):
        self._log.info("Stop Sending ACK from PCIE card")

        # PCIE_DLLPHY_STOP_ACK 0x1 > means ACK Normally OFF and STOP Send ACK
        self._exerciser.DllPhySet(self._portHandle, client.constants.PCIE_DLLPHY_STOP_ACK, 0x1)

        self._exerciser.RunFunctions(self._portHandle, 0x1)

    def start_ack(self):
        self._log.info("Start Sending ACK from PCIE card")

        # PCIE_DLLPHY_STOP_ACK 0x0 > means ACK Normally ON and Send ACK
        self._exerciser.DllPhySet(self._portHandle, client.constants.PCIE_DLLPHY_STOP_ACK, 0x0)

        self._exerciser.RunFunctions(self._portHandle, 0x1)

    def malformed_tlp(self):
        """
        Inject malformed tlp with undefined tlp format and type.
        """
        self._log.info("sending a Malformed Fmt-Type: UNDEFINED TLP FMT/TYPE")

        self._exerciser.SiDefaultSet(self._portHandle)

        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_FMT, 0)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_TYPE, 9)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_CFG_REGNUM, 0)
        self._exerciser.SiReqSet(self._portHandle, client.constants.PCIE_SI_LASTDWBE, 0x0)

        self._exerciser.SiSend(self._portHandle)

    def surprise_link_down(self):
        """
        Inject the surprise link down error.
        """
        self._log.info("Forcing the exerciser to stop responding to platform... Please wait...")

        self._exerciser.LinkStateDirect(self._portHandle, client.constants.PCIE_LINKSTATEDIRECT_IDLE)

        # After 5 seconds
        SURPRISE_LINK_DOWN_DELAY_SEC = 5
        time.sleep(SURPRISE_LINK_DOWN_DELAY_SEC)

        self._log.info("Waking up the exerciser to initiate link training...")
        self._exerciser.LinkStateDirect(self._portHandle, client.constants.PCIE_LINKSTATEDIRECT_START_LINKTRAINING)

        self._log.info("Finished waking up the exerciser.")

    def crs(self):
        raise NotImplementedError
        """
        self._log.info("Replace completion code with 'Configuration Request Retry Status' ")
        self._exerciser.BlockDefaultSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_LEN, 16)
        # Type and FMT can be changed to create reads or writes, or config rd/wr or IO rd/wr
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_TYPE, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_FMT, 1)
        # Change the following line to enter the address you would like to read from, this could be amended in a loop to cover multiple addresses

        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_MEM32_ADDR, 0x10003504)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_MEM64_ADDRHI, 0x1)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_INTADDR, 0x20000)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_REPEAT, 5)

        self._exerciser.BlockGenSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, client.constants.PCIE_BLOCKGEN_REPEAT, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_REQBEH_LEN, 1024)

        # Invoke uncorrectable completion behavior set
        self._exerciser.CompBehDefaultSet(self._portHandle, client.constants.PCIE_COMPQUEUE_0, 0)
        self._exerciser.CompBehSet(self._portHandle, client.constants.PCIE_COMPQUEUE_0, 0, client.constants.PCIE_COMPBEH_COMPSTATUS, 2)

        self._exerciser.Run(self._portHandle)

        # After 1 seconds
        time.sleep(1)

        self._exerciser.Stop(self._portHandle)

        self._log.info("finished")
        """
    def unexpected_completion(self):
        raise NotImplementedError
        """
        self._log.info("Send Request packet and get wrong sequence number from completer.")

        self._log.info("Send Request packet and discarding the the completions.")
        self._exerciser.BlockDefaultSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_LEN, 16)
        # Type and FMT can be changed to create reads or writes, or config rd/wr or IO rd/wr
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_TYPE, 0)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_FMT, 1)
        # Change the following line to enter the address you would like to read from, this could be amended in a loop to cover multiple addresses

        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_MEM32_ADDR, 0x10003504)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_MEM64_ADDRHI, 0x1)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_INTADDR, 0x20000)
        self._exerciser.BlockSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_BLOCK_REPEAT, 5)

        self._exerciser.BlockGenSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, client.constants.PCIE_BLOCKGEN_REPEAT, 0)
        self._exerciser.ReqBehSet(self._portHandle, client.constants.PCIE_HWCHANNEL_FUNCTION_A, 0, client.constants.PCIE_REQBEH_LEN, 1024)

        # Invoke uncorrectable completion behavior set
        self._exerciser.DllPhySet(self._portHandle, client.constants.PCIE_DLLPHY_SEQNO_OFFSET, 1)

        self._exerciser.CompBehDefaultSet(self._portHandle, client.constants.PCIE_COMPQUEUE_0, 0)
        self._exerciser.CompBehSet(self._portHandle, client.constants.PCIE_COMPQUEUE_0, 0, client.constants.PCIE_COMPBEH_REPLACE_SEQNO, 1)

        self._exerciser.Run(self._portHandle)

        # After 15 seconds 15s
        time.sleep(15)

        self._exerciser.Stop(self._portHandle)

        self._log.info("finished")

        time.sleep(0.5)

        self._exerciser.CompBehDefaultSet(self._portHandle, client.constants.PCIE_COMPBEH_REPLACE_SEQNO, 0)
        """
    def flow_ctrl_protocol_err(self):
        raise NotImplementedError

    def get_keysight_link_speed(self):
        """
        This method is to get the Link Speed of Keysight Card.

        :return speed
        """
        speed = self._exerciser.ExerciserStatusRead(self._portHandle, client.constants.PCIE_EXERCISERSTATUS_LINKSPEED)
        return speed

    def get_keysight_link_width(self):
        """
        This method is to get Link width of Keysight Card.

        :return width
        """
        width = self._exerciser.DataLinkStateRead(self._portHandle)
        return width

    def tlp_gen(self, field={}, count=1, dir=None):
        """
        This to inject he TLP Error.
        """
        raise NotImplementedError
