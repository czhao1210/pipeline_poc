from dtaf_core.lib.private.provider_config.base_provider_config import BaseProviderConfig
from dtaf_core.lib.config_file_constants import ConfigFileParameters


class DeploymentProviderConfig(BaseProviderConfig):
    def __init__(self, cfg_opts, log):
        super(DeploymentProviderConfig, self).__init__(cfg_opts, log)
        try:
            self.__repo_user = cfg_opts.find(
                ConfigFileParameters.XML_PATH_TO_DOWNLOAD_CRED
            ).attrib[ConfigFileParameters.ATTR_DEPLOYMENT_USER].strip()
            self.__repo_password = cfg_opts.find(
                ConfigFileParameters.XML_PATH_TO_DOWNLOAD_CRED
            ).attrib[ConfigFileParameters.ATTR_DEPLOYMENT_PASSWORD].strip()
            self.__local_root = cfg_opts.find(ConfigFileParameters.XML_PATH_TO_LOCAL_ROOT).text.strip()
        except AttributeError as attrib_err:
            # timeout not found in configuration file
            self.__repo_user = ""
            self.__repo_password = ""
            self.__local_root = ""

    @property
    def repo_user(self):
        return self.__repo_user

    @property
    def repo_password(self):
        return self.__repo_password

    @property
    def local_root(self):
        return self.__local_root
