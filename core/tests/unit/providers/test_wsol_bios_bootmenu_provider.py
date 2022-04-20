from xml.etree import ElementTree as ET

import mock

from dtaf_core.providers.internal.wsol_bios_bootmenu_provider import WsolBiosBootmenuProvider

cfg_opts = ET.fromstring("""
<bios_bootmenu>
    <driver>
        <wsol>
            <ip>xxx</ip>
            <port>xxx</port>
            <timeout>10</timeout>
            <credentials user="debuguser" password="0penBmc1"/>
        </wsol>
    </driver>
    <efishell_entry select_item="UEFI Internal Shell"/>
</bios_bootmenu>
""")


class TestSuites:

    @staticmethod
    def test_create():
        try:
            with WsolBiosBootmenuProvider(cfg_opts, log=mock.Mock()) as obj:
                return
        except:
            return
