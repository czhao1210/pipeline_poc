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
import time


from dtaf_core.providers.pcie_hw_injector_provider import PcieHwInjectorProvider


class Pei4PcieHwInjectorProvider(PcieHwInjectorProvider):
    """
    Class that provides PCIe hardware injectors using the Pei4 API.
    """
    MODE_DICT = {1: "Endpoint Mode",
                 2: "Interposer Mode"}

    DIRECTION_ROOTPORT = 0
    DIRECTION_ENDPOINT = 1

    def __init__(self, cfg_opts, log):
        super(Pei4PcieHwInjectorProvider, self).__init__(cfg_opts, log)
        self._path = self._config_model.driver_cfg.path

    def __enter__(self):
        try:
            sys.path.append(self._path)
            from pei_python import pei
            self._pei = pei
        except Exception as ex:
            log_err = "An Exception Occurred while attempting to import pei libaries : {}".format(ex)
            self._log.error(log_err)
            raise RuntimeError(log_err)
        self.check_link_speed()
        return super(Pei4PcieHwInjectorProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return super(Pei4PcieHwInjectorProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def _card_reset(self):
        """
        Resets the test card
        """
        reg = self._pei.port[0]
        reg.INJ_CTRL.sw_reset = 1
        self._pei.inj_err_up_en = False
        self._pei.inj_tlp_up_en = False
        self._pei.inj_err_dn_en = False
        self._pei.inj_tlp_dn_en = False

    def switch_mode(self, mode):
        """
        Switch to Endpoint mode or Interposer mode for PEI card.
        Note : After G3 the default setting would set back, this setting is non-persistant

        :param mode: The working mode PEI card switches to. 1 for Endpoint mode and 2 for Interposer Mode.
        :raise RuntimeError: Will raise RuntimeError is the option is not valid.
        """
        if mode not in self.MODE_DICT.keys():
            log_err = "Not able to switch mode for PEI card, options allowed are: 1 - Endpoint Mode and 2 - Interposer Mode"
            self._log.error(log_err)
            raise RuntimeError(log_err)
        self._log.info("Switching PEI mode to {}...".format(self.MODE_DICT[mode]))
        self._pei.load_image(mode)
        self._pei.status()

    def set_mode(self, mode):
        """
        set to Endpoint mode or Interposer mode for PEI card.
        Note: Even after G3, the setting would remain persistant

        :param mode: The working mode PEI card switches to. 1 for Endpoint mode and 2 for Interposer Mode.
        :raise RuntimeError: Will raise RuntimeError is the option is not valid.
        """
        if mode not in self.MODE_DICT.keys():
            log_err = "Not able to switch mode for PEI card, options allowed are: 1 - Endpoint Mode and 2 - Interposer Mode"
            self._log.error(log_err)
            raise RuntimeError(log_err)
        self._log.info("Switching PEI mode to {}...".format(self.MODE_DICT[mode]))
        self._pei.set_operating_image(mode)
        self._pei.status()

    def open_session(self):
        raise NotImplementedError

    def close_session(self):
        raise NotImplementedError

    def check_link_speed(self):
        """
        Get link speed and width info.
        """
        self._pei.status()

    def inject_bad_lcrc_err(self, count=10, duration_sec=120, route=DIRECTION_ROOTPORT):
        """
        Inject bad lcrc error.

        :param count: Number of errors to inject.
        :param duration_sec: Test duration. The test ends at the earliest occurance of 'count' or 'duration'
        :param route: The direction in which errors are injected.
        """

        self._log.info("Starting BAD_TLP_lcrc")
        self._card_reset()
        self._pei.BAD_TLP_lcrc(count=count, dir=route)
        self._pei.run(retry=duration_sec)

    def inject_bad_tlp_err(self, count=10, duration_sec=120, route=DIRECTION_ROOTPORT):
        """
        This method replaces packet's sequence number.

        :param count: Number of errors to inject.
        :param duration_sec: Test duration. The test ends at the earliest occurance of 'count' or 'duration'
        :param route: The direction in which errors are injected.
        """

        self._log.info("Starting BAD_TLP_CPL_TO_seq")
        self._card_reset()
        self._pei.BAD_TLP_CPL_TO_seq(count=count, dir=route)
        self._pei.run(retry=duration_sec)

    def inject_bad_dllp_err(self, count=10, duration_sec=120, route=DIRECTION_ROOTPORT):
        """
        Inject bad dllp error.

        :param count: Number of errors to inject.
        :param duration_sec: Test duration. The test ends at the earliest occurance of 'count' or 'duration'
        :param route: The direction in which errors are injected.
        """

        self._log.info("Starting BAD_DLLP_crc")
        self._card_reset()
        self._pei.BAD_DLLP_crc(count=count, dir=route)
        self._pei.run(retry=duration_sec)

    def inject_completer_abort_err(self, count=10, duration_sec=120, route=DIRECTION_ROOTPORT):
        """
        Inject completer abort error.
        Does not cause CA flag to set in UE AER of root port,
        according to PEI 4.0 User Guide.

        :param count: Number of errors to inject.
        :param duration_sec: Test duration. The test ends at the earliest occurance of 'count' or 'duration'
        :param route: The direction in which errors are injected.
        """
        from pei_def import TLP_HEADER, TLP_CPLSTAT
        mask = TLP_HEADER(size=64)
        mask.set(field=TLP_HEADER.CplStat, value=TLP_CPLSTAT.CA)

        self._log.info("Starting TLP_HDR")
        self._card_reset()
        self._pei.TLP_HDR_INJ(mask=mask, count=count, dir=route)
        self._pei.run(retry=duration_sec)

    def inject_cto_err(self, count=10, duration_sec=120, route=DIRECTION_ROOTPORT):
        """
        Inject completion timeout error.

        :param count: Number of errors to inject.
        :param duration_sec: Test duration. The test ends at the earliest occurance of 'count' or 'duration'
        :param route: The direction in which errors are injected.
        """

        self._log.info("Starting CPL_TO_no_tlp")
        self._card_reset()
        self._pei.CPL_TO_no_tlp(count=count, dir=route)
        self._pei.run(retry=duration_sec)

    def ack(self, count=10, duration_sec=120, route=DIRECTION_ROOTPORT):
        """
        Replay timer timeout and replay number rollover.

        :param count: Number of errors to inject.
        :param duration_sec: Test duration. The test ends at the earliest occurance of 'count' or 'duration'
        :param route: The direction in which errors are injected.
        """

        self._log.info("Starting REPLAY_no_end")
        self._card_reset()
        self._pei.REPLAY_no_end(count=count, dir=route)
        self._pei.run(retry=duration_sec)

    def nak(self, count=10, duration_sec=120, route=DIRECTION_ROOTPORT):
        """
        Replay timer timeout and replay number rollover.

        :param count: Number of errors to inject.
        :param duration_sec: Test duration. The test ends at the earliest occurance of 'count' or 'duration'
        :param route: The direction in which errors are injected.
        """

        self._log.info("Starting REPLAY_no_end")
        self._card_reset()
        self._pei.REPLAY_no_end(count=count, dir=route)
        self._pei.run(retry=duration_sec)

    def inject_ur_err(self, count=1, duration_sec=120, route=DIRECTION_ROOTPORT):
        """
        Inject unsupported request error.

        :param count: Number of errors to inject.
        :param duration_sec: Test duration. The test ends at the earliest occurance of 'count' or 'duration'
        :param route: The direction in which errors are injected.
        """

        self._log.info("Starting UR_gen_cfg")
        self._card_reset()
        self._pei.UR_gen_cfg(count=count, dir=route)
        self._pei.run(retry=duration_sec)

    def bad_ecrc(self, count=1, duration_sec=120, route=DIRECTION_ROOTPORT):
        """
        Inject bad ecrc error.

        :param count: Number of errors to inject.
        :param duration_sec: Test duration. The test ends at the earliest occurance of 'count' or 'duration'
        :param route: The direction in which errors are injected.
        """

        self._log.info("Starting ECRC_gen_td")
        self._card_reset()
        self._pei.ECRC_gen_td(count=count, dir=route)
        self._pei.run(retry=duration_sec)

    def poisoned_tlp(self, count=10, duration_sec=120, route=DIRECTION_ROOTPORT):
        """
        Inject poisoned tlp error.

        :param count: Number of errors to inject.
        :param duration_sec: Test duration. The test ends at the earliest occurance of 'count' or 'duration'
        :param route: The direction in which errors are injected.
        """

        self._log.info("Starting POISON_TLP_gen_ep")
        self._card_reset()
        self._pei.POISON_TLP_gen_ep(count=count, dir=route)
        self._pei.run(retry=duration_sec)

    def stop_ack(self, count=10, duration_sec=120, route=DIRECTION_ROOTPORT):
        """
        Not sending ACK.

        :param count: Number of errors to inject.
        :param duration_sec: Test duration. The test ends at the earliest occurance of 'count' or 'duration'
        :param route: The direction in which errors are injected.
        """

        self._log.info("Starting CPL_TO_UCPL_no_ack")
        self._card_reset()
        self._pei.CPL_TO_UCPL_no_ack(count=count, dir=route)
        self._pei.run(retry=duration_sec)

    def start_ack(self):
        raise NotImplementedError

    def malformed_tlp(self, count=1, duration_sec=120, route=DIRECTION_ROOTPORT):
        """
        Inject malformed tlp error.

        :param count: Number of errors to inject.
        :param duration_sec: Test duration. The test ends at the earliest occurance of 'count' or 'duration'
        :param route: The direction in which errors are injected.
        """

        self._log.info("Starting MTLP_gen_len")
        self._card_reset()
        self._pei.MTLP_gen_len(count=count, dir=route)
        self._pei.run(retry=duration_sec)

    def surprise_link_down(self, count=10, duration_sec=120, route=DIRECTION_ROOTPORT):
        """
        Inject the surprise link down error.
        Injection based on duration; injection counter does not advance.

        :param count: Number of errors to inject.
        :param duration_sec: Test duration. The test ends at the earliest occurance of 'count' or 'duration'
        :param route: The direction in which errors are injected.
        """

        self._log.info("Starting SURPRISE_DOWN")
        self._card_reset()
        self._pei.SURPRISE_DOWN(count=count, dir=route)
        self._pei.run(retry=duration_sec)

    def crs(self):
        raise NotImplementedError

    def unexpected_completion(self, count=1, duration_sec=120, route=DIRECTION_ROOTPORT):
        """
        Inject unexpected completion error.

        :param count: Number of errors to inject.
        :param duration_sec: Test duration. The test ends at the earliest occurance of 'count' or 'duration'
        :param route: The direction in which errors are injected.
        """

        self._log.info("Starting UCE_gen_len")
        self._card_reset()
        self._pei.UCE_gen_len(count=count, dir=route)
        self._pei.run(retry=duration_sec)

    def flow_ctrl_protocol_err(self, count=10, duration_sec=120, route=DIRECTION_ROOTPORT):
        """
        Inject flow control protocol error(Whitley).

        :param count: Number of errors to inject.
        :param duration_sec: Test duration. The test ends at the earliest occurance of 'count' or 'duration'
        :param route: The direction in which errors are injected.
        """

        self._log.info("Starting FCPE_updatefc")
        self._card_reset()
        self._pei.FCPE_updatefc(count=count, dir=route)
        self._pei.run(retry=duration_sec)

    def get_keysight_link_speed(self):
        raise NotImplementedError

    def get_keysight_link_width(self):
        raise NotImplementedError

    def tlp_gen(self, field={"Fmt": 3, "Type": 0, "Length": 1, "BE_1st": 0xf,
                             "EP": 1, "ReqID_Req": 0x0d4b, "Addr_64": 0x204ff0000000},
                count=1, dir=DIRECTION_ROOTPORT):
        """
        This to inject he TLP Error.
        """
        from pei_def import TLP_HEADER
        tlp = TLP_HEADER(size=128)
        tlp.set(TLP_HEADER.Fmt, field["Fmt"])
        tlp.set(TLP_HEADER.Type, field["Type"])
        tlp.set(TLP_HEADER.Length, field["Length"])
        tlp.set(TLP_HEADER.BE_1st, field["BE_1st"])
        tlp.set(TLP_HEADER.EP, field["EP"])
        tlp.set(TLP_HEADER.ReqID_Req, field["ReqID_Req"])
        tlp.set(TLP_HEADER.Addr_64, field["Addr_64"])

        self._pei.TLP_GEN(tlp=tlp, count=count, dir=dir)
        self._pei.run(retry=120)
