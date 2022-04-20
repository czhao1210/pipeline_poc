import six
if six.PY2:
    pass

if six.PY3 or six.PY34:
    pass
from mock_import import mock_import
from dtaf_core.providers.internal.cscripts_silicon_reg_provider import CscriptsSiliconRegProvider

from xml.etree import ElementTree as ET


class _Logs:
    def debug(self,*args, **kwargs):
        pass
    def error(self,*args, **kwargs):
        pass
    def info(self,*args, **kwargs):
        pass



cfg_normal_skx = ET.fromstring("""
                <silicon_reg>
                    <driver>
                        <cscripts>
                            <debugger_interface_type>ITP</debugger_interface_type>
                            <silicon>
                                <cpu_family>SKX</cpu_family>
                                <pch_family>LBG</pch_family>
                            </silicon>
                        </cscripts>
                    </driver>
                </silicon_reg>
    """)

cfg_normal_cpx = ET.fromstring("""
                <silicon_reg>
                    <driver>
                        <cscripts>
                            <debugger_interface_type>ITP</debugger_interface_type>
                            <silicon>
                                <cpu_family>CPX</cpu_family>
                                <pch_family>LBG</pch_family>
                            </silicon>
                        </cscripts>
                    </driver>
                </silicon_reg>
    """)
cfg_normal_clx = ET.fromstring("""
                <silicon_reg>
                    <driver>
                        <cscripts>
                            <debugger_interface_type>ITP</debugger_interface_type>
                            <silicon>
                                <cpu_family>CLX</cpu_family>
                                <pch_family>LBG</pch_family>
                            </silicon>
                        </cscripts>
                    </driver>
                </silicon_reg>
    """)
cfg_normal_ivt = ET.fromstring("""
                <silicon_reg>
                    <driver>
                        <cscripts>
                            <debugger_interface_type>ITP</debugger_interface_type>
                            <silicon>
                                <cpu_family>IVT</cpu_family>
                                <pch_family>LBG</pch_family>
                            </silicon>
                        </cscripts>
                    </driver>
                </silicon_reg>
    """)


class TestCScriptProvider:

    def setup_method(self):
        pass

    def teardown_method(self):
        pass

    @staticmethod
    @mock_import()
    def test_cscipt_normal():
            cfgs = (cfg_normal_clx, cfg_normal_cpx, cfg_normal_skx)
            for cfg in cfgs:
                with CscriptsSiliconRegProvider(cfg, _Logs()) as cscript:
                    cscript.get_dimminfo_object()
                    cscript.get_platform_modules()
                    cscript.refresh()
                    cscript.populate_scope_dict()
                    cscript.get_upi_obj()
                    cscript.get_cscripts_utils()
                    cscript.get_ras_object()
                    cscript.get_mc_utils_object()
                    cscript.get_ecc_error_injection_object()
                    cscript.get_klaxon_object()
                    cscript.get_xnm_memicals_utils_object()
                    cscript.resolve_scope(CscriptsSiliconRegProvider.UNCORE)
                    cscript.resolve_scope(CscriptsSiliconRegProvider.UNCORES)
                    cscript.resolve_scope(CscriptsSiliconRegProvider.SOCKET)
                    cscript.resolve_scope(CscriptsSiliconRegProvider.SOCKETS)