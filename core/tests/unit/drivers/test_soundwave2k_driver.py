import six

from dtaf_core.lib.exceptions import SoundWaveError, InputError

if six.PY2:
    import mock

if six.PY3 or six.PY34:
    from unittest import mock

import pytest
import serial
from dtaf_core.drivers.internal.soundwave2k_driver import SoundWaveSerialPort , Soundwave2kDriver
from dtaf_core.lib.exceptions import InvalidParameterError
import xml.etree.ElementTree as ET
from binascii import a2b_hex

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

cfg_opts = None
cfg_normal = ET.fromstring("""
                                    <soundwave2k enable_s3_detect="False">
                            <baudrate>115200</baudrate>
                            <serial type="1" />
                            <port>COM101</port>
                            <voltagethreholds>
                                <main_power>
                                    <low>0.8</low>
                                    <high>2.85</high>
                                </main_power>
                                <dsw>
                                    <low>0.8</low>
                                    <high>2.85</high>
                                </dsw>
                                <memory>
                                    <low>0.3</low>
                                    <high>2.2</high>
                                </memory>
                            </voltagethreholds>
                        </soundwave2k>
        """
                            )

cfg_normal_s3 = ET.fromstring("""
                                    <soundwave2k enable_s3_detect="True">
                            <baudrate>115200</baudrate>
                            <serial type="1" />
                            <port>COM101</port>
                            <voltagethreholds>
                                <main_power>
                                    <low>0.8</low>
                                    <high>2.85</high>
                                </main_power>
                                <dsw>
                                    <low>0.8</low>
                                    <high>2.85</high>
                                </dsw>
                                <memory>
                                    <low>0.3</low>
                                    <high>2.2</high>
                                </memory>
                            </voltagethreholds>
                        </soundwave2k>
        """
                            )

class SSP(object):
    def __init__(self, data):
        self.data = data

    @staticmethod
    def open():
        return None

    @staticmethod
    def send(*args):
        return True

    def receive(self, size):
        if size == 1:
            return self.data[:int(size)*2]
        else:
            return self.data[2:]

class TestSoundWaveSerialPort:

    @staticmethod
    @mock.patch.object(serial, 'Serial')
    @mock.patch.object(serial.Serial, 'open')
    @mock.patch.object(serial.Serial, 'reset_output_buffer')
    @mock.patch.object(serial.Serial, 'reset_input_buffer')
    @mock.patch.object(serial.Serial, 'write')
    @pytest.mark.parametrize('data, state', [(b"5503000058", True)])
    def test_send(write, input, output, open, serial, data, state):
        write.return_value = 5
        assert SoundWaveSerialPort('1', logger=_Log()).send(data) == state


