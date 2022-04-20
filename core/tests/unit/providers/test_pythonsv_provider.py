import six

if six.PY2:
    import mock

if six.PY3 or six.PY34:
    from unittest import mock
from mock_import import mock_import
from dtaf_core.providers.internal.pythonsv_silicon_reg_provider import PythonsvSiliconRegProvider

from xml.etree import ElementTree as ET


class _Logs:
    def debug(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass


cfg_normal_skx = ET.fromstring("""
                <silicon_reg>
                    <driver>
                        <pythonsv>
                            <unlocker>C:\PushUtil\PushUtil.exe</unlocker>
                            <debugger_interface_type>ITP</debugger_interface_type>
                            <silicon>
                                <cpu_family>SKX</cpu_family>
                                <pch_family>LBG</pch_family>
                            </silicon>
                        </pythonsv>
                    </driver>
                </silicon_reg>
    """)

cfg_normal_cpx = ET.fromstring("""
                <silicon_reg>
                    <driver>
                        <pythonsv>
                            <unlocker>C:\PushUtil\PushUtil.exe</unlocker>
                            <debugger_interface_type>ITP</debugger_interface_type>
                            <silicon>
                                <cpu_family>CPX</cpu_family>
                                <pch_family>LBG</pch_family>
                            </silicon>
                        </pythonsv>
                    </driver>
                </silicon_reg>
    """)
cfg_normal_clx = ET.fromstring("""
                <silicon_reg>
                    <driver>
                        <pythonsv>
                            <unlocker>C:\PushUtil\PushUtil.exe</unlocker>
                            <debugger_interface_type>ITP</debugger_interface_type>
                            <silicon>
                                <cpu_family>CLX</cpu_family>
                                <pch_family>LBG</pch_family>
                            </silicon>
                        </pythonsv>
                    </driver>
                </silicon_reg>
    """)
cfg_normal_ivt = ET.fromstring("""
                <silicon_reg>
                    <driver>
                        <pythonsv>
                            <unlocker>C:\PushUtil\PushUtil.exe</unlocker>
                            <debugger_interface_type>ITP</debugger_interface_type>
                            <silicon>
                                <cpu_family>IVT</cpu_family>
                                <pch_family>LBG</pch_family>
                            </silicon>
                        </pythonsv>
                    </driver>
                </silicon_reg>
    """)

cfg_normal_ivt_component = ET.fromstring("""
                <silicon_reg>
                    <driver>
                        <pythonsv>
                            <unlocker>C:\PushUtil\PushUtil.exe</unlocker>
                            <debugger_interface_type>ITP</debugger_interface_type>
                            <silicon>
                                <cpu_family>IVT</cpu_family>
                                <pch_family>LBG</pch_family>
                            </silicon>
                            <components>
                                <component>pch</component>
                                <component>socket</component>
                            </components>
                        </pythonsv>
                    </driver>
                </silicon_reg>
""")


class TestSuites:

    @staticmethod
    @mock_import()
    def test_get_platform_modules():
        with PythonsvSiliconRegProvider(cfg_normal_ivt_component, _Logs()) as sv:  # type: PythonsvSiliconRegProvider
            try:
                sv.get_platform_modules()
            except NotImplementedError:
                return

    @staticmethod
    @mock_import()
    def test_get_cscripts_utils():
        with PythonsvSiliconRegProvider(cfg_normal_ivt_component, _Logs()) as sv:  # type: PythonsvSiliconRegProvider
            try:
                sv.get_cscripts_utils()
            except NotImplementedError:
                return

    @staticmethod
    @mock_import()
    def test_get_cscripts_ei_object():
        with PythonsvSiliconRegProvider(cfg_normal_ivt_component, _Logs()) as sv:  # type: PythonsvSiliconRegProvider
            try:
                sv.get_cscripts_ei_object()
            except NotImplementedError:
                return

    @staticmethod
    @mock_import()
    def test_get_cscripts_nvd_object():
        with PythonsvSiliconRegProvider(cfg_normal_ivt_component, _Logs()) as sv:  # type: PythonsvSiliconRegProvider
            try:
                sv.get_cscripts_nvd_object()
            except NotImplementedError:
                return

    @staticmethod
    @mock_import()
    def test_get_dimminfo_object():
        with PythonsvSiliconRegProvider(cfg_normal_ivt_component, _Logs()) as sv:  # type: PythonsvSiliconRegProvider
            try:
                sv.get_dimminfo_object()
            except NotImplementedError:
                return

    @staticmethod
    @mock_import()
    def test_get_ras_object():
        with PythonsvSiliconRegProvider(cfg_normal_ivt_component, _Logs()) as sv:  # type: PythonsvSiliconRegProvider
            try:
                sv.get_ras_object()
            except NotImplementedError:
                return

    @staticmethod
    @mock_import()
    def test_get_add_tran_obj():
        with PythonsvSiliconRegProvider(cfg_normal_ivt_component, _Logs()) as sv:  # type: PythonsvSiliconRegProvider
            try:
                sv.get_add_tran_obj()
            except NotImplementedError:
                return

    @staticmethod
    @mock_import()
    def test_get_bootscript_obj():
        with PythonsvSiliconRegProvider(cfg_normal_ivt_component, _Logs()) as sv:  # type: PythonsvSiliconRegProvider
            try:
                sv.get_bootscript_obj()
            except NotImplementedError:
                return

    @staticmethod
    @mock_import()
    def test_get_mc_utils_obj():
        with PythonsvSiliconRegProvider(cfg_normal_ivt_component, _Logs()) as sv:  # type: PythonsvSiliconRegProvider
            try:
                sv.get_mc_utils_obj()
            except NotImplementedError:
                return

    @staticmethod
    @mock_import()
    def test_search():
        with PythonsvSiliconRegProvider(cfg_normal_ivt_component, _Logs()) as sv:  # type: PythonsvSiliconRegProvider
            sv.resolve_scope = mock.Mock()
            try:
                sv.search_reg('a', 'b')
            except KeyError:
                pass
            try:
                sv.search_reg_bitfield('a', 'b')
            except KeyError:
                pass
            try:
                sv.search_reg_descr('a', 'b')
            except KeyError:
                pass
            try:
                sv.get_addr('a', 'b')
            except KeyError:
                pass
            try:
                sv.get_default('a', 'b')
            except KeyError:
                pass
            try:
                sv.get_spec('a', 'b')
            except KeyError:
                pass
            try:
                sv.show('a', 'b')
            except KeyError:
                pass
            try:
                sv.show_search('a', 'b')
            except KeyError:
                pass
            try:
                sv.get_by_path('a', 'b')
            except KeyError:
                pass
            try:
                sv.get_field_value('a', 'b', 'c')
            except KeyError:
                return

    @staticmethod
    @mock_import()
    def test_get():
        with PythonsvSiliconRegProvider(cfg_normal_ivt_component, _Logs()) as sv:  # type: PythonsvSiliconRegProvider
            sv.get_sockets()
            sv.get_socket_count()

    @staticmethod
    @mock_import()
    @mock.patch(
        "dtaf_core.providers.internal.pythonsv_silicon_reg_provider.PythonsvSiliconRegProvider.get_socket_count")
    @mock.patch("dtaf_core.providers.internal.pythonsv_silicon_reg_provider.PythonsvSiliconRegProvider.get_sockets")
    def test_sv_normal(gMock, cMock):
        cMock.return_value = 2
        cfgs = (cfg_normal_clx, cfg_normal_cpx, cfg_normal_skx, cfg_normal_ivt_component)
        for cfg in cfgs:
            with PythonsvSiliconRegProvider(cfg, _Logs()) as sv:  # type: PythonsvSiliconRegProvider
                sv.populate_scope_dict()
                sv.refresh()
                try:
                    has_excpetion = False
                    sv.get_klaxon_object()
                except NotImplementedError:
                    has_excpetion = True
                assert has_excpetion
                try:
                    has_excpetion = False
                    sv.get_xnm_memicals_utils_object()
                except NotImplementedError:
                    has_excpetion = True
                assert has_excpetion
                sv.resolve_scope(PythonsvSiliconRegProvider.UNCORE)
                sv.resolve_scope(PythonsvSiliconRegProvider.UNCORES)
                sv.resolve_scope(PythonsvSiliconRegProvider.SOCKET)
                sv.resolve_scope(PythonsvSiliconRegProvider.SOCKETS)

    @staticmethod
    @mock_import()
    @mock.patch(
        "dtaf_core.providers.internal.pythonsv_silicon_reg_provider.PythonsvSiliconRegProvider.get_socket_count")
    @mock.patch("dtaf_core.providers.internal.pythonsv_silicon_reg_provider.PythonsvSiliconRegProvider.get_sockets")
    def test_sv_component(gMock, cMock):
        cMock.return_value = 2
        cfgs = [cfg_normal_ivt_component]
        for cfg in cfgs:
            with PythonsvSiliconRegProvider(cfg, _Logs()) as sv:  # type: PythonsvSiliconRegProvider
                sv.populate_scope_dict()
                sv.refresh()
                try:
                    has_excpetion = False
                    sv.get_klaxon_object()
                except NotImplementedError:
                    has_excpetion = True
                assert has_excpetion
                try:
                    has_excpetion = False
                    sv.get_xnm_memicals_utils_object()
                except NotImplementedError:
                    has_excpetion = True
                assert has_excpetion
                sv.resolve_scope(PythonsvSiliconRegProvider.UNCORE)
                sv.resolve_scope(PythonsvSiliconRegProvider.UNCORES)
                sv.resolve_scope(PythonsvSiliconRegProvider.SOCKET)
                sv.resolve_scope(PythonsvSiliconRegProvider.SOCKETS)
            assert sv.components_list == ["pch", "socket"]
