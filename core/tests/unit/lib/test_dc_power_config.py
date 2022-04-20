import xmltodict

from dtaf_core.lib.private.dc_power_config import DcPowerConfig

cfg = xmltodict.parse("""
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
""")


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


class TestSuites:
    @staticmethod
    def test_init():
        obj = DcPowerConfig(cfg, _Log())
        assert obj.poweron_timeout == None
        assert obj.poweroff_timeout == None
