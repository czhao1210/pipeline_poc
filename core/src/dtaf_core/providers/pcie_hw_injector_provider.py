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
from abc import ABCMeta, abstractmethod

import six
from dtaf_core.providers.base_provider import BaseProvider


class PcieHwInjectorProvider(BaseProvider):
    """
    Interface to abstract the various PCIe hardware injectors (Keysight, PEI etc)
    """

    # x-path for silicon pcie hardware injector provider in configuration file
    DEFAULT_CONFIG_PATH = "suts/sut/providers/pcie_hw_injector"

    def __init__(self, cfg_opts, log):
        """
        Create a new PcieHwInjectorProvider object

        :param log: Logger object to use for debug and info messages
        :param cfg_opts: xml.etree.ElementTree.Element of configuration options for execution environment.
        """
        super(PcieHwInjectorProvider, self).__init__(cfg_opts, log)

    def __enter__(self):
        return super(PcieHwInjectorProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(PcieHwInjectorProvider, self).__exit__(exc_type, exc_val, exc_tb)

    @abstractmethod
    def open_session(self):
        # type: () -> None
        """
        Opens a Keysight session for Keysight Gen 3 card.
        """
        raise NotImplementedError

    @abstractmethod
    def close_session(self):
        """
        Close all active Keysight sessions.
        """
        raise NotImplementedError

    @abstractmethod
    def check_link_speed(self):
        """
        Get link speed and width info.
        """
        raise NotImplementedError

    @abstractmethod
    def inject_bad_lcrc_err(self):
        """
        This API injects bad lcrc error.
        """
        raise NotImplementedError

    @abstractmethod
    def inject_bad_tlp_err(self):
        """
        This API injects bad tlp error.
        """
        raise NotImplementedError

    @abstractmethod
    def inject_bad_dllp_err(self):
        """
        This API injects bad dllp error.
        """
        raise NotImplementedError

    @abstractmethod
    def inject_completer_abort_err(self):
        """
        This API injects completer abort error.
        """
        raise NotImplementedError

    @abstractmethod
    def inject_cto_err(self):
        """
        Completion timeout.
        """
        raise NotImplementedError

    @abstractmethod
    def ack(self):
        """
        Replay timer timeout and replay number rollover.
        Work with the nak() method below.
        """
        raise NotImplementedError

    @abstractmethod
    def nak(self):
        """
        Replay timer timeout and replay number rollover.
        Work with the nak() method above.
        """
        raise NotImplementedError

    @abstractmethod
    def inject_ur_err(self):
        """
        This API injects the Unsupported Request error.
        """
        raise NotImplementedError

    @abstractmethod
    def bad_ecrc(self):
        """
        This API injects bad ecrc error.
        """
        raise NotImplementedError

    @abstractmethod
    def poisoned_tlp(self):
        """
        This API injects poisoned tlp error.
        """
        raise NotImplementedError

    @abstractmethod
    def stop_ack(self):
        """
        Stop Sending ACK from PCIE card
        """
        raise NotImplementedError

    @abstractmethod
    def start_ack(self):
        """
        Start Sending ACK from PCIE card
        """
        raise NotImplementedError

    @abstractmethod
    def malformed_tlp(self):
        """
        This API injects malformed tlp error.
        """
        raise NotImplementedError

    @abstractmethod
    def surprise_link_down(self):
        """
        This API injects surprise link down error.
        """
        raise NotImplementedError

    @abstractmethod
    def crs(self):
        """
        This API replace completion code with 'Configuration Request Retry Status,
        and injects IERRs.
        """
        raise NotImplementedError

    @abstractmethod
    def unexpected_completion(self):
        """
        This API injects unexpected completion error.
        """
        raise NotImplementedError

    @abstractmethod
    def flow_ctrl_protocol_err(self):
        """
        This API injects flow control protocol error.
        """
        raise NotImplementedError

    @abstractmethod
    def get_keysight_link_width(self):
        """
        This API give Link width.
        """
        raise NotImplementedError

    @abstractmethod
    def get_keysight_link_speed(self):
        """
        This API gived LinkSpeed.
        """
        raise NotImplementedError

    @abstractmethod
    def tlp_gen(self, field={}, count=1, dir=None):
        """
        This to inject he TLP Error.
        """
        raise NotImplementedError
