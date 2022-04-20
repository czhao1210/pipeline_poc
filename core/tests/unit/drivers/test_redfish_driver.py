import xml.etree.ElementTree as ET

import mock
import pytest

from dtaf_core.drivers.internal.redfish_driver import RedfishDriver


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


log = _Log()

cnf_normal = ET.fromstring("""
                        <redfish>
                            <ip>xxx.xxx.xxx.xxx</ip>
                            <username>xxx</username>
							<password>xxx</password>
							<image_name>demo.rom</image_name>
                        </redfish>
""")


class RaiseError():
    def Exception_error(self):
        raise Exception('My error.')


def return_mock(return_value):
    def return_func(*args, **kwargs):
        return return_value

    return return_func


class SessionMock():
    def __init__(self, post_status_code_value=None, post_content_value=None,
                 get_status_code_value=None, get_content_value=None, *args, **kwargs):
        self.post_status_code_value = post_status_code_value
        self.post_content_value = post_content_value
        self.get_status_code_value = get_status_code_value
        self.get_content_value = get_content_value

    def post(self, *args, **kwargs):
        return PostMock(status_code_value=self.post_status_code_value, content_value=self.post_content_value)

    def get(self, *args, **kwargs):
        return GetMock(status_code_value=self.get_status_code_value, content_value=self.get_content_value)


class PostMock():

    def __init__(self, status_code_value=None, content_value=None, *args, **kwargs):
        if status_code_value == 'Exception_error':
            self.status_code = RaiseError().Exception_error()
        else:
            self.status_code = status_code_value
            self.content = content_value


class GetMock():

    def __init__(self, status_code_value=None, content_value=None, *args, **kwargs):
        if status_code_value == 'Exception_error':
            self.status_code = RaiseError().Exception_error()
        else:
            self.status_code = status_code_value
            self.content = content_value

    def json(self):
        return {"PowerState": "default_On", "FirmwareVersion": "test_version"}


