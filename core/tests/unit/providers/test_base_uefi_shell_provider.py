import xml.etree.ElementTree as ET
from dtaf_core.providers.internal.base_uefi_shell_provider import BaseUefiShellProvider
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


class DFMockCreate():
    def register(self, *args, **kwargs):
        return True

    def start(self, *args, **kwargs):
        return True

    def read_from(self, *args, **kwargs):
        return "True"

    def write(self, *args, **kwargs):
        return True


class ReCompileMock():
    def search(self, *args, **kwargs):
        return True


def errormock(*args, **kwargs):
    from dtaf_core.providers.internal.base_uefi_shell_provider import TimeoutException
    raise TimeoutException("My error.")


class TestBUSProvider(object):
    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_uefi_shell_provider.re")
    @mock.patch("dtaf_core.providers.internal.base_uefi_shell_provider.DriverFactory")
    def test_wait_for_uefi(DF_mock, re_mock):
        re_mock.compile.return_value = ReCompileMock()
        DF_mock.create.return_value = DFMockCreate()
        with BaseUefiShellProvider(cfg_opts=cfg_opts, log=log) as BUSP_obj:
            BUSP_obj.wait_for_uefi(100)

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_uefi_shell_provider.re")
    @mock.patch("dtaf_core.providers.internal.base_uefi_shell_provider.DriverFactory")
    def test_exit_uefi(DF_mock, re_mock):
        re_mock.compile.return_value = ReCompileMock()
        DF_mock.create.return_value = DFMockCreate()
        with BaseUefiShellProvider(cfg_opts=cfg_opts, log=log) as BUSP_obj:
            BUSP_obj.exit_uefi()

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_uefi_shell_provider.re")
    @mock.patch("dtaf_core.providers.internal.base_uefi_shell_provider.DriverFactory")
    @pytest.mark.parametrize("error", [True, False])
    def test_in_uefi(DF_mock, re_mock, error):
        re_mock.compile.return_value = ReCompileMock()
        DF_mock.create.return_value = DFMockCreate()
        with BaseUefiShellProvider(cfg_opts=cfg_opts, log=log) as BUSP_obj:
            if error:
                BUSP_obj.execute = errormock
            try:
                BUSP_obj.in_uefi()
            except:
                pass

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_uefi_shell_provider.re")
    @mock.patch("dtaf_core.providers.internal.base_uefi_shell_provider.DriverFactory")
    def test_shutdown(DF_mock, re_mock):
        re_mock.compile.return_value = ReCompileMock()
        DF_mock.create.return_value = DFMockCreate()
        with BaseUefiShellProvider(cfg_opts=cfg_opts, log=log) as BUSP_obj:
            BUSP_obj.shutdown()

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_uefi_shell_provider.re")
    @mock.patch("dtaf_core.providers.internal.base_uefi_shell_provider.DriverFactory")
    def test_reboot(DF_mock, re_mock):
        re_mock.compile.return_value = ReCompileMock()
        DF_mock.create.return_value = DFMockCreate()
        with BaseUefiShellProvider(cfg_opts=cfg_opts, log=log) as BUSP_obj:
            BUSP_obj.reboot()

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_uefi_shell_provider.re")
    @mock.patch("dtaf_core.providers.internal.base_uefi_shell_provider.DriverFactory")
    def test_warm_reset(DF_mock, re_mock):
        re_mock.compile.return_value = ReCompileMock()
        DF_mock.create.return_value = DFMockCreate()
        with BaseUefiShellProvider(cfg_opts=cfg_opts, log=log) as BUSP_obj:
            BUSP_obj.warm_reset()

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_uefi_shell_provider.re")
    @mock.patch("dtaf_core.providers.internal.base_uefi_shell_provider.DriverFactory")
    def test_cold_reset(DF_mock, re_mock):
        re_mock.compile.return_value = ReCompileMock()
        DF_mock.create.return_value = DFMockCreate()
        with BaseUefiShellProvider(cfg_opts=cfg_opts, log=log) as BUSP_obj:
            BUSP_obj.cold_reset()
