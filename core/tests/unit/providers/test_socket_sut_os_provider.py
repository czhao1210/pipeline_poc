import six

from dtaf_core.lib.exceptions import OsStateTransitionException, OsBootTimeoutException, DriverIOError, \
    OsCommandException
from dtaf_core.lib.os_lib import OsCommandResult

if six.PY2:
    import mock

if six.PY3 or six.PY34:
    import mock
from dtaf_core.providers.internal.socket_sut_os_provider import SocketSutOsProvider
from dtaf_core.drivers.driver_factory import DriverFactory
from xml.etree import ElementTree as ET


class _Logs:
    def debug(self,*args, **kwargs):
        pass
    def error(self,*args, **kwargs):
        pass
    def info(self,*args, **kwargs):
        pass

class SD(object):
    def __init__(self):
        self.side_effect = list()
        self.return_data = list()
        self.count = 0

    def close(self):
        pass

    def open(self):
        pass

    def receive(self, timeout):
        if self.return_data:
            cur = self.count
            self.count += 1
            return self.return_data[cur]

    def send(self, data):
        if self.side_effect:
            cur = self.count
            self.count += 1
            raise self.side_effect[cur]

class _File(object):
    def write(self, data):
        self.return_data = list()
        self.count = 0

    def read(self, size):
        if self.return_data:
            cur = self.count
            self.count += 1
            return self.return_data[cur]

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

class Std(object):
    def __init__(self):
        self.lines = list()

    def readlines(self):
        return self.lines

cfg_normal = ET.fromstring("""
                <sut_os name="Linux" subtype="RHEL" version="7.6" kernel="3.10">
                    <shutdown_delay>5.0</shutdown_delay>
                    <driver>
                        <socket>
                            <ip>127.0.0.1</ip>
                            <port>5555</port>
                            <bufsize>1030</bufsize>
                        </socket>
                    </driver>
                </sut_os>
    """)


class TestSocketSutOsProvider:

    def setup_method(self):
        pass

    def teardown_method(self):
        pass

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.socket_sut_os_provider.SocketSutOsProvider.wait_for_os", return_value=None)
    @mock.patch("time.sleep", return_value=None)
    @mock.patch("dtaf_core.providers.internal.socket_sut_os_provider.SocketSutOsProvider.is_alive", side_effect=[False, True, False, True])
    @mock.patch("dtaf_core.drivers.driver_factory.DriverFactory.create", return_value=SD())
    @mock.patch("dtaf_core.providers.internal.socket_sut_os_provider.SocketSutOsProvider.execute_async")
    def test_socket_normal(execMock, cMock, iMock, tMock, wMock):
        with SocketSutOsProvider(cfg_normal, _Logs) as socket:
            socket.reboot(10)
            has_exception = False
            try:
                socket.reboot(10)
            except OsStateTransitionException as ex:
                has_exception = True
            assert has_exception
            has_exception = False
            socket.shutdown(10)
            has_exception = False
            try:
                socket.shutdown(10)
            except OsStateTransitionException as ex:
                has_exception = True
            assert has_exception
            has_exception = False

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.socket_sut_os_provider.open", return_value=_File())
    @mock.patch("dtaf_core.drivers.driver_factory.DriverFactory.create", return_value=SD())
    @mock.patch("dtaf_core.providers.internal.socket_sut_os_provider.json.loads",
                side_effect=[dict(ENTEROS=("linux", "S0")),
                             dict(ENTEROS=("WrongOS", "S0")),
                             dict(RESPONSE=(0, 0, "")),
                             dict(RESPONSE=(1, 1, "")),
                             dict(RESPONSE=(0, 0, "")),
                             dict(RESPONSE=(1, 1, "")),
                             dict(RESPONSE=(0, 0, "")), # file
                             dict(RESPONSE=(0, 0, "")),
                             dict(RESPONSE=(1, 1, "")), # file
                             dict(RESPONSE=(0, 0, "test0")),
                             dict(RESPONSE=(0, 0, "test1")),
                             dict(RESPONSE=(0, 0, "")), # file
                             dict(RESPONSE=(0, 0, "")),
                             dict(RESPONSE=(1, 1, ""))])
    def test_socket_api(lMock, sMock, foMock):
        with SocketSutOsProvider(cfg_normal, _Logs) as socket: #type: SocketSutOsProvider
            socket.wait_for_os(10)
            has_exception = False
            try:
                socket.wait_for_os(10)
            except OsBootTimeoutException as ex:
                has_exception = True
            assert has_exception
            has_exception = False
            assert socket.execute("dir", 10).return_code == 0
            assert socket.execute("dir", 10).return_code == 1
            assert socket.is_alive()
            assert not socket.is_alive()
            # aync
            assert socket.execute_async("dir").return_code == 0
            sMock.return_value.side_effect = [DriverIOError("UT"), KeyError("UT")]
            has_exception = False
            try:
                socket.execute_async("dir")
            except OsCommandException as e:
                has_exception = True
            assert has_exception
            has_exception = False
            try:
                socket.execute_async("dir")
            except OsCommandException as e:
                has_exception = True
            assert has_exception
            ## file
            sMock.return_value.side_effect = list()
            sMock.return_value.count = 0
            foMock.return_value.return_data = [b"hello", None]
            foMock.return_value.count = 0
            assert socket.copy_local_file_to_sut("source", "dest").return_code == 0
            sMock.return_value.side_effect = list()
            sMock.return_value.count = 0
            foMock.return_value.return_data = [b"hello", None]
            foMock.return_value.count = 0
            try:
                has_exception = False
                assert socket.copy_local_file_to_sut("source", "dest").return_code == 1
            except OsCommandException as ex:
                has_exception = True
            assert has_exception
            ## file: sut to local
            sMock.return_value.side_effect = list()
            sMock.return_value.count = 0
            import json
            sMock.return_value.return_data = [b"hello", None,
                                              json.dumps(dict(RESPONSE=(0, 0, "test"))),
                                              json.dumps(dict(RESPONSE=(0, 0, "")))]
            assert socket.copy_file_from_sut_to_local("source", "dest").return_code == 0
            sMock.return_value.side_effect = list()
            sMock.return_value.count = 0
            sMock.return_value.return_data = [b"hello", None, json.dumps(dict(RESPONSE=(1, 1, "")))]
            try:
                has_exception = False
                assert socket.copy_file_from_sut_to_local("source", "dest").return_code == 1
            except OsCommandException as ex:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.socket_sut_os_provider.SocketSutOsProvider.execute")
    @mock.patch("dtaf_core.drivers.driver_factory.DriverFactory.create", return_value=SD())
    def test_socket_check_files(sMock, eMock):
        s = Std()
        s.lines = [r"0 Dir(s)", r"1 File(s)"]
        e = Std()
        eMock.return_value = OsCommandResult(0, s, e)
        with SocketSutOsProvider(cfg_normal, _Logs) as socket:  # type: SocketSutOsProvider
            assert socket.check_if_path_exists("test", True)

