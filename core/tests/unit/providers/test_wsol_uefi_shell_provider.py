from xml.etree import ElementTree as ET

import mock

from dtaf_core.providers.internal.wsol_uefi_shell_provider import WsolUefiShellProvider

cfg_opts = ET.fromstring("""
<uefi_shell>
    <driver>
        <wsol>
            <ip>xxx</ip>
            <port>xxx</port>
            <timeout>10</timeout>
            <credentials user="debuguser" password="0penBmc1"/>
        </wsol>
    </driver>
</uefi_shell>
""")


class TestSuites:

    @staticmethod
    def test_create():
        with WsolUefiShellProvider(cfg_opts, log=mock.Mock()) as obj:
            return
