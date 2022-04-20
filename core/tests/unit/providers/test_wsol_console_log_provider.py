from xml.etree import ElementTree as ET

import mock

from dtaf_core.providers.internal.wsol_console_log_provider import WsolConsoleLogProvider

cfg_opts = ET.fromstring("""
<console_log>
                    <runwith/>
                    <logpath>tests/system/data/</logpath>
                    <driver>
                        <wsol>
                            <ip>xxx</ip>
                            <port>xxx</port>
                            <timeout>10</timeout>
                            <credentials user="debuguser" password="0penBmc1"/>
                        </wsol>
                    </driver>
                </console_log>""")


class TestSuites:

    @staticmethod
    def test_create():
        try:
            with WsolConsoleLogProvider(cfg_opts, log=mock.Mock()) as obj:
                return
        except:
            return
