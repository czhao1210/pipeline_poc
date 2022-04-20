from collections import OrderedDict

from dtaf_core.lib.private.providercfg_factory import ProviderCfgFactory

ASSUME = True

from dtaf_core.lib.private.provider_config.dc_provider_config import DcProviderConfig

import time
from xml.etree import ElementTree as ET


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


cfgs = [
    ET.fromstring("""
<dc>
    <driver>
        <soundwave2k enable_s3_detect="False">
            <baudrate>115200</baudrate>
            <serial type="1"></serial>
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
"""),
    ET.fromstring("""
<dc>
    <driver>
        <soundwave2k enable_s3_detect="False">
            <baudrate>115200</baudrate>
            <serial type="1"></serial>
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
        <power_off>20</power_off>
    </timeout>
</dc>
"""),
    ET.fromstring("""
<dc>
    <driver>
        <soundwave2k enable_s3_detect="False">
            <baudrate>115200</baudrate>
            <serial type="1"></serial>
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
    </timeout>
</dc>
""")
]


class TestSuites:
    def test_cfg_normal(self):
        for cfg in cfgs:
            try:
                cfg_model = ProviderCfgFactory.create(cfg, Logs())
                driver_cfg = cfg_model.driver_cfg
                assert cfg_model.poweron_timeout
                assert cfg_model.poweroff_timeout
                assert cfg_model.power_off_button_down
            except KeyError:
                pass
