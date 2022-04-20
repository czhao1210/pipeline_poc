from dtaf_core.lib.deploy_utils import *
import mock


def mock_func(*args, **kwargs):
    return True


class TestJumpers(object):

    @staticmethod
    def test_init():
        from dtaf_core.lib.deploy_utils import ConfigurationHelper, ProviderFactory, subprocess
        ConfigurationHelper.get_sut_config = mock.Mock()
        ConfigurationHelper.get_provider_config = mock.Mock()
        with mock.patch.object(ProviderFactory, 'create') as mock_create:
            mock_create.return_value.get_device_property.return_value = 'aaa'
            mock_create.return_value.get_device_property.return_value = 'aaa'
            subprocess.Popen = mock.Mock()
            obj = Deployment('a', 'b')
            obj.provision('aaa', 'aaa', 'aaa', [{'a': 'a', 'b': 'b'}], 'aaa')
