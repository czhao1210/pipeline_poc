from dtaf_core.providers.internal.pdu_ac_provider import PduAcProvider
import xml.etree.ElementTree as ET


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


cfg_opts = ET.fromstring("""
<ac>
                   <driver>
                       <pdu brand="raritan" model="px-5052R">
                            <ip>xxx.xxx.xxx.xxx</ip>
                            <port>22</port>
                            <username>xxx</username>
                            <password>xxx</password>
                            <timeout>
                                <powerstate>20</powerstate>
                                <invoke>5</invoke>
                            </timeout>
                            <outlets>
                                <outlet>100</outlet>
                            </outlets>
                        </pdu>
					</driver>
                    <timeout>
                        <power_on>5</power_on>
                        <power_off>5</power_off>
                    </timeout>
                </ac>""")
log = _Log()


class TestPduPduAcProvider(object):
    @staticmethod
    def test_ac_power_on():
        with PduAcProvider(cfg_opts, log) as obj:
            try:
                obj.ac_power_on()
            except:
                return

    @staticmethod
    def test_ac_power_off():
        with PduAcProvider(cfg_opts, log) as obj:
            try:
                obj.ac_power_off()
            except:
                return

    @staticmethod
    def test_get_ac_power_state():
        with PduAcProvider(cfg_opts, log) as obj:
            try:
                obj.get_ac_power_state()
            except:
                return

    @staticmethod
    def test_set_username_password():
        with PduAcProvider(cfg_opts, log) as obj:
            try:
                obj.set_username_password()
            except:
                pass

    @staticmethod
    def test_reset_username_password():
        with PduAcProvider(cfg_opts, log) as obj:
            try:
                obj.reset_username_password()
            except:
                pass
