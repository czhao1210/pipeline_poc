from xml.etree import ElementTree as ET

import mock
from dtaf_core.lib.exceptions import OsStateTransitionException, OsBootTimeoutException, TimeoutException, \
    OsCommandException
from dtaf_core.lib.os_lib import OsCommandResult
from dtaf_core.providers.internal.base_sut_os_provider import BaseSutOsProvider
from serial import SerialException

cfg_normal_com = ET.fromstring("""
    <sut_os name="Linux" subtype="RHEL" version="7.6" kernel="3.10">
        <shutdown_delay>10</shutdown_delay>
        <driver>
            <com>
                <baudrate>115200</baudrate>
                <port>COM100</port>
                <timeout>5</timeout>
            </com>
        </driver>
    </sut_os>
""")


class _Std(object):
    def write(self, data):
        return True


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


class TestBaseSutOsProvider(object):
    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_sut_os_provider.Message")
    @mock.patch("dtaf_core.providers.internal.base_sut_os_provider.time.sleep")
    @mock.patch("dtaf_core.providers.internal.base_sut_os_provider.BaseSutOsProvider.wait_for_os")
    @mock.patch("dtaf_core.providers.internal.base_sut_os_provider.BaseSutOsProvider.execute")
    @mock.patch("dtaf_core.drivers.driver_factory.DriverFactory.create")
    def test_reboot(c, e, w, s, m):
        m.send.return_val = True
        with BaseSutOsProvider(cfg_normal_com, _Log()) as sut:  # type: BaseSutOsProvider
            sut.reboot(10)

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_sut_os_provider.time.sleep")
    @mock.patch("dtaf_core.providers.internal.base_sut_os_provider.BaseSutOsProvider.is_alive",
                side_effect=[False, True])
    @mock.patch("dtaf_core.providers.internal.base_sut_os_provider.BaseSutOsProvider.execute_async")
    @mock.patch("dtaf_core.drivers.driver_factory.DriverFactory.create")
    def test_shutdown(c, e, w, s):
        with BaseSutOsProvider(cfg_normal_com, _Log()) as sut:  # type: BaseSutOsProvider
            sut.shutdown(10)
            has_exception = False
            try:
                sut.shutdown(10)
            except OsStateTransitionException as ex:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_sut_os_provider.json.loads", side_effect=[
        dict(ENTEROS=("linux", "S0")),
        dict(ENTEROS=("WrongOS", "S0"))]
                )
    @mock.patch("dtaf_core.providers.internal.base_sut_os_provider.Message.receive")
    @mock.patch("dtaf_core.drivers.driver_factory.DriverFactory.create")
    def test_shutdown(c, r, l):
        with BaseSutOsProvider(cfg_normal_com, _Log()) as sut:  # type: BaseSutOsProvider
            sut.wait_for_os((10))
            has_exception = False
            try:
                sut.wait_for_os(10)
            except OsBootTimeoutException as ex:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_sut_os_provider.json.loads", side_effect=[
        dict(ENTEROS=("linux", "S0")),
        dict(ENTEROS=("WrongOS", "S0"))]
                )
    @mock.patch("dtaf_core.providers.internal.base_sut_os_provider.Message.receive")
    @mock.patch("dtaf_core.drivers.driver_factory.DriverFactory.create")
    def test_wait_for_os(c, r, l):
        with BaseSutOsProvider(cfg_normal_com, _Log()) as sut:  # type: BaseSutOsProvider
            sut.wait_for_os((10))
            has_exception = False
            try:
                sut.wait_for_os(10)
            except OsBootTimeoutException as ex:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_sut_os_provider.BaseSutOsProvider.execute", side_effect=[
        OsCommandResult(0, 0, None),
        OsCommandResult(1, 1, None),
        TimeoutException("UT"),
        TypeError("UT")
    ])
    @mock.patch("dtaf_core.drivers.driver_factory.DriverFactory.create")
    def test_is_alive(c, e):
        with BaseSutOsProvider(cfg_normal_com, _Log()) as sut:  # type: BaseSutOsProvider
            assert sut.is_alive()
            assert not sut.is_alive()
            assert not sut.is_alive()
            assert not sut.is_alive()

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.base_sut_os_provider.json.loads", side_effect=[
        dict(RESPONSE=(0, 0, "test")),
        SerialException("UT"),
        TypeError("UT")
    ])
    @mock.patch("dtaf_core.providers.internal.base_sut_os_provider.Message.send")
    @mock.patch("dtaf_core.providers.internal.base_sut_os_provider.Message.receive")
    @mock.patch("dtaf_core.drivers.driver_factory.DriverFactory.create")
    def test_execute(c, r, s, l):
        with BaseSutOsProvider(cfg_normal_com, _Log()) as sut:  # type: BaseSutOsProvider
            # invalid command
            try:
                has_exception = False
                assert sut.execute(1, 10).return_code == 0
            except OsCommandException as ex:
                has_exception = True
            assert has_exception
            # invalid timeout
            try:
                has_exception = False
                assert sut.execute("dir", "aa").return_code == 0
            except OsCommandException as ex:
                has_exception = True
            assert has_exception
            assert sut.execute("dir", 10).return_code == 0
            # serial Exception
            try:
                has_exception = False
                assert sut.execute("dir", 10).return_code == 0
            except OsCommandException as ex:
                has_exception = True
            assert has_exception
            #  Exception
            try:
                has_exception = False
                assert sut.execute("dir", 10).return_code == 0
            except OsCommandException as ex:
                has_exception = True
            assert has_exception
