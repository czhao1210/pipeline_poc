from xml.etree import ElementTree as ET

import mock
import pytest

from dtaf_core.drivers.internal.simics_driver import SimicsDriver
from dtaf_core.drivers.internal.console.ssh_console import SshConsole
from dtaf_core.drivers.internal.console.telnet_console import TelnetConsole

cfg_normal = ET.fromstring("""
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

cfg_local = ET.fromstring("""
<simics>
    <serial_port>2122</serial_port>
    <host>
        <name>localhost</name>
    </host>
    <service_port>2121</service_port>
    <app>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww26.2/simics</app>
    <project>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww26.2</project>
    <script>/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2021ww26.2/targets/birchstream/birchstream-ap.simics</script>
</simics>
""")


class TestSimicsDriver(object):
    @mock.patch(r"dtaf_core.drivers.internal.simics_driver.ProcConsole")
    @mock.patch(r"dtaf_core.drivers.internal.simics_driver.TelnetConsole")
    @mock.patch(r"dtaf_core.drivers.internal.simics_driver.SshConsole")
    @pytest.mark.parametrize('cfg, ret_running, ret_exec, ret_is_simics_running, proc',
                             [
                                 # test remote mode
                                 (cfg_normal, True, "exec return", True, None),
                                 (cfg_normal, True, None, False, None),
                                 (cfg_normal, False, None, False, None),
                                 # test native mode
                                 (cfg_local, True, "exec return", False, None),
                                 (cfg_local, True, None, True, mock.MagicMock())
                             ])
    def test_simics_is_running_normal(self, mock_ssh, mock_telnet, mock_proc,
                                      cfg, ret_running, ret_exec, ret_is_simics_running, proc):
        with mock.patch(r"dtaf_core.drivers.internal.simics_driver.requests.session") as s:
            s.return_value.headers = dict()
            with SimicsDriver(cfg_opts=cfg, log=mock.MagicMock()) as d:  # type: SimicsDriver
                mock_proc.return_value._client = proc
                mock_ssh.return_value.is_running.return_value = ret_running
                mock_ssh.return_value.get_channel.return_value.execute_until.return_value = ret_exec
                assert d.is_simics_running() == ret_is_simics_running

    @mock.patch(r"dtaf_core.drivers.internal.simics_driver.ProcConsole")
    @mock.patch(r"dtaf_core.drivers.internal.simics_driver.TelnetConsole")
    @mock.patch(r"dtaf_core.drivers.internal.simics_driver.SshConsole")
    @pytest.mark.parametrize('cfg, ret_running, ret_exec, ret_simics_launch, proc',
                             [
                                 # test remote mode
                                 (cfg_normal, True, "exec return", True, None),
                                 (cfg_normal, True, None, False, None),
                                 (cfg_normal, False, None, False, None),
                                 # test native mode
                                 (cfg_local, True, "exec return", True, None),
                                 (cfg_local, True, None, False, mock.MagicMock())
                             ])
    def test_simics_launch(self, mock_ssh, mock_telnet, mock_proc,
                           cfg, ret_running, ret_exec, ret_simics_launch, proc):
        with mock.patch(r"dtaf_core.drivers.internal.simics_driver.requests.session") as s:
            s.return_value.headers = dict()
            with SimicsDriver(cfg_opts=cfg, log=mock.MagicMock()) as d:  # type: SimicsDriver
                import datetime
                n = datetime.datetime.now()
                with mock.patch(r"dtaf_core.drivers.internal.simics_driver.datetime") as p:
                    p.now.side_effect = ((n + datetime.timedelta(seconds=x * 5)) for x in range(0, 100))
                    mock_proc.return_value._client = proc
                    mock_ssh.return_value.is_running.return_value = ret_running
                    mock_ssh.return_value.get_channel.return_value.execute_until.return_value = ret_exec
                    mock_proc.return_value.get_channel.return_value.execute_until.return_value = ret_exec
                    mock_telnet.return_value.get_channel.return_value.execute_until.return_value = ret_exec
                    assert d.launch_simics() == ret_simics_launch
