import mock
import pytest

from dtaf_core.lib.ssh_lib import SSHlib


class TestSuites:
    @staticmethod
    @mock.patch('dtaf_core.lib.ssh_lib.paramiko')
    @pytest.mark.parametrize('execute_return', [(mock.Mock(), mock.Mock(), mock.Mock())])
    def test_download(paramiko_mock, execute_return):
        paramiko_mock.SSHClient.return_value.exec_command.return_value = execute_return
        with SSHlib(ip='xxx', port=22, username='xxx', password='xxx') as obj:
            obj.download('xxx', 'xxx')

    @staticmethod
    @mock.patch('dtaf_core.lib.ssh_lib.os')
    @mock.patch('dtaf_core.lib.ssh_lib.paramiko')
    @pytest.mark.parametrize('execute_return', [(mock.Mock(), mock.Mock(), mock.Mock())])
    def test_upload(paramiko_mock, os_mock, execute_return):
        paramiko_mock.SSHClient.return_value.exec_command.return_value = execute_return
        with SSHlib(ip='xxx', port=22, username='xxx', password='xxx') as obj:
            os_mock.path.isdir.return_value = False
            obj.upload('xxx', 'xxx')
            os_mock.path.isdir.return_value = True
            obj.upload('xxx', 'xxx')
