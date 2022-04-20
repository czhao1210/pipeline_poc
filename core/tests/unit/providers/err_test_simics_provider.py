import six
if six.PY2:
    import mock

if six.PY3 or six.PY34:
    from unittest import mock

import time
from dtaf_core.providers.internal.com_simics_provider import ComSimicsProvider

from xml.etree import ElementTree as ET
from dtaf_core.lib.configuration import ConfigurationHelper

def read_cfg(filename):
    tree = ET.ElementTree()
    tree.parse(filename)
    root = tree.getroot()

    sut_dict = dict(
        platform=dict(
            attrib=dict(type=r"commercial")
        ),
        silicon=dict()
    )

    sut = ConfigurationHelper.filter_sut_config(root, r"10.13.168.111", sut_filter=sut_dict)[0]
    provider = ConfigurationHelper.get_provider_config(sut=sut, provider_name=r"ac")
    return provider


class Logs:
    def debug(self,*args, **kwargs):
        pass
    def error(self,*args, **kwargs):
        pass
    def info(self,*args, **kwargs):
        pass

def power_on_states_timeout():
    time.sleep(10)
    return r'On'

def power_off_states_timeout():
    time.sleep(10)
    return r'Off'


cfg_normal = ET.fromstring("""
    <simics>
        <driver>
            <com>
                <baudrate>115200</baudrate>
                <port>COM100</port>
                <timeout>5</timeout>
            </com>
        </driver>
        <telnet_port>2121</telnet_port>
        <serial_log>c:\workspace\serial.log</serial_log>
        <workspace>c:\workspace</workspace>
        <simics_path>C:\Program Files\Simics\Simics 5\Simics 5.0.139\win64\\bin</simics_path>
    </simics>
    """)


class TestSimicsProvider:

    def setup_method(self):
        pass

    def teardown_method(self):
        pass

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.com_simics_provider.telnetlib.Telnet")
    @mock.patch("dtaf_core.providers.internal.com_simics_provider.ComSimicsProvider.shutdown_simics",
                return_value="SUCCESS")
    @mock.patch("dtaf_core.providers.internal.com_simics_provider.subprocess.Popen")
    def test_simics_normal(procMock, shutdownFunc, telnetMock):
        telnetMock.return_value.write.return_value = None
        telnetMock.return_value.__read_until.return_value = b"simics>test passed"
        procMock.return_value.communicate.side_effect = [
            ("test line 1\r\ntestline 2\r\ntest line3", ""),
            ("test line 1\r\ntestline 2\r\ntest line3", ""),
        ]
        with mock.patch("time.sleep", return_value=None) as sleepFunc:
            with ComSimicsProvider(cfg_opts=cfg_normal, log=Logs()) as simics:
                assert simics.launch_simics(configuration=dict(bios="ifwi.bin"), simics_script="test.simics") == "SUCCESS"
                telnetMock.return_value.__read_until.return_value = b"running>test passed"
                assert simics.run_simics_command("test", 10).return_code == "SUCCESS"