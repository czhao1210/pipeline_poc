import xml.etree.ElementTree as ET
import mock
import pytest
from dtaf_core.lib.private.driver_config.simics_driver_config import SimicsDriverConfig

cfg_opts = ET.fromstring("""
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
""")


class TestSimicsDriverConfig(object):

    @mock.patch(r"dtaf_core.providers.internal.simics_ac_provider.DriverFactory.create")
    def test_ac_power_on(self, mock_simics):
        with SimicsDriverConfig(cfg_opts, mock.MagicMock()) as obj: #type: SimicsDriverConfig
            assert isinstance(obj.app, str) and len(obj.app) > 0
            assert isinstance(obj.name, str) and len(obj.name) > 0
            assert isinstance(obj.host, str) and len(obj.host) > 0
            assert isinstance(obj.host_password, str) and len(obj.host_password) > 0
            assert isinstance(obj.host_username, str) and len(obj.host_username) > 0
            assert isinstance(obj.script, str) and len(obj.script) > 0
            assert isinstance(obj.service_port, int)
            assert isinstance(obj.project, str) and len(obj.project) > 0
            assert isinstance(obj.host_port, int)