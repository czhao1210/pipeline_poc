import six
if six.PY2:
    import mock

if six.PY3 or six.PY34:
    from unittest import mock

import pytest
from dtaf_core.providers.internal.base_bios_setupmenu_provider import BaseBiosSetupMenuProvider
from xml.etree import ElementTree as ET
import serial


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


cfg_opts = None
log = _Log()
cfg_opts_normal= ET.fromstring("""
        <bios_setupmenu>
            <driver>
                <com>
                    <port>COM100</port>
                    <baudrate>115200</baudrate>
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
        </bios_setupmenu>
""")

class TestBaseBiosSetupMenuProvider(object):

    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    @pytest.mark.parametrize('key_code, return_v, state', [('F2', True, True),
                                                 ('F7', True, True),
                                                 ('ESC', False, False)])
    def test_press(serial, adapter, key_code, return_v, state):
        adapter.return_value.data_adapter['entry_menu'].press = mock.Mock(return_value= return_v)
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).press(key_code) == state

    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    @pytest.mark.parametrize('key_code, not_ignore, timeout, return_v, state', [('ESC', True, 5, True, True),
                                                                                ('F2', True, 5, False, False)])
    def test_press_key(serial, adapter, key_code, not_ignore, timeout, return_v, state):
        adapter.return_value.data_adapter['setup_menu'].press_key = mock.Mock(return_value=return_v)
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).press_key(key_code, not_ignore, timeout) == state

    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    @pytest.mark.parametrize('timeout, return_v, state', [( 5, True, True),
                                                          ( 5, None, None)])
    def test_wait_for_entry_menu(serial, adapter, timeout, return_v, state):
        adapter.return_value.data_adapter['entry_menu'].wait_for_entrymenu = mock.Mock(return_value=return_v)
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).wait_for_entry_menu(timeout) == state

    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    @pytest.mark.parametrize('timeout, return_v, state', [( 5, True, True)])
    def test_get_current_screen_info(serial, adapter, timeout, return_v, state):
        adapter.return_value.data_adapter['setup_menu'].get_current_screen_info = mock.Mock(return_value=return_v)
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).get_current_screen_info() == state



    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    @pytest.mark.parametrize('item_name, item_type, use_regex, timeout, return_v, state', [('bios', 'BIOS_UI_OPT_TYPE', True, 5, 'SUCCESS', 'SUCCESS'),
                                                                                           ('bios', 'BIOS_UI_OPT_TYPE', True, 5, 'TEST_FAIL','TEST_FAIL'),
                                                                                           ('dasd' , 'BIOS_UI_OPT_TYPE', True, 5, 'INVALID_INPUT','INVALID_INPUT'),
                                                                          ])
    def test_select(serial,adapter, item_name, item_type, use_regex, timeout, return_v, state):
        adapter.return_value.data_adapter['setup_menu'].select = mock.Mock(return_value= return_v)
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).select(item_name, item_type, use_regex, timeout) == state


    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    @pytest.mark.parametrize('path, use_regex, timeout_config, is_page_info', [('bios', 'BIOS_UI_OPT_TYPE', True, 5),
                                                                          ])
    def test_goto(serial,adapter, path, use_regex, timeout_config, is_page_info):
        adapter.return_value.data_adapter['setup_menu'].goto = mock.Mock(return_value='SUCCESS')
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).goto(path, use_regex, timeout_config, is_page_info) == 'SUCCESS'



    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    @pytest.mark.parametrize('timeout, is_page_info', [(5, True),
                                                         ])
    def test_back_to_root(serial, adapter, timeout, is_page_info):
        adapter.return_value.data_adapter['setup_menu'].back_to_root = mock.Mock(return_value='SUCCESS')
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).back_to_root(timeout, is_page_info) == 'SUCCESS'


    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    @pytest.mark.parametrize('ignore, timeout', [(True, True) ])
    def test_enter_selected_item(serial, adapter, ignore, timeout):
        adapter.return_value.data_adapter['setup_menu'].enter_selected_item = mock.Mock(return_value='SUCCESS')
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).enter_selected_item(ignore, timeout) == 'SUCCESS'


    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    def test_get_selected_item(serial, adapter):
        adapter.return_value.data_adapter['setup_menu'].get_selected_item = mock.Mock(return_value='SUCCESS')
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).get_selected_item() == 'SUCCESS'


    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    def test_get_page_information(serial, adapter):
        adapter.return_value.data_adapter['setup_menu'].get_page_information = mock.Mock(return_value='SUCCESS')
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).get_page_information() == 'SUCCESS'


    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    def test_scan_current_page_items(serial, adapter):
        adapter.return_value.data_adapter['setup_menu'].scan_current_page_items = mock.Mock(return_value='SUCCESS')
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).scan_current_page_items() == 'SUCCESS'


    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    @pytest.mark.parametrize('item_name, timeout, use_regex',[('F1', 5, True)])
    def test_wait_for_popup_hightlight(serial, adapter, item_name, timeout, use_regex):
        adapter.return_value.data_adapter['setup_menu'].wait_for_popup_hightlight = mock.Mock(return_value='SUCCESS')
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).wait_for_popup_hightlight(item_name, timeout, use_regex) == 'SUCCESS'

    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    @pytest.mark.parametrize('text',['F2'])
    def test_input_text(serial, adapter, text):
        adapter.return_value.data_adapter['setup_menu'].input_text = mock.Mock(return_value='SUCCESS')
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).input_text(text) == 'SUCCESS'


    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    @pytest.mark.parametrize('value, use_regex, ', [('F2', True)])
    def test_select_from_popup(serial, adapter, value, use_regex):
        adapter.return_value.data_adapter['setup_menu'].select_from_popup = mock.Mock(return_value='SUCCESS')
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).select_from_popup(value, use_regex) == 'SUCCESS'


    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    @pytest.mark.parametrize('order_list', [([1, 2])])
    def test_change_order(serial, adapter, order_list):
        adapter.return_value.data_adapter['setup_menu'].change_order = mock.Mock(return_value='SUCCESS')
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).change_order(order_list) == 'SUCCESS'


    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    def test_is_check_type(serial, adapter):
        adapter.return_value.data_adapter['setup_menu'].is_check_type = mock.Mock(return_value='SUCCESS')
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).is_check_type() == 'SUCCESS'

    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    @pytest.mark.parametrize('timeout, return_v, state', [(5, 'SUCCESS', 'SUCCESS'),
                                                (None, 'INVALID_INPUT', 'INVALID_INPUT')])
    def test_wait_for_bios_ui(serial, adapter, timeout, return_v, state):
        adapter.return_value.data_adapter['setup_menu'].wait_for_bios_ui = mock.Mock(return_value=return_v)
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).wait_for_bios_ui(timeout) == state

    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    @pytest.mark.parametrize('timeout, return_v, state', [(5, 'SUCCESS', 'SUCCESS'),
                                                (None, 'INVALID_INPUT', 'INVALID_INPUT')])
    def test_wait_for_bios_setup_menu(serial, adapter, timeout, return_v, state):
        adapter.return_value.data_adapter['setup_menu'].wait_for_bios_setup_menu = mock.Mock(return_value=return_v)
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).wait_for_bios_setup_menu(timeout) == state

    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    @pytest.mark.parametrize('timeout, return_v, state', [(5, 'SUCCESS', 'SUCCESS'),
                                                          (None, 'INVALID_INPUT', 'INVALID_INPUT')])
    def test_enter_efishell(serial, adapter, timeout, return_v, state):
        adapter.return_value.data_adapter['setup_menu'].enter_efishell= mock.Mock(return_value=return_v)
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).enter_efishell(timeout) == state


    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    def test_continue_to_os(serial, adapter):
        adapter.return_value.data_adapter['setup_menu'].continue_to_os = mock.Mock(return_value='SUCCESS')
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).continue_to_os() == 'SUCCESS'


    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    @pytest.mark.parametrize('timeout, return_v, state', [(5, 'SUCCESS', 'SUCCESS'),
                                                          (None, 'INVALID_INPUT', 'INVALID_INPUT')])
    def test_reboot(serial, adapter, timeout, return_v, state):
        adapter.return_value.data_adapter['setup_menu'].reboot = mock.Mock(return_value=return_v)
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).reboot(timeout) == state

    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    def test_get_title(serial, adapter):
        adapter.return_value.data_adapter['setup_menu'].get_title = mock.Mock(return_value='SUCCESS')
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).get_title() == 'SUCCESS'

    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    @pytest.mark.parametrize('item_list, new_item', [([], '')])
    def test_check_item_repeat(serial, adapter, item_list, new_item):
        adapter.return_value.data_adapter['setup_menu'].check_item_repeat = mock.Mock(return_value='SUCCESS')
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).check_item_repeat(item_list, new_item) == 'SUCCESS'


    @staticmethod
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    def test_get_highlight_with_position(serial, adapter):
        adapter.return_value.data_adapter['setup_menu'].get_highlight_with_position = mock.Mock(return_value=('SUCCESS', True, (None, None)))
        assert BaseBiosSetupMenuProvider(cfg_opts_normal, log).get_highlight_with_position()[1] == True





























