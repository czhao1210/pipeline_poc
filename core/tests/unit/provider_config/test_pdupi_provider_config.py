from dtaf_core.lib.private.providercfg_factory import ProviderCfgFactory

ASSUME = True

import time
from xml.etree import ElementTree as ET
import xmltodict


class Logs:
    def debug(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


def power_on_states_timeout():
    time.sleep(10)
    return r'On'


def power_off_states_timeout():
    time.sleep(10)
    return r'Off'


cfg_dict = dict(
    pdupi=[
        ET.fromstring("""
            <pdupi>
                <ip>10.190.155.147</ip>
                <port>80</port>
                <proxy>http://child-prc.intel.com:913</proxy>
                <channel>ch1</channel>
                <username>admin</username>
                <password>intel@123</password>
                <masterkey>smartrpipdu</masterkey>
               <driver>
                    <pdupi>
                        <ip>10.190.155.147</ip>
                        <port>80</port>
                        <proxy>http://child-prc.intel.com:913</proxy>
                        <channel>ch1</channel>
                        <username>admin</username>
                        <password>intel@123</password>
                        <masterkey>smartrpipdu</masterkey>
                    </pdupi>
                </driver>
            </pdupi>
        """),
        xmltodict.parse("""
            <pdupi>
                <ip>10.190.155.147</ip>
                <port>80</port>
                <proxy>http://child-prc.intel.com:913</proxy>
                <channel>ch1</channel>
                <username>admin</username>
                <password>intel@123</password>
                <masterkey>smartrpipdu</masterkey>
               <driver>
                    <pdupi>
                        <ip>10.190.155.147</ip>
                        <port>80</port>
                        <proxy>http://child-prc.intel.com:913</proxy>
                        <channel>ch1</channel>
                        <username>admin</username>
                        <password>intel@123</password>
                        <masterkey>smartrpipdu</masterkey>
                    </pdupi>
                </driver>
            </pdupi>
        """)],
    pdupi_err=[
        ET.fromstring("""
            <pdupi>
                <ip><xxx></xxx></ip>
                <port>80</port>
                <proxy>http://child-prc.intel.com:913</proxy>
                <channel>ch1</channel>
                <username>admin</username>
                <password>intel@123</password>
                <masterkey>smartrpipdu</masterkey>
               <driver>
                    <pdupi>
                        <ip>10.190.155.147</ip>
                        <port>80</port>
                        <proxy>http://child-prc.intel.com:913</proxy>
                        <channel>ch1</channel>
                        <username>admin</username>
                        <password>intel@123</password>
                        <masterkey>smartrpipdu</masterkey>
                    </pdupi>
                </driver>
            </pdupi>
        """),
        xmltodict.parse("""
            <pdupi>
                <ip><xxx></xxx></ip>
                <port>80</port>
                <proxy>http://child-prc.intel.com:913</proxy>
                <channel>ch1</channel>
                <username>admin</username>
                <password>intel@123</password>
                <masterkey>smartrpipdu</masterkey>
               <driver>
                    <pdupi>
                        <ip>10.190.155.147</ip>
                        <port>80</port>
                        <proxy>http://child-prc.intel.com:913</proxy>
                        <channel>ch1</channel>
                        <username>admin</username>
                        <password>intel@123</password>
                        <masterkey>smartrpipdu</masterkey>
                    </pdupi>
                </driver>
            </pdupi>
        """)
    ]
)


class TestSetupmenuProviderConfig:
    def test_pdupi_provider_cfg_normal(self):
        for cfg in cfg_dict["pdupi"]:
            with ProviderCfgFactory.create(cfg, Logs()) as cfg_model:
                driver_cfg = cfg_model.driver_cfg
                for k, v in cfg_model.__dict__.items():
                    print(k, v)
                    assert v is not None
                for k, v in driver_cfg.__dict__.items():
                    print(k, v)
                    assert v is not None

    def test_pdupi_provider_cfg_error(self):
        for cfg in cfg_dict["pdupi_err"]:
            with ProviderCfgFactory.create(cfg, Logs()) as cfg_model:
                driver_cfg = cfg_model.driver_cfg
                for k, v in cfg_model.__dict__.items():
                    print(k, v)
                    try:
                        assert v is None
                    except:
                        pass
                for k, v in driver_cfg.__dict__.items():
                    print(k, v)
                    assert v is not None