class TestSoundwave2kDriver(object):

    def ___execute_cmd(self, code, res_len):
        return code.lower()

    @staticmethod
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch("dtaf_core.drivers.internal.soundwave2k_driver.Soundwave2kDriver")
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.SoundWaveSerialPort')
    @pytest.mark.parametrize('data, state', [(b'5503000058', True),
                                             (b'550300005a', False)])
    def test_reboot(ssp, sd, cfg, data, state):
        ssp.return_value = SSP(data)
        assert  Soundwave2kDriver(cfg_opts, log=_Log()).reboot() == state

    @staticmethod
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch("dtaf_core.drivers.internal.soundwave2k_driver.Soundwave2kDriver")
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.SoundWaveSerialPort')
    @pytest.mark.parametrize('data, state', [(b'550302015b', True),
                                             (b'550300005a', False)])
    def test_ac_power_on(ssp, sd, cfg, data, state):
        ssp.return_value = SSP(data)
        assert  Soundwave2kDriver(cfg_opts, log=_Log()).ac_power_on() == state


    @staticmethod
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch("dtaf_core.drivers.internal.soundwave2k_driver.Soundwave2kDriver")
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.SoundWaveSerialPort')
    @pytest.mark.parametrize('data, state', [(b'550302025c', True),
                                             (b'550300005a', False)])
    def test_ac_power_off(ssp, sd, cfg, data, state):
        ssp.return_value = SSP(data)
        assert  Soundwave2kDriver(cfg_opts, log=_Log()).ac_power_off() == state


    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.Serial', return_value=serial.SerialException("UT"))
    def test_serial_port_open(serMock):
        with mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.SoundWaveSerialPort') as sspMock:
            sspMock.return_value.send.return_value = True
            sspMock.return_value.receive.side_effect = [b"55", b"0302025c"]
            assert Soundwave2kDriver(cfg_normal, log=_Log()).ac_power_off() == True

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.Serial')
    def test_serial_port_send(serMock):
        serMock.return_value.reset_input_buffer.return_value = None
        serMock.return_value.reset_output_buffer.return_value = None
        serMock.return_value.write.side_effect = serial.SerialTimeoutException("UT")
        soudwave_error = False
        try:
            Soundwave2kDriver(cfg_normal, log=_Log()).ac_power_off()
        except SoundWaveError as error:
            print(error)
            soudwave_error = True
        assert soudwave_error

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.Serial')
    def test_serial_port_recv(serMock):
        serMock.return_value.reset_input_buffer.return_value = None
        serMock.return_value.reset_output_buffer.return_value = None
        serMock.return_value.write.return_value = 5
        serMock.return_value.read.side_effect = [
            a2b_hex('55'), a2b_hex('0302025c'), a2b_hex('55')]
        soudwave_error = False
        try:
            with Soundwave2kDriver(cfg_normal, log=_Log()) as d:
                d.ac_power_off()
        except Exception as error:
            print(error)
            soudwave_error = True
        assert not soudwave_error

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.Serial')
    def test_read_exception(serMock):
        serMock.return_value.reset_input_buffer.return_value = None
        serMock.return_value.reset_output_buffer.return_value = None
        serMock.return_value.write.return_value = 5
        serMock.return_value.read.side_effect = serial.SerialException("UT")
        soudwave_error = False
        try:
            with Soundwave2kDriver(cfg_normal, log=_Log()) as d:
                d.ac_power_off()
        except Exception as error:
            print(error)
            soudwave_error = True
        assert soudwave_error

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.SoundWaveSerialPort', side_effect=Exception("UT"))
    def test_open_exception(sspMock):
        soudwave_error = False
        try:
            with Soundwave2kDriver(cfg_normal, log=_Log()) as d:
                d.ac_power_off()
        except AttributeError as error:
            print(error)
            soudwave_error = True
        assert soudwave_error

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.Serial', side_effect=serial.SerialException("UT"))
    def test_open_serial_exception(serMock):
        soudwave_error = False
        serMock.return_value.reset_input_buffer.return_value = None
        serMock.return_value.reset_output_buffer.return_value = None
        serMock.return_value.write.return_value = 5
        try:
            with Soundwave2kDriver(cfg_normal, log=_Log()) as d:
                d.ac_power_off()
        except AttributeError as error:
            print(error)
            soudwave_error = True
        assert soudwave_error

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.SoundWaveSerialPort.receive',
                side_effect=[b"50", b"55", b"0302025c",  b"55"])
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.Serial')
    def test_serial_port_recv(serMock, sspMock):
        serMock.return_value.reset_input_buffer.return_value = None
        serMock.return_value.reset_output_buffer.return_value = None
        serMock.return_value.write.return_value = 5
        with Soundwave2kDriver(cfg_normal, log=_Log()) as d:
            assert d.ac_power_off()

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.SoundWaveSerialPort.receive',
                side_effect=[b"50", b"55", b"0402005b",  b"55"])
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.Serial')
    def test_get_ac_power_state_normal(serMock, sspMock):
        serMock.return_value.reset_input_buffer.return_value = None
        serMock.return_value.reset_output_buffer.return_value = None
        serMock.return_value.write.return_value = 5
        with mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.Soundwave2kDriver.get_voltages', side_effect=[
            [3.0, 3.0, 2.5],
            [0.2, 3.0, 2.5],
            [0.2, 3.0, 0.2],
            [0.2, 0.2, 0.2],
            [0.2, 0.2, 3.0],
            [3.0, 3.0],
            [0.1, 3.0],
            [0.1, 0.2],
            [3.0, 0.1]
        ]) as funcMock:
            # test s3 enabled
            with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
                assert d.get_power_state() == "S0"
            with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
                assert d.get_power_state() == "S3"
            with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
                assert d.get_power_state() == "S5"
            with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
                assert d.get_power_state() == "G3"
            with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
                assert d.get_power_state() == "Unknown"
            # test s3 disabled
            with Soundwave2kDriver(cfg_normal, log=_Log()) as d:
                assert d.get_power_state() == "S0"
            with Soundwave2kDriver(cfg_normal, log=_Log()) as d:
                assert d.get_power_state() == "S5"
            with Soundwave2kDriver(cfg_normal, log=_Log()) as d:
                assert d.get_power_state() == "G3"
            with Soundwave2kDriver(cfg_normal, log=_Log()) as d:
                assert d.get_power_state() == "Unknown"

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.SoundWaveSerialPort.receive',
                side_effect=[
                    b"50",
                    b"55", b"0302025c",
                    b"55", b"0302015b",
                    b"55", b"0402005b",
                    b"55", b"0303025d",
                    b"55", b"0303015c",
                    b"55", b"0403005c"
                ])
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.Serial')
    def test_ac_port_state(serMock, sspMock):
        serMock.return_value.reset_input_buffer.return_value = None
        serMock.return_value.reset_output_buffer.return_value = None
        serMock.return_value.write.return_value = 5
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.ac_power_off()
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.ac_power_on()
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.get_ac_port_state() == 0
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.ac2_power_off()
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.ac2_power_on()
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.get_ac2_port_state() == 0

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.SoundWaveSerialPort.receive',
                side_effect=[
                    b"55", b"0301035c",
                    b"55", b"0301015a",
                    b"55", b"0301025b",
                    b"55", b"0401005a",
                    b"55", b"0" * 10,
                    b"55", b"0" * (264-len(b"55")),
                    b"55", b"0003" + b"0" * (264-len(b"550003")),
                    b"55", b"00032345" + b"0" * (264-len(b"5500032345c0")) + b"c0",
                    b"55", b"0002303335353536" + b"f" * (264-len(b"55000230333535353615"))+b"15"
                ])
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.Serial')
    def test_usb(serMock, sspMock):
        serMock.return_value.reset_input_buffer.return_value = None
        serMock.return_value.reset_output_buffer.return_value = None
        serMock.return_value.write.side_effect = [5, 5, 5, 5, 4, 4, 4, 4, 132]
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.usb_to_open()
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.usb_to_port_a()
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.usb_to_port_b()
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.get_usb_port_state() is not None
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.get_user_messasge() == ""
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.get_user_messasge() == ""
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.get_user_messasge() == ""
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.get_user_messasge()[0:2] == "#E"
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.set_user_messasge("035556")

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.SoundWaveSerialPort.receive',
                side_effect=[
                    b"55", b"050100000000005b",
                    b"55", b"050101000000005c",
                    b"55", b"050f01000000006a",
                    b"55", b"050f000000000069",
                    b"55", b"000459",
                    b"55", b"00055a",
                    b"55", b"00010000000056",
                    b"55", b"00000000000055"
                ])
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.Serial')
    def test_misc(serMock, sspMock):
        serMock.return_value.reset_input_buffer.return_value = None
        serMock.return_value.reset_output_buffer.return_value = None
        serMock.return_value.write.side_effect = [
            len(b"55050100000000005b")/2,
            len(b"55050101000000005c")/2,
            len(b"55050f01000000006a")/2,
            len(b"55050f01000000006a")/2,
            len(b"55000459")/2,
            len(b"5500055a")/2,
            len(b"55000156")/2,
            len(b"55000055")/2
        ]
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.get_ad_hw_version() == b'00.00.00.00'
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.get_ad_sw_version() == b'00.00.00.00'
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.get_fp_sw_version() == b'00.00.00.00'
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.get_fp_hw_version() == b'00.00.00.00'
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.enable_live_debug()
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.disable_live_debug()
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.get_sw_version()
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.get_hw_version()

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.SoundWaveSerialPort.receive',
                side_effect=[
                    b"55", b"070f10017c",
                    b"55", b"070f0d0179",
                    b"55", b"070f0f017b",
                    b"55", b"070f0e017a",
                    b"55", b"070f10007b",
                    b"55", b"070f0f007a",
                    b"55", b"070f0d0078",
                    b"55", b"070f0e0079"
                ])
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.Serial')
    def test_button(serMock, sspMock):
        serMock.return_value.reset_input_buffer.return_value = None
        serMock.return_value.reset_output_buffer.return_value = None
        serMock.return_value.write.side_effect = [
            len(b"55070f10017c")/2,
            len(b"55070f0d0179")/2,
            len(b"55070f0f017b")/2,
            len(b"55070f0e017a")/2,
            len(b"55070f10007b")/2,
            len(b"55070f0f007a")/2,
            len(b"55070f0d0078")/2,
            len(b"55070f0e0079")/2,
        ]
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.press_nmi_button()
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.press_power_button()
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.press_reset_button()
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.press_system_id_button()
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.release_nmi_button()
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.release_reset_button()
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.release_power_button()
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.release_system_id_button()

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.SoundWaveSerialPort.receive',
                side_effect=[
                    b"55", b"0701010203040500000000006c",
                    b"55", b"070f02006d",
                    b"55", b"080f01006d"
                ])
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.Serial')
    def test_cmd(serMock, sspMock):
        serMock.return_value.reset_input_buffer.return_value = None
        serMock.return_value.reset_output_buffer.return_value = None
        serMock.return_value.write.side_effect = [
            len(b"550701010203040500000000006c")/2,
            len(b"55070f02006d")/2,
            len(b"55080f01006d")/2,
        ]
        has_exception = False
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            try:
                d.get_ad_values([])
            except InvalidParameterError as ex:
                print(ex)
                has_exception = True
            assert has_exception
            has_exception = False
            try:
                d.get_ad_values([1,2,3,4,5])
            except InvalidParameterError as ex:
                print(ex)
                has_exception = True
            assert not has_exception
            has_exception = False
            try:
                d.ctr_fp_two_ways_switch(fp_port=0, action=0)
            except InputError as ex:
                print(ex)
                has_exception = True
            assert has_exception
            has_exception = False
            try:
                d.ctr_fp_two_ways_switch(fp_port=0, action=10)
            except InputError as ex:
                print(ex)
                has_exception = True
            assert has_exception
            has_exception = False
            assert d.ctr_fp_two_ways_switch(fp_port=2, action=0)
            has_exception = False
            try:
                d.ctr_fp_two_ways_switch(fp_port=0, action=10)
            except InputError as ex:
                print(ex)
                has_exception = True
            assert has_exception
            has_exception = False
            try:
                assert d.get_fp_switch_state(fp_port=0)
            except InvalidParameterError as ex:
                print(ex)
                has_exception = True
            assert has_exception
            has_exception = False
            assert d.get_fp_switch_state(fp_port=1)

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.soundwave2k_driver.Soundwave2kDriver.get_ad_values', return_value=[1, 1, 1])
    def test_voltages(funcMock):
        with Soundwave2kDriver(cfg_normal_s3, log=_Log()) as d:
            assert d.get_voltages([
                'SLPMemory', 'SLPP3V3', 'SLPDSW'])













