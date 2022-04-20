import six

from dtaf_core.drivers.internal.rsc2_driver import RscDriverException
from dtaf_core.lib.exceptions import DriverIOError

ASSUME = True

from dtaf_core.lib.dtaf_constants import PowerState

if six.PY2:
    import mock

if six.PY3 or six.PY34:
    from unittest import mock

import time
from dtaf_core.providers.provider_factory import ProviderFactory
from dtaf_core.providers.dc_power import DcPowerControlProvider
from xml.etree import ElementTree as ET


class DF:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        pass

    def ac_power_on(self):
        return True

    def ac2_power_on(self):
        return True

    def ac_power_off(self):
        return True

    def ac2_power_off(self):
        return True

    def get_power_state(self):
        return 'On'

    def get_voltages(self, lists=[]):
        return lists

    def close(self):
        pass


class Logs:
    def debug(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


def power_on_states_timeout():
    time.sleep(10)
    return r'On'


def power_off_states_timeout():
    time.sleep(10)
    return r'Off'


cfg_dict = dict(
    normal=[
        # soundwave2k
        ET.fromstring(
            """
            <dc>
                <driver>
                    <soundwave2k enable_s3_detect="False">
                        <baudrate>115200</baudrate>
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
                </driver>
                <timeout>
                    <power_on>5</power_on>
                    <power_off>20</power_off>
                </timeout>
            </dc>
            """
        ),
        # pdupi
        ET.fromstring(
            """
            <dc>
               <driver>
                    <pdupi>
                        <ip>10.190.155.147</ip>
                        <port>80</port>
                        <proxy>http://child-prc.intel.com:913</proxy>
                        <channel>ch1</channel>
                        <username>admin</username>
                        <password>intel@123</password>
                        <masterkey>smartrpipdu</masterkey>
                    </pdupi>
                </driver>
                <timeout>
                    <power_on>6</power_on>
                    <power_off>6</power_off>
                </timeout>
            </dc>
            """
        ),
        # pi
        ET.fromstring(
            """
            <dc>
               <driver>
                    <pi>
                        <ip>10.190.155.174</ip>
                        <port>80</port>
                        <proxy>http://child-prc.intel.com:913</proxy>
                    </pi>
                </driver>
                <timeout>
                    <power_on>5</power_on>
                    <power_off>5</power_off>
                </timeout>
            </dc>
            """
        ),
        # rsc2
        ET.fromstring(
            """
            <dc>
                <driver>
                    <rsc2>
                    </rsc2>
                </driver>
                <timeout>
                    <power_on>5</power_on>
                    <power_off>20</power_off>
                </timeout>
            </dc>
            """
        ),
        # banino
        ET.fromstring(
            """
            <dc>
                <timeout>
                    <power_on>5</power_on>
                    <power_off>20</power_off>
                </timeout>
               <driver>
                   <banino>
							<banino_dll_path>r"C:\\banino\code\Banino_SXState\\x64\ladybird.dll"</banino_dll_path>
							<banino_power_cmd>"C:\\banino\code\Banino_SXState"</banino_power_cmd>
							<ladybird_driver_serial>152903681</ladybird_driver_serial>
                            <image_path>C:\IFWI_Image\</image_path>
							<image_name>egs.bin</image_name>
							<rasp>xxx</rasp>
                        </banino>
                </driver>
            </dc>
            """
        )
    ]
)


class TestDcProvider:

    # dc power on success
    def test_rsc2_dc_power_on_success(self):
        self.__test_dc_power_on_success("rsc2")

    def test_pi_dc_power_on_success(self):
        self.__test_dc_power_on_success("pi")

    def test_pdupi_dc_power_on_success(self):
        self.__test_dc_power_on_success("pdupi")

    def test_soundwave2k_dc_power_on_success(self):
        self.__test_dc_power_on_success("soundwave2k")

    def test_banino_dc_power_on_success(self):
        self.__test_dc_power_on_success("banino")

    def __test_dc_power_on_success(self, driver_name):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if driver_name == tag:
                patch_obj = r"dtaf_core.providers.internal.{}_dc_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    if "rsc2" == tag:
                        m.return_value.read_power_led.side_effect = [False, False, True, True]
                    elif "soundwave2k" == tag:
                        m.return_value.__enter__.return_value.press_power_button.return_value = True
                        m.return_value.__enter__.return_value.release_power_button.return_value = True
                        m.return_value.__enter__.return_value.get_power_state.side_effect = [
                            PowerState.S5, PowerState.S5, PowerState.S0, PowerState.S0]
                    else:
                        m.return_value.__enter__.return_value.dc_power_on.return_value = True
                    dc = ProviderFactory.create(cfg, Logs())  # type: DcPowerControlProvider
                    print('tag={} test...'.format(tag))
                    assert dc.dc_power_on() is True

    # dc power on fail
    def test_rsc2_dc_power_on_fail(self):
        self.__test_dc_power_on_fail("rsc2")

    def test_pi_dc_power_on_fail(self):
        self.__test_dc_power_on_fail("pi")

    def test_pdupi_dc_power_on_fail(self):
        self.__test_dc_power_on_fail("pdupi")

    def test_soundwave2k_dc_power_on_fail(self):
        self.__test_dc_power_on_fail("soundwave2k")

    def test_banino_dc_power_on_fail(self):
        self.__test_dc_power_on_fail("banino")

    def __test_dc_power_on_fail(self, driver_name):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == driver_name:
                patch_obj = r"dtaf_core.providers.internal.{}_dc_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    loop = 1
                    if "rsc2" == tag:
                        m.return_value.read_power_led.return_value = False
                    elif "soundwave2k" == tag:
                        m.return_value.__enter__.return_value.press_power_button.return_value = True
                        m.return_value.__enter__.return_value.release_power_button.return_value = True
                        m.return_value.__enter__.return_value.get_power_state.return_value = PowerState.S5
                    else:
                        m.return_value.__enter__.return_value.dc_power_on.return_value = False
                    dc = ProviderFactory.create(cfg, Logs())  # type: DcPowerControlProvider
                    print('tag={} test...'.format(tag))
                    for i in range(0, loop):
                        print('tag={} test {}...'.format(tag, i))
                        assert dc.dc_power_on() is False

    # test dc power on exception
    def test_rsc2_dc_power_on_exception(self):
        self.__test_dc_power_on_exception("rsc2")

    def test_pi_dc_power_on_exception(self):
        self.__test_dc_power_on_exception("pi")

    def test_pdupi_dc_power_on_exception(self):
        self.__test_dc_power_on_exception("pdupi")

    def test_soundwave2k_dc_power_on_exception(self):
        self.__test_dc_power_on_exception("soundwave2k")

    def test_banino_dc_power_on_exception(self):
        self.__test_dc_power_on_exception("banino")

    def __test_dc_power_on_exception(self, driver_name):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == driver_name:
                patch_obj = r"dtaf_core.providers.internal.{}_dc_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    if "rsc2" == tag:
                        m.return_value.read_power_led.side_effect = [False, False, True, True]
                        m.return_value.press_power_button.side_effect = RscDriverException("UT")
                    elif "soundwave2k" == tag:
                        m.return_value.__enter__.return_value.press_power_button.side_effect = [False, True, True]
                        m.return_value.__enter__.return_value.release_power_button.side_effect = [False,
                                                                                                  Exception("UT")]
                        m.return_value.__enter__.return_value.get_power_state.return_value = PowerState.S5
                        loop = 3
                    elif "banino" == tag:
                        m.return_value.__enter__.return_value.dc_power_on.side_effect = DriverIOError("UT")
                    else:
                        m.return_value.__enter__.return_value.dc_power_on.side_effect = Exception("UT")
                    with ProviderFactory.create(cfg, Logs()) as dc:  # type: DcPowerControlProvider
                        loop = 1
                        print('tag={} test...'.format(tag))
                        for i in range(0, loop):
                            print('tag={} test {}...'.format(tag, i))
                            try:
                                has_exception = False
                                assert dc.dc_power_on() is None
                            except DriverIOError as err:
                                has_exception = True
                            except Exception as ex:
                                assert isinstance(ex, DriverIOError), "Unexpected Exception Type Caught:{}".format(
                                    type(ex))
                            assert has_exception

    # dc power off success
    def test_rsc2_dc_power_off_success(self):
        self.__test_dc_power_off_success("rsc2")

    def test_pi_dc_power_off_success(self):
        self.__test_dc_power_off_success("pi")

    def test_pdupi_dc_power_off_success(self):
        self.__test_dc_power_off_success("pdupi")

    def test_soundwave2k_dc_power_off_success(self):
        self.__test_dc_power_off_success("soundwave2k")

    def test_banino_dc_power_off_success(self):
        self.__test_dc_power_off_success("banino")

    def __test_dc_power_off_success(self, driver_name):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if driver_name == tag:
                patch_obj = r"dtaf_core.providers.internal.{}_dc_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    if "rsc2" == tag:
                        m.return_value.read_power_led.side_effect = [True, True, False, False]
                    elif "soundwave2k" == tag:
                        m.return_value.__enter__.return_value.press_power_button.return_value = True
                        m.return_value.__enter__.return_value.release_power_button.return_value = True
                        m.return_value.__enter__.return_value.get_power_state.side_effect = [
                            PowerState.S0, PowerState.S0, PowerState.S5, PowerState.S5]
                    elif "banino" == tag:
                        m.return_value.__enter__.return_value.dc_power_off.return_value = True
                    else:
                        m.return_value.__enter__.return_value.dc_power_on.return_value = True
                    with ProviderFactory.create(cfg, Logs()) as dc:  # type: DcPowerControlProvider
                        print('tag={} test...'.format(tag))
                        assert dc.dc_power_off() is True

    # dc power off fail
    def test_rsc2_dc_power_off_fail(self):
        self.__test_dc_power_off_fail("rsc2")

    def test_pi_dc_power_off_fail(self):
        self.__test_dc_power_off_fail("pi")

    def test_pdupi_dc_power_off_fail(self):
        self.__test_dc_power_off_fail("pdupi")

    def test_soundwave2k_dc_power_off_fail(self):
        self.__test_dc_power_off_fail("soundwave2k")

    def test_banino_dc_power_off_fail(self):
        self.__test_dc_power_off_fail("banino")

    def __test_dc_power_off_fail(self, driver_name):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if driver_name == tag:
                patch_obj = r"dtaf_core.providers.internal.{}_dc_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    if "rsc2" == tag:
                        m.return_value.read_power_led.return_value = True
                    elif "soundwave2k" == tag:
                        m.return_value.__enter__.return_value.press_power_button.return_value = True
                        m.return_value.__enter__.return_value.release_power_button.return_value = True
                        m.return_value.__enter__.return_value.get_power_state.return_value = PowerState.S0
                    elif "banino" == tag:
                        m.return_value.__enter__.return_value.dc_power_off.return_value = False
                    else:
                        m.return_value.__enter__.return_value.dc_power_off.return_value = False
                    with ProviderFactory.create(cfg, Logs()) as dc:  # type: DcPowerControlProvider
                        print('tag={} test...'.format(tag))
                        assert dc.dc_power_off() is False

    # dc power off exception
    def test_rsc2_dc_power_off_exception(self):
        self.__test_dc_power_off_exception("rsc2")

    def test_pi_dc_power_off_exception(self):
        self.__test_dc_power_off_exception("pi")

    def test_pdupi_dc_power_off_exception(self):
        self.__test_dc_power_off_exception("pdupi")

    def test_soundwave2k_dc_power_off_exception(self):
        self.__test_dc_power_off_exception("soundwave2k")

    def test_banino_dc_power_off_exception(self):
        self.__test_dc_power_off_exception("banino")

    def __test_dc_power_off_exception(self, driver_name):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == driver_name:
                patch_obj = r"dtaf_core.providers.internal.{}_dc_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    if "rsc2" == tag:
                        m.return_value.read_power_led.side_effect = [True, True, False, False]
                        m.return_value.press_power_button.side_effect = RscDriverException("UT")
                    elif "soundwave2k" == tag:
                        m.return_value.__enter__.return_value.press_power_button.side_effect = [False, True, True]
                        m.return_value.__enter__.return_value.release_power_button.side_effect = [False,
                                                                                                  Exception("UT")]
                        m.return_value.__enter__.return_value.get_power_state.return_value = PowerState.S5
                        loop = 3
                    elif 'banino' == tag:
                        m.return_value.__enter__.return_value.dc_power_off.side_effect = DriverIOError("UT")
                    else:
                        m.return_value.__enter__.return_value.dc_power_off.side_effect = Exception("UT")
                    with ProviderFactory.create(cfg, Logs()) as dc:  # type: DcPowerControlProvider
                        loop = 1
                        print('tag={} test...'.format(tag))
                        for i in range(0, loop):
                            print('tag={} test {}...'.format(tag, i))
                            try:
                                has_exception = False
                                assert dc.dc_power_off() is None
                            except DriverIOError as err:
                                has_exception = True
                            except Exception as ex:
                                assert isinstance(ex, DriverIOError), "Unexpected Exception Type Caught:{}".format(
                                    type(ex))
                            assert has_exception
