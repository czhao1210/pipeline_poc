from xml.etree import ElementTree as ET

import mock

from dtaf_core.providers.internal.wsol_bios_setupmenu_provider import WsolBiosSetupmenuProvider

cfg_opts = ET.fromstring("""
<bios_setupmenu>
    <driver>
        <wsol>
            <ip>xxx</ip>
            <port>xxx</port>
            <timeout>10</timeout>
            <credentials user="debuguser" password="0penBmc1"/>
        </wsol>
    </driver>
    <efishell_entry select_item="Launch EFI Shell">
        <path>
            <node>Setup Menu</node>
            <node>Boot Manager</node>
        </path>
    </efishell_entry>
    <continue select_item="Continue"/>
    <reset press_key="\\33R\\33r\\33R" parse="False"/>
</bios_setupmenu>
""")


class TestSuites:

    @staticmethod
    def test_create():
        with WsolBiosSetupmenuProvider(cfg_opts, log=mock.Mock()) as obj:
            return
