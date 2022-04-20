import xmltodict

from dtaf_core.lib.private.ac_power_config import AcPowerConfig

cfg = xmltodict.parse("""
<ac>
 <driver>
        <pi>
            <ip>1.1.1.1</ip>
            <port>80</port>
            <proxy>http://child-prc.intel.com:913</proxy>
        </pi>    
   </driver>
   <timeout>
        <power_on>5</power_on>
        <power_off>10</power_off>
   </timeout>
</ac>
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
        obj = AcPowerConfig(cfg, _Log())
        assert obj.poweron_timeout == None
        assert obj.poweroff_timeout == None
