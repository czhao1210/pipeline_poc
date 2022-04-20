from dtaf_core.providers.internal.sf100_flash_provider import Sf100FlashProvider
import xml.etree.ElementTree as ET
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
<flash>
    <driver>
        <sf100 cli_path="C:\Program Files (x86)\DediProg\SF Programmer\">
            <pch name="SF106223" chip="MX66L51235F" />
            <bmc name="SF113876" chip="MX66L1G45G" />
        </sf100>
    </driver>
</flash>""")
log = _Log()


class TestSuites(object):
    @staticmethod
    @mock.patch('dtaf_core.providers.internal.sf100_flash_provider.platform')
    @mock.patch('dtaf_core.providers.internal.sf100_flash_provider.subprocess')
    def test_flash_image(subprocess_mock, platform_mock):
        subprocess_mock = mock.Mock()
        platform_mock.system.return_value = 'Windows'
        with Sf100FlashProvider(cfg_opts, log) as obj:
            obj.flash_image('a', 'b', 0, 'd')

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.sf100_flash_provider.platform')
    def test_chip_identify(platform_mock):
        platform_mock.system.return_value = 'Windows'
        with Sf100FlashProvider(cfg_opts, log) as obj:
            obj.chip_identify()

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.sf100_flash_provider.platform')
    def test_read(platform_mock):
        platform_mock.system.return_value = 'Windows'
        with Sf100FlashProvider(cfg_opts, log) as obj:
            obj.read()

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.sf100_flash_provider.platform')
    def test_write(platform_mock):
        platform_mock.system.return_value = 'Windows'
        with Sf100FlashProvider(cfg_opts, log) as obj:
            obj.write()

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.sf100_flash_provider.platform')
    def test_current_bios_version_check(platform_mock):
        platform_mock.system.return_value = 'Windows'
        with Sf100FlashProvider(cfg_opts, log) as obj:
            try:
                obj.current_bios_version_check()
            except NotImplementedError:
                return

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.sf100_flash_provider.platform')
    def test_current_bmc_version_check(platform_mock):
        platform_mock.system.return_value = 'Windows'
        with Sf100FlashProvider(cfg_opts, log) as obj:
            try:
                obj.current_bmc_version_check()
            except NotImplementedError:
                return

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.sf100_flash_provider.platform')
    def test_current_cpld_version_check(platform_mock):
        platform_mock.system.return_value = 'Windows'
        with Sf100FlashProvider(cfg_opts, log) as obj:
            try:
                obj.current_cpld_version_check()
            except NotImplementedError:
                return

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.sf100_flash_provider.platform')
    def test_flash_image_bmc(platform_mock):
        platform_mock.system.return_value = 'Windows'
        with Sf100FlashProvider(cfg_opts, log) as obj:
            try:
                obj.flash_image_bmc()
            except NotImplementedError:
                return 

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.sf100_flash_provider.platform')
    def test_init_errot(platform_mock):
        platform_mock.system.return_value = 'a'
        try:
            with Sf100FlashProvider(cfg_opts, log) as obj:
                return
        except RuntimeError:
            return
