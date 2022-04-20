from xml.etree import ElementTree as ET

import mock

from dtaf_core.providers.internal.keysight_pcie_hw_injector_provider import KeysightPcieHwInjectorProvider

cfg_opts = ET.fromstring("""
<sut_os name="Linux" subtype="RHEL" version="7.6" kernel="3.10" verify="false">
    <shutdown_delay>10</shutdown_delay>
    <driver>
        <wsol>
            <ip>xxx</ip>
            <port>xxx</port>
            <timeout>10</timeout>
            <credentials user="debuguser" password="0penBmc1"/>
        </wsol>
    </driver>
</sut_os>
""")


class provider_create_mock:
    def __init__(self):
        self.driver_cfg = mock.Mock()


class mock_func:
    def __init__(self):
        return


class TestSuites:

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.keysight_pcie_hw_injector_provider.client')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=provider_create_mock())
    def test_open_session(mock_obj, client_mock):
        obj = KeysightPcieHwInjectorProvider(cfg_opts, log=mock.Mock())
        obj._sessionMgr = mock.Mock()
        obj._sessionPtr = mock.Mock()
        client_mock.constants = mock.Mock()
        try:
            obj.open_session()
        except RuntimeError:
            return

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.keysight_pcie_hw_injector_provider.client')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=provider_create_mock())
    def test_close_session(mock_obj, client_mock):
        obj = KeysightPcieHwInjectorProvider(cfg_opts, log=mock.Mock())
        obj._sessionMgr = mock.Mock()
        obj._sessionPtr = mock.Mock()
        client_mock.constants = mock.Mock()
        try:
            obj.close_session()
        except RuntimeError:
            return

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.keysight_pcie_hw_injector_provider.client')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=provider_create_mock())
    def test_check_link_speed(mock_obj, client_mock):
        obj = KeysightPcieHwInjectorProvider(cfg_opts, log=mock.Mock())
        obj._sessionMgr = mock.Mock()
        obj._sessionPtr = mock.Mock()
        obj._exerciser = mock.Mock()
        obj._portHandle = mock.Mock()
        client_mock.constants = mock.Mock()
        try:
            obj.check_link_speed()
        except RuntimeError:
            return

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.keysight_pcie_hw_injector_provider.client')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=provider_create_mock())
    def test_inject_bad_lcrc_err(mock_obj, client_mock):
        obj = KeysightPcieHwInjectorProvider(cfg_opts, log=mock.Mock())
        obj._sessionMgr = mock.Mock()
        obj._sessionPtr = mock.Mock()
        obj._exerciser = mock.Mock()
        obj._portHandle = mock.Mock()
        client_mock.constants = mock.Mock()
        try:
            obj.inject_bad_lcrc_err()
        except RuntimeError:
            return

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.keysight_pcie_hw_injector_provider.client')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=provider_create_mock())
    def test_inject_bad_tlp_err(mock_obj, client_mock):
        obj = KeysightPcieHwInjectorProvider(cfg_opts, log=mock.Mock())
        obj._sessionMgr = mock.Mock()
        obj._sessionPtr = mock.Mock()
        obj._exerciser = mock.Mock()
        obj._portHandle = mock.Mock()
        client_mock.constants = mock.Mock()
        try:
            obj.inject_bad_tlp_err()
        except RuntimeError:
            return

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.keysight_pcie_hw_injector_provider.client')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=provider_create_mock())
    def test_error(mock_obj, client_mock):
        obj = KeysightPcieHwInjectorProvider(cfg_opts, log=mock.Mock())
        try:
            obj.inject_bad_dllp_err()
        except NotImplementedError:
            pass
        try:
            obj.inject_completer_abort_err()
        except NotImplementedError:
            pass
        try:
            obj.inject_cto_err()
        except NotImplementedError:
            pass
        try:
            obj.ack()
        except NotImplementedError:
            pass
        try:
            obj.nak()
        except NotImplementedError:
            pass
        try:
            obj.inject_ur_err()
        except NotImplementedError:
            pass
        try:
            obj.bad_ecrc()
        except NotImplementedError:
            pass
        try:
            obj.crs()
        except NotImplementedError:
            pass
        try:
            obj.unexpected_completion()
        except NotImplementedError:
            pass
        try:
            obj.flow_ctrl_protocol_err()
        except NotImplementedError:
            pass

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.keysight_pcie_hw_injector_provider.client')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=provider_create_mock())
    def test_poisoned_tlp(mock_obj, client_mock):
        obj = KeysightPcieHwInjectorProvider(cfg_opts, log=mock.Mock())
        obj._sessionMgr = mock.Mock()
        obj._sessionPtr = mock.Mock()
        obj._exerciser = mock.Mock()
        obj._portHandle = mock.Mock()
        client_mock.constants = mock.Mock()
        try:
            obj.poisoned_tlp()
        except RuntimeError:
            return

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.keysight_pcie_hw_injector_provider.client')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=provider_create_mock())
    def test_stop_ack(mock_obj, client_mock):
        obj = KeysightPcieHwInjectorProvider(cfg_opts, log=mock.Mock())
        obj._sessionMgr = mock.Mock()
        obj._sessionPtr = mock.Mock()
        obj._exerciser = mock.Mock()
        obj._portHandle = mock.Mock()
        client_mock.constants = mock.Mock()
        obj.stop_ack()

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.keysight_pcie_hw_injector_provider.client')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=provider_create_mock())
    def test_start_ack(mock_obj, client_mock):
        obj = KeysightPcieHwInjectorProvider(cfg_opts, log=mock.Mock())
        obj._sessionMgr = mock.Mock()
        obj._sessionPtr = mock.Mock()
        obj._exerciser = mock.Mock()
        obj._portHandle = mock.Mock()
        client_mock.constants = mock.Mock()
        obj.start_ack()

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.keysight_pcie_hw_injector_provider.client')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=provider_create_mock())
    def test_malformed_tlp(mock_obj, client_mock):
        obj = KeysightPcieHwInjectorProvider(cfg_opts, log=mock.Mock())
        obj._sessionMgr = mock.Mock()
        obj._sessionPtr = mock.Mock()
        obj._exerciser = mock.Mock()
        obj._portHandle = mock.Mock()
        client_mock.constants = mock.Mock()
        obj.malformed_tlp()

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.keysight_pcie_hw_injector_provider.client')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create',
                return_value=provider_create_mock())
    def test_surprise_link_down(mock_obj, client_mock):
        obj = KeysightPcieHwInjectorProvider(cfg_opts, log=mock.Mock())
        obj._sessionMgr = mock.Mock()
        obj._sessionPtr = mock.Mock()
        obj._exerciser = mock.Mock()
        obj._portHandle = mock.Mock()
        client_mock.constants = mock.Mock()
        obj.surprise_link_down()
