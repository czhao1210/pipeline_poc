from xml.etree import ElementTree as ET

import mock

from dtaf_core.providers.internal.wsol_sut_os_provider import WsolSutOsProvider

cfg_opts = ET.fromstring("""
<sut_os name="Linux" subtype="RHEL" version="7.6" kernel="3.10" verify="false">
    <shutdown_delay>10</shutdown_delay>
    <driver>
        <wsol>
            <ip>xxx</ip>
            <port>xxx</port>
            <timeout>10</timeout>
            <credentials user="debuguser" password="0penBmc1"/>
        </wsol>
    </driver>
</sut_os>
""")


class TestSuites:

    @staticmethod
    def test_create():
        try:
            with WsolSutOsProvider(cfg_opts, log=mock.Mock()) as obj:
                return
        except:
            return 
