import builtins
from subprocess import CalledProcessError

import six
from dtaf_core.lib.exceptions import DriverIOError, SoundWaveError

ASSUME = True

from dtaf_core.lib.dtaf_constants import PowerState

if six.PY2:
    import mock

if six.PY3 or six.PY34:
    from unittest import mock

import time
from dtaf_core.providers.provider_factory import ProviderFactory
from dtaf_core.providers.ac_power import AcPowerControlProvider
from xml.etree import ElementTree as ET
import pytest

cfg_dict = dict(
    normal=[
        # soundwave2k
        ET.fromstring(
            """
            <ac>
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
            </ac>
            """
        ),
        # pdupi
        ET.fromstring(
            """
            <ac>
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
            </ac>
            """
        ),
        # pi
        ET.fromstring(
            """
            <ac>
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
            </ac>
            """
        ),
        # rsc2
        ET.fromstring(
            """
            <ac>
                <driver>
                    <rsc2>
                    </rsc2>
                </driver>
                <timeout>
                    <power_on>5</power_on>
                    <power_off>20</power_off>
                </timeout>
            </ac>
            """
        ),
        # pdu
        ET.fromstring(
            """
            <ac>
                <timeout>
                    <power_on>5</power_on>
                    <power_off>20</power_off>
                </timeout>
               <driver>
                   <pdu brand="raritan" model="px-5052R">
                        <ip>10.239.129.19</ip>
                        <port>22</port>
                        <username>admin</username>
                        <password>intel@123</password>
                        <timeout>5</timeout>
                        <outlets>
                            <outlet>1</outlet>
                            <outlet>2</outlet>
                        </outlets>
                   </pdu>
                </driver>
            </ac>
            """
        ),
        # simics
        ET.fromstring(
            """
            <ac>
                <timeout>
                    <power_on>5</power_on>
                    <power_off>20</power_off>
                </timeout>
               <driver>
                    <simics>
                        <serial_port>2122</serial_port>
                        <host>
                            <name>10.148.204.64</name>
                            <port>22</port>
                            <username>uuuuu</username>
                            <password>xxxxx</password>
                        </host>
                        <service_port>2121</service_port>
                        <app>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww26.2/simics</app>
                        <project>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww26.2</project>
                        <script>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww26.2/targets/birchstream/birchstream-ap.simics</script>
                    </simics>
                </driver>
            </ac>
            """
        )
    ]
)


