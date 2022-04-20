from dtaf_core.providers.internal.pi_flash_provider import PiFlashProvider
import xml.etree.ElementTree as ET
import mock
import pytest


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
						<pi>
                            <ip>10.190.155.174</ip>
                            <port>80</port>
                            <proxy>http://child-prc.intel.com:913</proxy>
							<image_name>xeon-d.bin</image_name>
                        </pi>    
                    </driver>
				</flash>""")
log = _Log()


class CreateMock():
    def __init__(self):
        self.ip = "a"
        self.proxy = "b"


class ErrorMock():
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def chip_flash(self):
        raise Exception("My error.")

    def chip_identify(self):
        raise Exception("My error.")

    def chip_reading(self):
        raise Exception("My error.")


class TestPFProvider(object):
    @staticmethod
    @mock.patch('dtaf_core.providers.internal.pi_flash_provider.DriverFactory')
    @pytest.mark.parametrize("image_name,error", [(True, False), (False, False),
                                                  (True, True), (True, True), ])
    def test_flash_image(df_mock, image_name, error):
        if not error:
            df_mock.create.return_value.chip_flash.return_value = True
        else:
            df_mock.create.return_value = ErrorMock()
        with PiFlashProvider(cfg_opts, log) as PFP_obj:
            try:
                PFP_obj.flash_image(image_name=image_name)
            except:
                pass

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.pi_flash_provider.DriverFactory')
    @pytest.mark.parametrize("error", [True, False])
    def test_chip_identify(df_mock, error):
        if not error:
            df_mock.create.return_value.chip_identify.return_value = True
        else:
            df_mock.create.return_value = ErrorMock()
        with PiFlashProvider(cfg_opts, log) as PFP_obj:
            try:
                PFP_obj.chip_identify()
            except:
                pass

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.pi_flash_provider.DriverFactory')
    @pytest.mark.parametrize("error", [True, False])
    def test_read(df_mock, error):
        if not error:
            df_mock.create.return_value.chip_reading.return_value = True
        else:
            df_mock.create.return_value = ErrorMock()
        with PiFlashProvider(cfg_opts, log) as PFP_obj:
            try:
                PFP_obj.read()
            except:
                pass
