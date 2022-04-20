import xml.etree.ElementTree as ET
from dtaf_core.providers.internal.onebkc_deployment_provider import OnebkcDeploymentProvider
import pytest
import mock


class _Log(object):
    @classmethod
    def debug(cls, msg):
        print(msg)

    @classmethod
    def info(cls, msg):
        print(msg)

    @classmethod
    def warning(cls, msg):
        print(msg)

    @classmethod
    def error(cls, msg):
        print(msg)

    @classmethod
    def critical(cls, msg):
        print(msg)

    warn = warning
    fatal = critical


cfg_opts = ET.fromstring("""
<bios_setupmenu>
                    <driver>
                        <com>
                            <baudrate>115200</baudrate>
                            <port>COM100</port>
                            <timeout>5</timeout>
                        </com>
                    </driver>
                    <efishell_entry select_item="Launch EFI Shell">
                        <path>
                            <node>Setup Menu</node>
                            <node>Boot Manager</node>
                        </path>
                    </efishell_entry>
                    <continue select_item="Continue"/>
                    <reset press_key="\\33R\\33r\\33R" parse="False"/>
                </bios_setupmenu>""")
log = _Log()


class ConfigModelMock:
    def __init__(self):
        self.local_root = True
        self.repo_user = True
        self.repo_password = True


class RequestMock():
    def __init__(self):
        self.get_method = True


class DFMock():
    @staticmethod
    def parse_ingredient_info_from_manifest(*args, **kwargs):
        return True


class TestODProvider(object):
    @staticmethod
    @mock.patch('dtaf_core.providers.internal.onebkc_deployment_provider.os')
    @mock.patch('dtaf_core.providers.internal.onebkc_deployment_provider.urllib')
    @pytest.mark.parametrize("os_path_exists", [True, False])
    def test_download(urllib_mock, os_mock, os_path_exists):
        os_mock.path.basename.return_value = True
        os_mock.path.join.return_value = True
        os_mock.path.exists.return_value = os_path_exists
        os_mock.makedirs.return_value = True
        urllib_mock.request.Request.return_value = RequestMock()
        with OnebkcDeploymentProvider(cfg_opts=cfg_opts, log=log) as ODP_obj:
            ODP_obj._config_model = ConfigModelMock()
            ODP_obj.download(package_url="test.txt")

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.onebkc_deployment_provider.os')
    @mock.patch('dtaf_core.providers.internal.onebkc_deployment_provider.urllib')
    @mock.patch('dtaf_core.providers.internal.onebkc_deployment_provider.DriverFactory')
    def test_get_ingredient_info(DF_mock, urllib_mock, os_mock, ):
        DF_mock.create.return_value = DFMock()

        os_mock.path.basename.return_value = True
        os_mock.path.join.return_value = True
        os_mock.path.exists.return_value = True
        os_mock.makedirs.return_value = True
        urllib_mock.request.Request.return_value = RequestMock()
        with OnebkcDeploymentProvider(cfg_opts=cfg_opts, log=log) as ODP_obj:
            ODP_obj._config_model = ConfigModelMock()
            ODP_obj.get_ingredient_info("a", "b", "c")

    @staticmethod
    @pytest.mark.parametrize("name", ["a", None])
    def test_get_device_property(name):
        with OnebkcDeploymentProvider(cfg_opts, log) as ODP_obj:
            ODP_obj._config_model = ConfigModelMock()
            ODP_obj.get_device_property(name=name)
