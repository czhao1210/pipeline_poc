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



class TestCscriptSiliconRegProvider(BaseTestCase):
    """
    Basic test case demonstrating the use of CScriptSiliconRegProvider
    """

    list_14nm_silicon_family = [ProductFamilies.SKX, ProductFamilies.CLX, ProductFamilies.CPX]

    def __init__(self, test_log, arguments, cfg_opts):
        super(TestCscriptSiliconRegProvider, self).__init__(test_log, arguments, cfg_opts)
        si_dbg_cfg = cfg_opts.find(SiliconRegProvider.DEFAULT_CONFIG_PATH)
        self._cscript = ProviderFactory.create(si_dbg_cfg, test_log)  # type: SiliconRegProvider

    def test_refresh(self):
        self._log.info("Execute CScripts sv.refresh...")
        self._cscript.refresh()
        # assert number of sockets > 0
        num_sockets = self._cscript.get_socket_count()
        print("num_sockets=%s" % str(num_sockets))
        assert num_sockets > 0

    def test_get_cpu_stepping(self):
        cscripts_utils = self._cscript.get_cscripts_utils()
        if hasattr(cscripts_utils, "getStepping"):
            stepping = cscripts_utils.getStepping(self._cscript.get_sockets()[0])
            self._log.info("CScripts utils().getStepping() obtained as: " + str(stepping))
            assert stepping is not None
        else:
            assert False

    def test_add_map(self):
        self._log.info("Execute CScripts get_mc_obj().addMap()...")
        platform_modules = self._cscript.get_platform_modules()
        if hasattr(platform_modules, "get_mc_obj"):
            mc_obj = platform_modules.get_mc_obj()
            assert mc_obj is not None
            self._log.info("CScripts get_mc_obj().addMap() obtained as:\n")
            mc_obj.addMap()
        else:
            assert False

    def test_search_reg(self):
        self._log.info("Execute CScripts get_socket_count...")
        assert self._cscript.get_socket_count() != 0

        self._log.info("Execute CScripts sv.socket1.search...")
        search_output = self._cscript.search_reg(self._cscript.SOCKET, "adddc", socket_index=0)
        print("Search output='{}'".format(str(search_output)))
        assert search_output is not None
        self._log.info("CScripts sv.socket1.search obtained as:\n" + str(search_output))

        self._log.info("Execute CScripts sv.sockets.search...")
        search_output = self._cscript.search_reg(self._cscript.SOCKETS, "adddc")
        assert search_output is not None
        self._log.info("CScripts sv.sockets.search obtained as:\n" + str(search_output))

    def test_get_by_path_for_uncore(self):
        self._log.info("Execute CScripts getby_path...")
        self._log.info("Execute CScripts sv.socket0.uncore0.getreg...")
        get_reg_output = self._cscript.get_by_path(self._cscript.UNCORE, "imc0_spareinterval")
        assert get_reg_output is not None
        self._log.info("CScripts csp.sv.socket0.uncore0.imc0_spareinterval obtained as:\n" + str(get_reg_output))

    def test_get_by_default(self):
        self._log.info("Execute CScripts get_by_default...")
        get_value_output = self._cscript.get_field_value(self._cscript.UNCORE, "imc0_spareinterval", "numspare")
        assert get_value_output is not None
        self._log.info("CScripts csp.sv.socket0.uncore0.imc0_spareinterval.numspare obtained as:\n" +
                       str(get_value_output))

    def test_get_by_path_for_uncores(self):
        self._log.info("Execute CScripts getby_path...")
        self._log.info("Execute CScripts sv.socket0.uncores.getreg...")
        get_reg_output = self._cscript.get_by_path(self._cscript.UNCORES, "imc0_spareinterval")
        assert get_reg_output is not None
        self._log.info("CScripts csp.sv.socket0.uncores.imc0_spareinterval obtained as:\n" + str(get_reg_output))

    def test_get_default(self):
        self._log.info("Execute CScripts sv.socket0.uncore0.getdefault...")
        default = self._cscript.get_default(self._cscript.UNCORE, "imc1_c2_adddc_region3")
        assert default == 0
        self._log.info("CScripts sv.getdefault obtained as: " + str(default))

    def test_get_xnm_memicals_utils_object(self):
        self._log.info("Executing CScripts get_xnm_memicals_utils_object...")
        muObj = self._cscript.get_xnm_memicals_utils_object()
        assert muObj is not None

        if self._cscript.silicon_cpu_family in self.list_14nm_silicon_family:
            pop_ch_list = muObj.getPopChList(socket=0)
        else:
            pop_ch_list = muObj.get_pop_ch_list(socket=0)

        assert pop_ch_list is not None
        self._log.info("Number of pop_mc_list='{}'".format(len(pop_ch_list)))

    def test_get_mc_utils_object(self):
        self._log.info("Executing CScripts get_mc_utils_object...")
        muObj = self._cscript.get_mc_utils_object()
        assert muObj is not None

        if self._cscript.silicon_cpu_family in self.list_14nm_silicon_family:
            mirror_status = muObj.getMirrorStatus(socket=0)
        else:
            mirror_status = muObj.get_mirror_status(socket=0)

        assert mirror_status is not None
        self._log.info("Mirror status='{}'".format(mirror_status))
        self._log.info("The test case 'test_get_mc_utils_object' passed...")

    def test_get_ecc_error_injection_object(self):
        self._log.info("Executing CScripts get_ecc_error_injection_object...")
        muObj = self._cscript.get_ecc_error_injection_object()
        assert muObj is not None

        self._log.info("The test case 'get_ecc_error_injection_object' passed...")

    def test_get_dimminfo_object(self):
        self._log.info("Executing CScripts test_get_dimminfo_object...")
        dimminfo_obj = self._cscript.get_dimminfo_object()
        assert dimminfo_obj is not None
        self._log.info("The test case 'test_get_dimminfo_object' passed...")

    def test_get_klaxon_object(self):
        self._log.info("Executing CScripts test_get_klaxon_object...")
        klaxon_obj = self._cscript.get_klaxon_object()
        assert klaxon_obj is not None
        self._log.info("The test case 'test_get_klaxon_object' passed...")

    def test_get_ras_object(self):
        self._log.info("Executing CScripts test_get_ras_object...")
        ras_obj = self._cscript.get_ras_object()
        assert ras_obj is not None
        self._log.info("The test case 'test_get_klaxon_object' passed...")

    def test_get_add_tran_obj(self):
        self._log.info("Executing CScripts test_get_ras_object...")
        add_tran_obj = self._cscript.get_add_tran_obj()
        assert add_tran_obj is not None
        self._log.info("The test case 'test_get_klaxon_object' passed...")

    def execute(self):
        self._log.info("Execute is where the main CscriptsSiliconRegProvider test code should be called.")
        self.test_get_add_tran_obj()
        self.test_get_ras_object()
        self.test_refresh()
        self.test_get_cpu_stepping()
        self.test_add_map()
        self.test_search_reg()
        self.test_get_by_path_for_uncore()
        self.test_get_by_default()
        self.test_get_by_path_for_uncores()
        self.test_get_default()
        self.test_get_xnm_memicals_utils_object()
        self.test_get_mc_utils_object()
        self.test_get_ecc_error_injection_object()
        self.test_get_dimminfo_object()
        self.test_get_klaxon_object()
        return True


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if TestCscriptSiliconRegProvider.main() else Framework.TEST_RESULT_FAIL)