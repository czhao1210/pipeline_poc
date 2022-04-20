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

import platform
import subprocess
import time

from dtaf_core.lib.dtaf_constants import OperatingSystems
from dtaf_core.providers.flash_provider import FlashProvider


class Sf100FlashProvider(FlashProvider):
    DPCMD = "dpcmd.exe"
    DEVICE = "--device-SN"
    BATCH = "-z"
    TIMEOUT = "-t"
    TYPE = "--type"

    def __init__(self, cfg_opts, log):
        super(Sf100FlashProvider, self).__init__(cfg_opts, log)
        if platform.system() != OperatingSystems.WINDOWS:
            raise RuntimeError("Dediprog Sf100Pro software can only run on Windows hosts!")

        # self.device_mapping = self._config_model.driver_cfg.chip_config
        self.base_cmd = self._config_model.driver_cfg.cli_path + self.DPCMD

    def flash_image(self, device_name, image_path, timeout, chip):
        self._flash_image(device_name, image_path, timeout, chip)

    def _flash_image(self, device_name, image_path, timeout, chip):
        self._log.debug("Flashing image {} to SF100 on Device {}".format(image_path, device_name))
        cmd = r'"%s" %s %s %s "%s" %s %s %s %s' % (
            self.base_cmd, self.DEVICE, str(device_name), self.BATCH, image_path, self.TIMEOUT, timeout, self.TYPE,
            chip)
        obj = subprocess.Popen(cmd, shell=True)
        time.sleep(int(timeout))

    def chip_identify(self):
        pass

    def read(self, address=None, length=None, target=None):
        pass

    def write(self, address=None, data=None, target=None):
        pass

    def current_bios_version_check(self):
        raise NotImplementedError

    def current_bmc_version_check(self):
        raise NotImplementedError

    def current_cpld_version_check(self):
        raise NotImplementedError

    def flash_image_bmc(self, path=None, image_name=None, target=None, amc=None):
        raise NotImplementedError
