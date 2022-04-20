from dtaf_core.lib.private.provider_config.base_provider_config import BaseProviderConfig


class PcieHwInjectorProviderConfig(BaseProviderConfig):
    """
    Configuration options for PcieHwInjector, regardless of concrete implementation.
    """
    def __init__(self, cfg_opts, log):

        super(PcieHwInjectorProviderConfig, self).__init__(cfg_opts, log)
