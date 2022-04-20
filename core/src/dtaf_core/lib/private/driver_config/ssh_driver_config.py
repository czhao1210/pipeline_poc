from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig


class SshDriverConfig(BaseDriverConfig):
    def __init__(self, cfg_opts, log):
        super(SshDriverConfig, self).__init__(cfg_opts, log)
        driver_name = list(cfg_opts.keys())[0]
        cfg_dict = dict(cfg_opts)
        self._ip = cfg_dict[driver_name]["ipv4"]
        self._user = cfg_dict[driver_name]["credentials"]["@user"]
        self._password = cfg_dict[driver_name]["credentials"]["@password"]

        try:
            self._jump_host = cfg_dict[driver_name]["credentials"]["@jump_host"]
            self._jump_user = cfg_dict[driver_name]["credentials"]["@jump_user"]
            self._jump_auth = cfg_dict[driver_name]["credentials"]["@jump_auth"]
        except KeyError:
            self._jump_host = None
            self._jump_user = None
            self._jump_auth = None
        try:
            self._port = cfg_dict[driver_name]['port']
        except KeyError:
            self._port = 22
        try:
            self._jump_auth = cfg_dict[driver_name]["credentials"]["@jump_auth"]
        except KeyError:
            self._jump_auth = None

        try:
            self._server_path = cfg_dict[driver_name]["script_execution"]["server_path"]
            self._enable = bool(cfg_dict[driver_name]["script_execution"]["enable"])
        except KeyError:
            self._server_path = None
            self._enable = False

        try:
            self._retry_cnt = cfg_dict[driver_name]["retry_cnt"]
        except KeyError:
            self._retry_cnt = 1

    @property
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    @property
    def retry_cnt(self):
        return self._retry_cnt

    @property
    def user(self):
        return self._user

    @property
    def password(self):
        return self._password

    @property
    def jump_host(self):
        return self._jump_host

    @property
    def jump_user(self):
        return self._jump_user

    @property
    def jump_auth(self):
        return self._jump_auth

    @property
    def server_path(self):
        return self._server_path

    @property
    def enable(self):
        return self._enable