class TestAcProvider:
    # power on success
    def __test_power_on_success(self, cfg):
        with ProviderFactory.create(cfg, mock.MagicMock()) as ac:  # type: AcPowerControlProvider
            assert ac.ac_power_on()

    @pytest.mark.parametrize('is_running, execute_value',
                             [(True, "AC_PRESENT state : 1"), (False, "AC_PRESENT state : 1")])
    def test_simics_ac_power_on_success(self, is_running, execute_value):
        tag = r"simics"
        patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
        for cfg in cfg_dict["normal"]:
            if tag == cfg.find("driver/*").tag:
                with mock.patch(patch_obj) as m:
                    m.return_value.register.return_value = None
                    m.return_value.is_simics_running.return_value = is_running
                    m.return_value.start.return_value = None
                    m.return_value.launch_simics.return_value = True
                    m.return_value.SimicsChannel.execute_until.return_value = execute_value
                    self.__test_power_on_success(cfg)

    def test_rsc2_ac_power_on_success(self):
        tag = r"rsc2"
        patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
        for cfg in cfg_dict["normal"]:
            if tag == cfg.find("driver/*").tag:
                with mock.patch(patch_obj) as m:
                    m.return_value.ac_connected.return_value = True
                    self.__test_power_on_success(cfg)

    def test_pi_ac_power_on_success(self):
        tag = r"pi"
        patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
        for cfg in cfg_dict["normal"]:
            if tag == cfg.find("driver/*").tag:
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.ac_power_on.return_value = True
                    self.__test_power_on_success(cfg)

    def test_pdupi_ac_power_on_success(self):
        tag = r"pdupi"
        patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
        for cfg in cfg_dict["normal"]:
            if tag == cfg.find("driver/*").tag:
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.ac_power_on.return_value = True
                    self.__test_power_on_success(cfg)

    def test_soundwave2k_ac_power_on_success(self):
        tag = r"soundwave2k"
        patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
        for cfg in cfg_dict["normal"]:
            if tag == cfg.find("driver/*").tag:
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.ac_power_on.return_value = True
                    m.return_value.__enter__.return_value.ac2_power_on.return_value = True
                    m.return_value.__enter__.return_value.get_power_state.side_effect = [PowerState.G3, PowerState.G3,
                                                                                         PowerState.G3, PowerState.G3,
                                                                                         PowerState.S0, PowerState.S0,
                                                                                         PowerState.S0, PowerState.S0]
                    self.__test_power_on_success(cfg)

    def test_pdu_ac_power_on_success(self):
        tag = r"pdu"
        patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
        for cfg in cfg_dict["normal"]:
            if tag == cfg.find("driver/*").tag:
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.ac_power_on.return_value = True
                    self.__test_power_on_success(cfg)

    # power on fail
    def __test_ac_power_on_fail(self, cfg):
        with ProviderFactory.create(cfg_opts=cfg, logger=mock.MagicMock()) as ac:  # type: AcPowerControlProvider
            assert not ac.ac_power_on(timeout=3)

    def test_simics_ac_power_on_fail(self):
        tag = r"simics"
        patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
        for cfg in cfg_dict["normal"]:
            if tag == cfg.find("driver/*").tag:
                with mock.patch(patch_obj) as m:
                    m.return_value.register.return_value = None
                    m.return_value.is_simics_running.return_value = False
                    m.return_value.start.return_value = None
                    m.return_value.launch_simics.return_value = False
                    m.return_value.SimicsChannel.execute_until.return_value = "AC_PRESENT state : 0"
                    self.__test_ac_power_on_fail(cfg)

    def test_rsc2_ac_power_on_fail(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "rsc2":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.ac_connected.return_value = False
                    m.return_value.ac_power_on.return_value = False
                    self.__test_ac_power_on_fail(cfg)

    def test_pi_ac_power_on_fail(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pi":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.ac_power_on.return_value = False
                    self.__test_ac_power_on_fail(cfg)

    def test_pdupi_ac_power_on_fail(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pdupi":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.ac_power_on.return_value = False
                    self.__test_ac_power_on_fail(cfg)

    def test_soundwave2k_ac_power_on_fail(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "soundwave2k":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    # mock.patch(r"dtaf_core.providers.internal.{}_ac_provider.sleep".format(tag))
                    m.return_value.__enter__.return_value.ac_power_on.return_value = True
                    m.return_value.__enter__.return_value.ac2_power_on.return_value = True
                    m.return_value.__enter__.return_value.get_power_state.return_value = PowerState.G3
                    self.__test_ac_power_on_fail(cfg)

    def test_pdu_ac_power_on_fail(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pdu":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.ac_power_on.return_value = False
                    self.__test_ac_power_on_fail(cfg)

    # test exxception
    def __test_ac_power_on_exception(self, cfg):
        with ProviderFactory.create(cfg_opts=cfg, logger=mock.MagicMock()) as ac:  # type: AcPowerControlProvider
            # expected result: fail or rais Exception
            try:
                ac.ac_power_on(timeout=10)
                assert False, "an exception is expected."
            except Exception as ex:
                print(ex)

    @pytest.mark.parametrize('ret_register, ret_running, ret_start, ret_launch',
                             [(Exception("UT"), False, None, True),
                              (None, Exception("UT"), None, True),
                              (None, False, Exception("UT"), True),
                              (None, False, None, Exception("UT"))])
    def test_simics_ac_power_on_exception(self, ret_register, ret_running, ret_start, ret_launch):
        tag = r"simics"
        patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
        for cfg in cfg_dict["normal"]:
            if tag == cfg.find("driver/*").tag:
                with mock.patch(patch_obj) as m:
                    m.return_value.register.return_value = ret_register
                    m.return_value.is_simics_running.return_value = ret_running
                    m.return_value.start.return_value = ret_start
                    m.return_value.launch_simics.return_value = ret_launch
                    self.__test_ac_power_on_exception(cfg)

    def test_rsc2_ac_power_on_exception(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "rsc2":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.connect_power.side_effect = Exception("UT")
                    m.return_value.ac_connected.return_value = False
                    self.__test_ac_power_on_exception(cfg)

    def test_pi_ac_power_on_exception(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pi":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.ac_power_on.return_value = Exception("UT")
                    self.__test_ac_power_on_exception(cfg)

    def test_pdupi_ac_power_on_exception(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pdupi":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.ac_power_on.return_value = Exception("UT")
                    self.__test_ac_power_on_exception(cfg)

    def test_soundwave2k_ac_power_on_exception(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pdupi":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.ac_power_on.return_value = Exception("UT")
                    self.__test_ac_power_on_exception(cfg)

    def test_pdu_ac_power_on_exception(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pdupi":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.ac_power_on.return_value = Exception("UT")
                    self.__test_ac_power_on_exception(cfg)

    # test power off success
    def __test_ac_power_off_success(self, cfg):
        with ProviderFactory.create(cfg_opts=cfg, logger=mock.MagicMock()) as ac:  # type: AcPowerControlProvider
            # expected result: fail or rais Exception
            assert ac.ac_power_off(timeout=3)

    @pytest.mark.parametrize('ret_running, ret_shutdown, ret_stop, ret_unregister',
                             [(False, None, None, None),
                              (True, True, None, None)])
    def test_simics_ac_power_off_success(self, ret_running, ret_shutdown, ret_stop, ret_unregister):
        tag = r"simics"
        patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
        for cfg in cfg_dict["normal"]:
            if tag == cfg.find("driver/*").tag:
                with mock.patch(patch_obj) as m:
                    m.return_value.is_simics_running.return_value = ret_running
                    m.return_value.shutdown_simics.return_value = ret_shutdown
                    m.return_value.stop.return_value = ret_stop
                    m.return_value.unregister.return_value = ret_unregister
                    self.__test_ac_power_off_success(cfg)

    def test_rsc2_ac_power_off_success(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "rsc2":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.ac_connected.return_value = False
                    self.__test_ac_power_off_success(cfg)

    def test_pi_ac_power_off_success(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pi":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.ac_power_off.return_value = True
                    self.__test_ac_power_off_success(cfg)

    def test_pdupi_ac_power_off_success(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pdupi":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.ac_power_off.return_value = True
                    self.__test_ac_power_off_success(cfg)

    def test_soundwave2k_ac_power_off_success(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "soundwave2k":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.ac_power_off.return_value = True
                    m.return_value.__enter__.return_value.ac2_power_off.return_value = True
                    m.return_value.__enter__.return_value.get_power_state.side_effect = [
                        PowerState.S0, PowerState.S0,
                        PowerState.G3, PowerState.G3,
                        PowerState.G3, PowerState.G3
                    ]
                    self.__test_ac_power_off_success(cfg)

    def test_pdu_ac_power_off_success(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pdu":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.ac_power_off.return_value = True
                    self.__test_ac_power_off_success(cfg)

    # ac off fail
    def __test_ac_power_off_fail(self, cfg):
        with ProviderFactory.create(cfg_opts=cfg, logger=mock.MagicMock()) as ac:  # type: AcPowerControlProvider
            # expected result: fail or rais Exception
            ret = ac.ac_power_off(timeout=3)
            assert not ret, "expected value: False, actual: {}".format(ret)

    def test_simics_ac_power_off_fail(self):
        tag = r"simics"
        patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
        for cfg in cfg_dict["normal"]:
            if tag == cfg.find("driver/*").tag:
                with mock.patch(patch_obj) as m:
                    m.return_value.is_simics_running.return_value = True
                    m.return_value.shutdown_simics.return_value = False
                    m.return_value.stop.return_value = None
                    m.return_value.unregister.return_value = None
                    self.__test_ac_power_off_fail(cfg)

    def test_rsc2_ac_power_off_fail(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "rsc2":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.ac_connected.return_value = True
                    self.__test_ac_power_off_fail(cfg)

    def test_pi_ac_power_off_fail(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pi":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.ac_power_off.return_value = False
                    self.__test_ac_power_off_fail(cfg)

    def test_pdupi_ac_power_off_fail(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pdupi":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.ac_power_off.return_value = False
                    self.__test_ac_power_off_fail(cfg)

    def test_soundwave2k_ac_power_off_fail(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "soundwave2k":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.ac_power_off.return_value = True
                    m.return_value.__enter__.return_value.ac2_power_off.return_value = True
                    m.return_value.__enter__.return_value.get_power_state.return_value = PowerState.S0
                    self.__test_ac_power_off_fail(cfg)

    def test_pdu_ac_power_off_fail(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pdu":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.ac_power_off.return_value = False
                    self.__test_ac_power_off_fail(cfg)

    # ac off exception
    @pytest.mark.parametrize('ret_running, ret_shutdown, ret_stop, ret_unregister',
                             [(Exception("UT"), True, None, None),
                              (True, Exception("UT"), None, None),
                              (True, True, Exception("UT"), None),
                              (True, True, None, Exception("UT"))])
    def test_simics_ac_power_off_exception(self, ret_running, ret_shutdown, ret_stop, ret_unregister):
        tag = r"simics"
        patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
        for cfg in cfg_dict["normal"]:
            if tag == cfg.find("driver/*").tag:
                with mock.patch(patch_obj) as m:
                    m.return_value.is_simics_running.return_value = ret_running
                    m.return_value.shutdown_simics.return_value = ret_shutdown
                    m.return_value.stop.return_value = ret_stop
                    m.return_value.unregister.return_value = ret_unregister
                    self.__test_ac_power_off_exception(cfg)

    def test_rsc2_power_off_exception(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "rsc2":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.connect_power.return_value = Exception("UT")
                    m.return_value.ac_connected.return_value = True
                    self.__test_ac_power_off_exception(cfg)

    def test_pi_power_off_exception(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pi":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.connect_power.return_value = Exception("UT")
                    m.return_value.ac_connected.return_value = True
                    self.__test_ac_power_off_exception(cfg)

    def test_soundwave2k_power_off_exception(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "soundwave2k":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.ac_power_on.return_value = Exception("UT")
                    self.__test_ac_power_off_exception(cfg)

    def test_pdu_power_off_exception(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pdu":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.ac_power_on.return_value = Exception("UT")
                    self.__test_ac_power_off_exception(cfg)

    def test_pdupi_power_off_exception(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pdupi":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.ac_power_on.return_value = Exception("UT")
                    self.__test_ac_power_off_exception(cfg)

    def __test_ac_power_off_exception(self, cfg):
        with ProviderFactory.create(cfg_opts=cfg, logger=mock.MagicMock()) as ac:  # type: AcPowerControlProvider
            try:
                ac.ac_power_off(timeout=3)
                assert False, "an exception is expected"
            except Exception as ex:
                pass

    # get ac power state success
    @pytest.mark.parametrize('ret_state, expected',
                             [(True, True),
                              (False, False)])
    def test_rsc2_get_ac_power_state_success(self, ret_state, expected):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "rsc2":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.ac_connected.return_value = ret_state
                    self.__test_get_ac_power_state_success(cfg, expected=expected)

    @pytest.mark.parametrize('ret_state, expected',
                             [(True, True),
                              (False, False)])
    def test_simics_get_ac_power_state_success(self, ret_state, expected):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "simics":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.is_simics_running.return_value = ret_state
                    self.__test_get_ac_power_state_success(cfg, expected=expected)

    @pytest.mark.parametrize('ret_state, expected',
                             [(True, True),
                              (False, False)])
    def test_pi_get_ac_power_state_success(self, ret_state, expected):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pi":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.get_ac_power_state.return_value = ret_state
                    self.__test_get_ac_power_state_success(cfg, expected=expected)

    @pytest.mark.parametrize('ret_state, expected',
                             [(True, True),
                              (False, False)])
    def test_pdupi_get_ac_power_state_success(self, ret_state, expected):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pdupi":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.get_ac_power_state.return_value = ret_state
                    self.__test_get_ac_power_state_success(cfg, expected=expected)

    @pytest.mark.parametrize('ret_state, expected',
                             [(PowerState.S0, True),
                              (PowerState.S3, True),
                              (PowerState.S4, True),
                              (PowerState.S5, True),
                              (PowerState.G3, False)])
    def test_soundwave2k_get_ac_power_state_success(self, ret_state, expected):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "soundwave2k":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.get_power_state.return_value = ret_state
                    self.__test_get_ac_power_state_success(cfg, expected=expected)

    @pytest.mark.parametrize('ret_state, expected',
                             [(True, True),
                              (False, False)])
    def test_pdu_get_ac_power_state_success(self, ret_state, expected):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pdu":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.__enter__.return_value.get_ac_power_state.return_value = ret_state
                    self.__test_get_ac_power_state_success(cfg, expected=expected)

    def __test_get_ac_power_state_success(self, cfg, expected):
        with ProviderFactory.create(cfg_opts=cfg, logger=mock.MagicMock()) as ac:  # type: AcPowerControlProvider
            assert expected == ac.get_ac_power_state()

    # get ac power state exception
    def test_simics_get_ac_power_state_success(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "simics":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.is_simics_running.return_value = Exception("UT")
                    self.__test_get_ac_power_state_exception(cfg)

    def test_rsc2_get_ac_power_state_exception(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "rsc2":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.ac_connected.return_value = Exception("UT")
                    self.__test_get_ac_power_state_exception(cfg)

    def test_pi_get_ac_power_state_exception(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pi":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.get_ac_power_state.return_value = Exception("UT")
                    self.__test_get_ac_power_state_exception(cfg)

    def test_pdupi_get_ac_power_state_exception(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pdupi":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.get_ac_power_state.return_value = Exception("UT")
                    self.__test_get_ac_power_state_exception(cfg)

    def test_pdu_get_ac_power_state_exception(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "pdu":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.get_ac_power_state.return_value = Exception("UT")
                    self.__test_get_ac_power_state_exception(cfg)

    def test_soundwave2k_get_ac_power_state_exception(self):
        for cfg in cfg_dict["normal"]:
            tag = cfg.find("driver/*").tag
            if tag == "soundwave2k":
                patch_obj = r"dtaf_core.providers.internal.{}_ac_provider.DriverFactory.create".format(tag)
                with mock.patch(patch_obj) as m:
                    m.return_value.get_ac_power_state.return_value = Exception("UT")
                    self.__test_get_ac_power_state_exception(cfg)

    def __test_get_ac_power_state_exception(self, cfg):
        with ProviderFactory.create(cfg_opts=cfg, logger=mock.MagicMock()) as ac:  # type: AcPowerControlProvider
            try:
                ac.get_ac_power_state()
                assert False, "an exception is expected"
            except Exception as ex:
                pass
