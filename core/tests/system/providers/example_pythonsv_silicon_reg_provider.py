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
import sys
import time

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.lib.dtaf_constants import ProductFamilies

from dtaf_core.providers.provider_factory import ProviderFactory
from dtaf_core.providers.silicon_reg_provider import SiliconRegProvider



class TestPythonSVSiliconRegProvider(BaseTestCase):
    """
    Basic test case demonstrating the use of TestPythonSVSiliconRegProvider
    """

    list_14nm_silicon_family = [ProductFamilies.SKX, ProductFamilies.CLX, ProductFamilies.CPX]

    def __init__(self, test_log, arguments, cfg_opts):
        super(TestPythonSVSiliconRegProvider, self).__init__(test_log, arguments, cfg_opts)
        si_dbg_cfg = cfg_opts.find(SiliconRegProvider.DEFAULT_CONFIG_PATH)
        self._sv = ProviderFactory.create(si_dbg_cfg, test_log)  # type: SiliconRegProvider

    def test_refresh(self):
        self._log.info("Execute PythonSV sv.refresh...")
        self._sv.refresh()
        # assert number of sockets > 0
        num_sockets = self._sv.get_socket_count()
        print("num_sockets=%s" % str(num_sockets))
        assert num_sockets > 0


    def test_search_reg(self):
        self._log.info("Execute CScripts get_socket_count...")
        assert self._sv.get_socket_count() != 0

        self._log.info("Execute CScripts sv.socket1.search...")
        search_output = self._sv.search_reg(self._sv.SOCKET, "adddc", socket_index=0)
        print("Search output='{}'".format(str(search_output)))
        assert search_output is not None
        self._log.info("PythonSV sv.socket1.search obtained as:\n" + str(search_output))

        self._log.info("Execute CScripts sv.sockets.search...")
        search_output = self._sv.search_reg(self._sv.SOCKETS, "adddc")
        assert search_output is not None
        self._log.info("PythonSV sv.sockets.search obtained as:\n" + str(search_output))


    def test_get_by_default(self):
        self._log.info("Execute PythonSV get_by_default...")
        get_value_output = self._sv.get_field_value(self._sv.UNCORE, "imc0_spareinterval", "numspare")
        assert get_value_output is not None
        self._log.info("PythonSV csp.sv.socket0.uncore0.imc0_spareinterval.numspare obtained as:\n" +
                       str(get_value_output))

    def test_get_by_path_for_uncores(self):
        self._log.info("Execute PythonSV getby_path...")
        self._log.info("Execute PythonSV sv.socket0.uncores.getreg...")
        get_reg_output = self._sv.get_by_path(self._sv.UNCORES, "imc0_spareinterval")
        assert get_reg_output is not None
        self._log.info("PythonSV csp.sv.socket0.uncores.imc0_spareinterval obtained as:\n" + str(get_reg_output))

    def test_get_default(self):
        self._log.info("Execute PythonSV sv.socket0.uncore0.getdefault...")
        default = self._sv.get_default(self._sv.UNCORE, "imc1_c2_adddc_region3")
        assert default == 0
        self._log.info("PythonSV sv.getdefault obtained as: " + str(default))

    def execute(self):
        self._log.info("Execute is where the main PythonSVSilicongReg test code should be called.")
        self.test_refresh()
        self.test_get_by_default()
        self.test_get_by_path_for_uncores()
        self.test_search_reg()
        self.test_get_by_path_for_uncores()
        self.unlock()
        return True

    def unlocker(self):
        assert  self._sv.unlock("dal", r"ccr\czhao")


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if TestPythonSVSiliconRegProvider.main() else Framework.TEST_RESULT_FAIL)
