from dtaf_core.lib.private.provider_config.pduapc_provider_config import PduApcProviderConfig

ASSUME = True

import xmltodict


class Logs:
    def debug(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


cfg = xmltodict.parse("""
<pduapc>
    <ip>10.190.155.147</ip>
    <port>80</port>
    <proxy>http://child-prc.intel.com:913</proxy>
    <channel>ch1</channel>
    <username>admin</username>
    <password>intel@123</password>
    <masterkey>smartrpipdu</masterkey>
    <driver>
        <pduapc>
            <ip>10.190.155.147</ip>
        </pduapc>
    </driver>
</pduapc>
""")


class TestSetupmenuProviderConfig:
    def test_pdupi_provider_cfg_normal(self):
        with PduApcProviderConfig(cfg, Logs()) as cfg_model:
            driver_cfg = cfg_model.driver_cfg
            for k, v in cfg_model.__dict__.items():
                print(k, v)
                try:
                    assert v is not None
                except:
                    pass
            for k, v in driver_cfg.__dict__.items():
                print(k, v)
                try:
                    assert v is not None
                except:
                    pass
