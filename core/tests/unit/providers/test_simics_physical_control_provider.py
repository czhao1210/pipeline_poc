from dtaf_core.providers.internal.simics_physical_control_provider import SimicsPhysicalControlProvider
from dtaf_core.providers.provider_factory import ProviderFactory
import xml.etree.ElementTree as ET
import mock
import pytest

cfg_opts = ET.fromstring("""
<ac>
    <timeout>
        <power_on>5</power_on>
        <power_off>20</power_off>
    </timeout>
   <driver>
        <simics>
            <serial_port>2122</serial_port>
            <host>
                <name>10.148.204.64</name>
                <port>22</port>
                <username>uuuuu</username>
                <password>xxxxx</password>
            </host>
            <service_port>2121</service_port>
            <app>/nfs/site/disks/simcloud_users/raoarcha/workarea/projects/gnr-6.0/2021ww26.2/simics</app>
            <project>/nfs/site/disks/simcloud_users/raoarcha/workarea/projects/gnr-6.0/2021ww26.2</project>
            <script>/nfs/site/disks/simcloud_users/raoarcha/workarea/projects/gnr-6.0/2021ww26.2/targets/birchstream/birchstream-ap.simics</script>
        </simics>
    </driver>
</ac>
""")


class TestSimicsPhysicalControlProvider(object):

    @mock.patch(r'dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @mock.patch(r"dtaf_core.providers.internal.simics_physical_control_provider.DriverFactory.create")

    def test_read_s_pin_success(self, mock_simics, mock_cfg):
        with SimicsPhysicalControlProvider(cfg_opts, mock.MagicMock()) as obj:  # type: SimicsPhysicalControlProvider
            mock_simics.return_value.__enter__.return_value.launch_simics.return_value = True
            mock_simics.return_value.__enter__.return_value.start.return_value = None
            mock_simics.return_value.__enter__.return_value.is_simics_running.return_value = True
            mock_simics.return_value.__enter__.return_value.register.return_value = None
            assert obj.read_s3_pin()
            assert obj.read_s4_pin()

    @mock.patch(r'dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @mock.patch(r"dtaf_core.providers.internal.simics_physical_control_provider.DriverFactory.create")

    def test_read_s_pin_exception(self, mock_simics, mock_cfg):
        with SimicsPhysicalControlProvider(cfg_opts, mock.MagicMock()) as obj:  # type: SimicsPhysicalControlProvider
            mock_simics.return_value.__enter__.return_value.launch_simics.return_value = False
            mock_simics.return_value.__enter__.return_value.start.return_value = None
            mock_simics.return_value.__enter__.return_value.is_simics_running.return_value = False
            mock_simics.return_value.__enter__.return_value.register.return_value = None
            try:
                assert not obj.read_s4_pin()
            except Exception as ex:
                pass

