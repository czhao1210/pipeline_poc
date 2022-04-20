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
from dtaf_core.providers.internal.base_bios_bootmenu_provider import BaseBiosBootmenuProvider
from six import add_metaclass
from abc import ABCMeta


@add_metaclass(ABCMeta)
class ComBiosBootmenuProvider(BaseBiosBootmenuProvider):
    def close(self):
        self.__dict__.get('_BaseBiosBootmenuProvider__driver').close()

    def update_configuration(self, update_cfg_opts, update_log):
        self.close()
        super(ComBiosBootmenuProvider, self).update_configuration(update_cfg_opts=update_cfg_opts,
                                                                        update_log=update_log)
        self.__init__(update_cfg_opts, update_log)
