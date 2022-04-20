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
from dtaf_core.drivers.base_driver import BaseDriver


class TcfDriver(BaseDriver):

    def __init__(self, cfg_opts, log):
        super(TcfDriver, self).__init__(cfg_opts, log)
        self.targets = self._driver_cfg_model.targets
        self.interconnects = self._driver_cfg_model.interconnects

    def get_num_targets(self):
        return len(self.targets)

    def get_num_interconnects(self):
        return len(self.interconnects)

    def get_target(self, index=0):
        """Convenience function for getting a single TCF target"""
        return self.targets[index]

    def get_interconnect(self, index=0):
        """Convenience function for getting a single TCF interconnect"""
        return self.interconnects[index]
