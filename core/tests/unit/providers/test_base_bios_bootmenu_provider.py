import xml.etree.ElementTree as ET

import mock
from dtaf_core.providers.internal.base_bios_bootmenu_provider import BaseBiosBootmenuProvider


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
<bios_bootmenu>
					<driver>
						<pi>
                            <ip>10.190.155.174</ip>
                            <port>80</port>
                            <proxy>http://child-prc.intel.com:913</proxy>
							<image_name>xeon-d.bin</image_name>
                        </pi>    
                    </driver>
                    <screen width='100' height="31"/>
                    <efishell_entry select_item="Launch EFI Shell"/>
				</bios_bootmenu>""")
log = _Log()


class CIMockGet():
    pass


class DFMockCreate():
    def register(self, *args, **kwargs):
        return True

    def start(self, *args, **kwargs):
        return True


class EfishellEntryMock:
    def __init__(self):
        self.select_item = "a"
        self.path = "b"


class TestBaseBiosBootmenuProvider(object):
    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_bios_bootmenu_provider.DriverFactory")
    @mock.patch("dtaf_core.providers.internal.base_bios_bootmenu_provider._ContextInstance")
    def test_press(ci_mock, df_mock):
        ci_mock.get.return_value.data_adapter['boot_menu'] = CIMockGet()
        df_mock.create.return_value = DFMockCreate()
        with BaseBiosBootmenuProvider(cfg_opts, log) as BBBP_obj:
            BBBP_obj.press("F7")

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_bios_bootmenu_provider.DriverFactory")
    @mock.patch("dtaf_core.providers.internal.base_bios_bootmenu_provider._ContextInstance")
    def test_press_key(ci_mock, df_mock):
        ci_mock.get.return_value.data_adapter['boot_menu'] = CIMockGet()
        df_mock.create.return_value = DFMockCreate()
        with BaseBiosBootmenuProvider(cfg_opts, log) as BBBP_obj:
            BBBP_obj.press_key("F7")

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_bios_bootmenu_provider.DriverFactory")
    @mock.patch("dtaf_core.providers.internal.base_bios_bootmenu_provider._ContextInstance")
    def test_wait_for_entry_menu(ci_mock, df_mock):
        ci_mock.get.return_value.data_adapter['boot_menu'] = CIMockGet()
        df_mock.create.return_value = DFMockCreate()
        with BaseBiosBootmenuProvider(cfg_opts, log) as BBBP_obj:
            BBBP_obj.wait_for_entry_menu(100)

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_bios_bootmenu_provider.DriverFactory")
    @mock.patch("dtaf_core.providers.internal.base_bios_bootmenu_provider._ContextInstance")
    def test_select(ci_mock, df_mock):
        ci_mock.get.return_value.data_adapter['boot_menu'] = CIMockGet()
        df_mock.create.return_value = DFMockCreate()
        with BaseBiosBootmenuProvider(cfg_opts, log) as BBBP_obj:
            BBBP_obj.select("a", "b", 100, "c")

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_bios_bootmenu_provider.DriverFactory")
    @mock.patch("dtaf_core.providers.internal.base_bios_bootmenu_provider._ContextInstance")
    def test_enter_selected_item(ci_mock, df_mock):
        ci_mock.get.return_value.data_adapter['boot_menu'] = CIMockGet()
        df_mock.create.return_value = DFMockCreate()
        with BaseBiosBootmenuProvider(cfg_opts, log) as BBBP_obj:
            BBBP_obj.enter_selected_item(100, "c")

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_bios_bootmenu_provider.DriverFactory")
    @mock.patch("dtaf_core.providers.internal.base_bios_bootmenu_provider._ContextInstance")
    def test_get_selected_item(ci_mock, df_mock):
        ci_mock.get.return_value.data_adapter['boot_menu'] = CIMockGet()
        df_mock.create.return_value = DFMockCreate()
        with BaseBiosBootmenuProvider(cfg_opts, log) as BBBP_obj:
            BBBP_obj.get_selected_item()

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_bios_bootmenu_provider.DriverFactory")
    @mock.patch("dtaf_core.providers.internal.base_bios_bootmenu_provider._ContextInstance")
    def test_get_page_information(ci_mock, df_mock):
        ci_mock.get.return_value.data_adapter['boot_menu'] = CIMockGet()
        df_mock.create.return_value = DFMockCreate()
        with BaseBiosBootmenuProvider(cfg_opts, log) as BBBP_obj:
            BBBP_obj.get_page_information()

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_bios_bootmenu_provider.DriverFactory")
    @mock.patch("dtaf_core.providers.internal.base_bios_bootmenu_provider._ContextInstance")
    def test_wait_for_bios_boot_menu(ci_mock, df_mock):
        ci_mock.get.return_value.data_adapter['boot_menu'] = CIMockGet()
        df_mock.create.return_value = DFMockCreate()
        with BaseBiosBootmenuProvider(cfg_opts, log) as BBBP_obj:
            BBBP_obj.wait_for_bios_boot_menu(100)

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_bios_bootmenu_provider.DriverFactory")
    @mock.patch("dtaf_core.providers.internal.base_bios_bootmenu_provider._ContextInstance")
    def test_enter_efishell(ci_mock, df_mock):
        ci_mock.get.return_value.data_adapter['boot_menu'] = CIMockGet()
        df_mock.create.return_value = DFMockCreate()
        with BaseBiosBootmenuProvider(cfg_opts, log) as BBBP_obj:
            BBBP_obj._config_model.efishell_entry = EfishellEntryMock()
            BBBP_obj.enter_efishell(100)

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_bios_bootmenu_provider.DriverFactory")
    @mock.patch("dtaf_core.providers.internal.base_bios_bootmenu_provider._ContextInstance")
    def test_reboot(ci_mock, df_mock):
        ci_mock.get.return_value.data_adapter['boot_menu'] = CIMockGet()
        df_mock.create.return_value = DFMockCreate()
        with BaseBiosBootmenuProvider(cfg_opts, log) as BBBP_obj:
            BBBP_obj.reboot(100)
