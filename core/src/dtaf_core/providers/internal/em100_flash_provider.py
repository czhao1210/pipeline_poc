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
from dtaf_core.providers.internal.em100_flash_emulator_provider import Em100FlashEmulatorProvider


class Em100FlashProvider(Em100FlashEmulatorProvider):
    """
    Class that interfaces with Dediprog EM100 Flash emulators.

    For best results, ensure that the EM100Pro GUI is closed when running automation. The GUI can interfere with the CLI
    and force the emulator/driver into a state which requires a host restart.

    Ensure that the following items are fully up-to-date. Older versions of Dediprog software will not work properly.
    1 - Dediprog EM100Pro/-G2 host software
    2 - Dediprog EM100Pro/-G2 host USB driver
    3 - Dediprog EM100Pro/-G2 FPGA Firmware
    """

    def __init__(self, cfg_opts, log):
        super(Em100FlashProvider, self).__init__(cfg_opts, log)

    def start(self, target):
        raise NotImplementedError("Emulator is in use as a FlashProvider - emulation not available by convention!")

    def stop(self, target):
        raise NotImplementedError("Emulator is in use as a FlashProvider - emulation not available by convention!")
