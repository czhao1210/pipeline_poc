import six
if six.PY2:
    import mock

if six.PY3 or six.PY34:
    from unittest import mock

import pytest
from dtaf_core.providers.internal.base_bios_bootmenu_provider import BaseBiosBootmenuProvider
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

class _Serial(object):

    def __init__(self,port='/dev/ttyS0',baudrate=9600,timeout=30,write_timeout=5):
        self.write_timeout = write_timeout
        self.path = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.open()

    def read(self, size=1):
        if size > 0:
            read = bytearray(b"abcdefg")
            return bytes(read)

    def write(self, data):
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError('expected %s or bytearray, got %s' % (bytes, type(data)))

        return len(data)

    @property
    def in_waiting(self, data=1):
        return data

    @staticmethod
    def register(buffer_name='', size=4096):
        pass

    @staticmethod
    def read_from(buffer_name=''):
        return ''

    def open(self):
        self.is_open = True

    def close(self):
        if self.is_open:
            # if self.sPort:
            #     self.sPort.close()
            #     self.sPort = None
            self.is_open = False

class TestBaseBiosBootmenuProvider(object):
    @staticmethod
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    @pytest.mark.parametrize('key_code, return_v, state', [('F2', True, True),
                                                 ('F7', True, True),
                                                 ('ESC', False, False)])
    def test_press(serial, adapter, cfg, provider,  key_code, return_v, state):
        cfg.return_value.tag = 'com'
        adapter.return_value.data_adapter['entry_menu'].press = mock.Mock(return_value= return_v)
        assert BaseBiosBootmenuProvider(cfg_opts, log).press(key_code) == state


    @staticmethod
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    @pytest.mark.parametrize('key_code,  return_v, state', [('ESC', True, True),
                                                             ('F2', False, False)])
    def test_press_key(serial, adapter, cfg, provider,  key_code, return_v, state):
        cfg.return_value.tag = 'com'
        adapter.return_value.data_adapter['boot_menu'].press_key = mock.Mock(return_value=return_v)
        assert BaseBiosBootmenuProvider(cfg_opts, log).press_key(key_code) == state

    @staticmethod
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch.object(serial, 'Serial')
    @pytest.mark.parametrize('timeout, return_v, state', [( 5, True, True),
                                                          ( 5, None, None)])
    def test_wait_for_entry_menu(serial, adapter, cfg, provider, timeout, return_v, state):
        cfg.return_value.tag = 'com'
        adapter.return_value.data_adapter['entry_menu'].wait_for_entrymenu = mock.Mock(return_value=return_v)
        assert BaseBiosBootmenuProvider(cfg_opts, log).wait_for_entry_menu(timeout) == state

    @staticmethod
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch('dtaf_core.drivers.internal.com_driver.serial.Serial', return_value=_Serial())
    @pytest.mark.parametrize('item_name, item_type, timeout, use_regex, return_v, state', [('bios', 'BIOS_UI_OPT_TYPE', 5, True, 'SUCCESS', True),
                                                                                           ('', 'BIOS_UI_OPT_TYPE', 5, True, 'TEST_FAIL', False),
                                                                                           ('bios', 'BIOS_UI_OPT_TYPE', 5, False, 'TEST_FAIL', False),
                                                                          ])
    def test_select(serial,adapter, cfg, provider, item_name, item_type, timeout, use_regex,return_v, state):
        cfg.return_value.tag = 'com'
        adapter.return_value.data_adapter['boot_menu'].select = mock.Mock(return_value=return_v)
        assert BaseBiosBootmenuProvider(cfg_opts, log).select(item_name, item_type, timeout, use_regex) == state

    @staticmethod
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch('dtaf_core.drivers.internal.com_driver.serial.Serial', return_value=_Serial())
    @pytest.mark.parametrize('timeout, ignore_output, return_v, state', [(5, True, 'SUCCESS', True),
                                                                         (5, True, 'TEST_FAIL', False),
                                                         ])
    def test_enter_selected_item(serial,adapter, cfg, provider, timeout, ignore_output, return_v, state):
        cfg.return_value.tag = 'com'
        adapter.return_value.data_adapter['boot_menu'].enter_selected_item = mock.Mock(return_value=return_v)
        assert BaseBiosBootmenuProvider(cfg_opts, log).enter_selected_item(timeout, ignore_output) == state

    @staticmethod
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch('dtaf_core.drivers.internal.com_driver.serial.Serial', return_value=_Serial())
    @pytest.mark.parametrize('timeout, return_v, state', [(5, 'SUCCESS', True),
                                                              (5, 'TEST_FAIL', False)])
    def test_wait_for_bios_boot_menu(serial, adapter, cfg, provider, timeout, return_v, state):
        cfg.return_value.tag = 'com'
        adapter.return_value.data_adapter['boot_menu'].wait_for_bios_boot_menu = mock.Mock(return_value=return_v)
        assert BaseBiosBootmenuProvider(cfg_opts, log).wait_for_bios_boot_menu(timeout) == state


    @staticmethod
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch('dtaf_core.drivers.internal.com_driver.serial.Serial', return_value=_Serial())
    @pytest.mark.parametrize('timeout, return_v, state', [(5, 'SUCCESS', True),
                                                          (5, 'TEST_FAIL', False)])
    def test_enter_efishell(serial,adapter, cfg, provider, timeout, return_v, state):
        cfg.return_value.tag = 'com'
        adapter.return_value.data_adapter['boot_menu'].enter_efishell = mock.Mock(return_value=return_v)
        assert BaseBiosBootmenuProvider(cfg_opts, log).enter_efishell(timeout) == state


    @staticmethod
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @mock.patch('dtaf_core.lib.private.context.ContextInstance.get')
    @mock.patch('dtaf_core.drivers.internal.com_driver.serial.Serial', return_value=_Serial())
    @pytest.mark.parametrize('timeout, return_v, state', [(5, 'SUCCESS', True),
                                                          (5, 'TEST_FAIL', False)])
    def test_reboot(serial, adapter, cfg, provider, timeout, return_v, state):
        cfg.return_value.tag = 'com'
        adapter.return_value.data_adapter['boot_menu'].reboot = mock.Mock(return_value=return_v)
        assert BaseBiosBootmenuProvider(cfg_opts, log).reboot(timeout) == state