class TestRedfishDrive(object):
    @staticmethod
    @pytest.mark.parametrize("post_status_code_value", [100, 200, 'Exception_error'])
    def test_ac_power_on(post_status_code_value):
        with RedfishDriver(cnf_normal, log) as rd_obj:
            rd_obj.session = SessionMock(post_status_code_value=post_status_code_value, post_content_value='abc')
            try:
                rd_obj.ac_power_on(10)
            except:
                pass

    @staticmethod
    @pytest.mark.parametrize("post_status_code_value", [100, 200, 'Exception_error'])
    def test_ac_power_off(post_status_code_value):
        with RedfishDriver(cnf_normal, log) as rd_obj:
            rd_obj.session = SessionMock(post_status_code_value=post_status_code_value, post_content_value='abc')
            try:
                rd_obj.ac_power_off(10)
            except:
                pass

    @staticmethod
    @pytest.mark.parametrize("post_status_code_value", [100, 200, 'Exception_error'])
    def test_get_ac_power_state(post_status_code_value):
        with RedfishDriver(cnf_normal, log) as rd_obj:
            rd_obj.session = SessionMock(post_status_code_value=post_status_code_value, post_content_value='abc')
            rd_obj.get_ac_power_state()
            rd_obj.session.get = mock.Mock()
            rd_obj.session.get.return_value.status_code = 200
            rd_obj.session.get.return_value.json.return_value = {'PowerState': 'On'}
            rd_obj.get_ac_power_state()
            rd_obj.session.get.return_value.json.return_value = {'PowerState': 'Off'}
            rd_obj.get_ac_power_state()

    @staticmethod
    @pytest.mark.parametrize("post_status_code_value", [100, 200, 'Exception_error'])
    def test_clear_cmos(post_status_code_value):
        with RedfishDriver(cnf_normal, log) as rd_obj:
            rd_obj.session = SessionMock(post_status_code_value=post_status_code_value, post_content_value='abc')
            try:
                rd_obj.clear_cmos()
            except:
                pass

    @staticmethod
    @pytest.mark.parametrize("post_status_code_value", [100, 200, 'Exception_error'])
    def test_dc_power_on(post_status_code_value):
        with RedfishDriver(cnf_normal, log) as rd_obj:
            rd_obj.session = SessionMock(post_status_code_value=post_status_code_value, post_content_value='abc')
            try:
                rd_obj.dc_power_on()
            except:
                pass

    @staticmethod
    @pytest.mark.parametrize("post_status_code_value", [100, 200, 'Exception_error'])
    def test_dc_power_off(post_status_code_value):
        with RedfishDriver(cnf_normal, log) as rd_obj:
            rd_obj.session = SessionMock(post_status_code_value=post_status_code_value, post_content_value='abc')
            try:
                rd_obj.dc_power_off()
            except:
                pass

    @staticmethod
    @pytest.mark.parametrize("get_status_code_value", [100, 200, 'Exception_error'])
    def test_get_dc_power_state(get_status_code_value):
        with RedfishDriver(cnf_normal, log) as rd_obj:
            rd_obj.session = SessionMock(get_status_code_value=get_status_code_value, get_content_value='abc')
            try:
                rd_obj.get_dc_power_state()
            except:
                pass
            rd_obj.session.get = mock.Mock()
            rd_obj.session.get.return_value.json.return_value = {'PowerState': 'Off'}
            rd_obj.session.get.return_value.status_code = 200
            rd_obj.get_dc_power_state()

    @staticmethod
    @pytest.mark.parametrize("post_status_code_value", [100, 200, 'Exception_error'])
    def test_dc_power_reset(post_status_code_value):
        with RedfishDriver(cnf_normal, log) as rd_obj:
            rd_obj.session = SessionMock(post_status_code_value=post_status_code_value, post_content_value='abc')
            try:
                rd_obj.dc_power_reset()
            except:
                pass

    @staticmethod
    @pytest.mark.parametrize("post_status_code_value,redfish_cmd",
                             [(100, None),
                              (200, None),
                              ('Exception_error', RaiseError)])
    def test_execute(post_status_code_value, redfish_cmd):
        from dtaf_core.drivers.internal.redfish_driver import requests
        from dtaf_core.drivers.internal import redfish_driver
        redfish_driver.__dict__["ipmi_cmd"] = "a"
        with RedfishDriver(cnf_normal, log) as rd_obj:
            requests.session = mock.Mock(
                return_value=SessionMock(post_status_code_value=post_status_code_value, post_content_value='abc'))
            try:
                rd_obj.execute(redfish_cmd=redfish_cmd)
            except:
                pass

    @staticmethod
    @pytest.mark.parametrize("get_status_code_value", [100, 200, 'Exception_error'])
    def test_current_bmc_version_check(get_status_code_value):
        from dtaf_core.drivers.internal.redfish_driver import requests
        with RedfishDriver(cnf_normal, log) as rd_obj:
            requests.session = mock.Mock(
                return_value=SessionMock(get_status_code_value=get_status_code_value, get_content_value='abc'))
            try:
                rd_obj.current_bmc_version_check()
            except:
                pass

    @staticmethod
    @pytest.mark.parametrize("get_status_code_value", [100, 200, 'Exception_error'])
    def test_current_bmc_version_check_one_Timer(get_status_code_value):
        from dtaf_core.drivers.internal.redfish_driver import requests
        with RedfishDriver(cnf_normal, log) as rd_obj:
            requests.session = mock.Mock(
                return_value=SessionMock(get_status_code_value=get_status_code_value, get_content_value='abc'))
            try:
                rd_obj.current_bmc_version_check(one_Timer=True)
            except:
                pass

    @staticmethod
    @pytest.mark.parametrize("post_status_code_value,image_name",
                             [(100, __file__),
                              (202, __file__),
                              ('Exception_error', __file__)])
    def test_chip_flash_bmc(post_status_code_value, image_name):
        from dtaf_core.drivers.internal.redfish_driver import requests
        with RedfishDriver(cnf_normal, log) as rd_obj:
            requests.session = mock.Mock(
                return_value=SessionMock(post_status_code_value=post_status_code_value, post_content_value='abc'))
            try:
                rd_obj.chip_flash_bmc(image_name=image_name)
            except:
                pass

    @staticmethod
    @pytest.mark.parametrize("get_status_code_value", [100, 200, 'Exception_error'])
    def test_current_bios_version_check(get_status_code_value):
        from dtaf_core.drivers.internal.redfish_driver import requests
        with RedfishDriver(cnf_normal, log) as rd_obj:
            requests.session = mock.Mock(
                return_value=SessionMock(get_status_code_value=get_status_code_value, get_content_value='abc'))
            try:
                rd_obj.current_bios_version_check()
            except:
                pass

    @staticmethod
    @pytest.mark.parametrize("get_status_code_value", [100, 200, 'Exception_error'])
    def test_current_bios_version_check_one_Timer(get_status_code_value):
        from dtaf_core.drivers.internal.redfish_driver import requests
        with RedfishDriver(cnf_normal, log) as rd_obj:
            requests.session = mock.Mock(
                return_value=SessionMock(get_status_code_value=get_status_code_value, get_content_value='abc'))
            try:
                rd_obj.current_bios_version_check(one_Timer=True)
            except:
                pass

    @staticmethod
    @pytest.mark.parametrize("post_status_code_value,image_name",
                             [(100, __file__),
                              (202, __file__),
                              ('Exception_error', __file__)])
    def test_chip_flash_bios(post_status_code_value, image_name):
        from dtaf_core.drivers.internal.redfish_driver import requests
        with RedfishDriver(cnf_normal, log) as rd_obj:
            requests.session = mock.Mock(
                return_value=SessionMock(post_status_code_value=post_status_code_value, post_content_value='abc'))
            rd_obj.current_bios_version_check = mock.Mock()
            try:
                rd_obj.chip_flash_bios(image_name=image_name)
            except:
                pass

    @staticmethod
    @pytest.mark.parametrize("get_status_code_value", [100, 200, 'Exception_error'])
    def test_current_cpld_version_check(get_status_code_value):
        from dtaf_core.drivers.internal.redfish_driver import requests
        with RedfishDriver(cnf_normal, log) as rd_obj:
            requests.session = mock.Mock(
                return_value=SessionMock(get_status_code_value=get_status_code_value, get_content_value='abc'))
            try:
                rd_obj.current_cpld_version_check()
            except:
                pass

    @staticmethod
    @pytest.mark.parametrize("get_status_code_value", [100, 200, 'Exception_error'])
    def test_current_cpld_version_check_one_Timer(get_status_code_value):
        from dtaf_core.drivers.internal.redfish_driver import requests
        with RedfishDriver(cnf_normal, log) as rd_obj:
            requests.session = mock.Mock(
                return_value=SessionMock(get_status_code_value=get_status_code_value, get_content_value='abc'))
            try:
                rd_obj.current_cpld_version_check(one_Timer=True)
            except:
                pass

    @staticmethod
    @pytest.mark.parametrize("post_status_code_value,image_name",
                             [(100, __file__),
                              (202, __file__),
                              ('Exception_error', __file__)])
    def test_chip_flash_cpld(post_status_code_value, image_name):
        from dtaf_core.drivers.internal.redfish_driver import requests
        with RedfishDriver(cnf_normal, log) as rd_obj:
            requests.session = mock.Mock(
                return_value=SessionMock(post_status_code_value=post_status_code_value, post_content_value='abc'))
            try:
                rd_obj.chip_flash_cpld(image_name=image_name)
            except:
                pass

    @staticmethod
    @pytest.mark.parametrize("post_status_code_value,image_name",
                             [(100, __file__),
                              (202, __file__),
                              ('Exception_error', __file__)])
    def test_read_volt(post_status_code_value, image_name):
        from dtaf_core.drivers.internal.redfish_driver import requests
        with RedfishDriver(cnf_normal, log) as rd_obj:
            requests.session = mock.Mock(
                return_value=SessionMock(post_status_code_value=post_status_code_value, post_content_value='abc'))
            try:
                rd_obj.read_volt()
            except:
                pass

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.redfish_driver.json')
    def test_platform_postcode(json_mock):
        with RedfishDriver(cnf_normal, log) as rd_obj:
            rd_obj.platform_postcode()

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.redfish_driver.json')
    def test_set_bios_category_bootorder(json_mock):
        with RedfishDriver(cnf_normal, log) as rd_obj:
            rd_obj.set_bios_category_bootorder()

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.redfish_driver.json')
    def test_get_bios_category_bootorder(json_mock):
        with RedfishDriver(cnf_normal, log) as rd_obj:
            try:
                rd_obj.get_bios_category_bootorder()
            except AttributeError:
                pass

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.redfish_driver.json')
    @mock.patch('dtaf_core.drivers.internal.redfish_driver.requests')
    def test_get_system_info(requests_mock, json_mock):
        requests_mock.session.return_value.get.return_value.json.return_value = {
            'ChassisType': 'abc', 'Manufacturer': 'abc', 'Model': 'abc', 'PartNumber': 'abc', 'SerialNumber': 'abc',
            'UUID': 'abc'}
        with RedfishDriver(cnf_normal, log) as rd_obj:
            rd_obj.get_system_info()

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.redfish_driver.json')
    @mock.patch('dtaf_core.drivers.internal.redfish_driver.requests')
    def test_get_system_status_led(requests_mock, json_mock):
        requests_mock.session.return_value.get.return_value.json.return_value = {
            'MemorySummary': {'Status': {'Health': 'abc'}},
            'ProcessorSummary': {'Status': {'Health': 'abc'}},
            'Status': {'Health': 'abc'}}
        with RedfishDriver(cnf_normal, log) as rd_obj:
            try:
                rd_obj.get_system_status_led()
            except UnboundLocalError:
                return
