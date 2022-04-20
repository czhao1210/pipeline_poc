from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element
from lib.configuration import ConfigurationHelper
from lib.private.providercfg_factory import ProviderCfgFactory
tree = ET.ElementTree()
tree.parse(r"configuration_sample.xml")
root = tree.getroot()
# suts = root.find(r"suts")

sut_dict = dict(
            platform=dict(
                attrib=dict(type=r"commercial")
            ),
            silicon=dict()
        )

ret = Element("result", attrib={})
# ret.extend(conf.filter_providers(r"10.13.168.111", sut_dict, r"dc", r"rsc2"))
# ret.extend(conf.filter_suts(r"10.13.168.111", sut_dict))
sut = ConfigurationHelper.filter_sut_config(root, r"10.13.168.111", sut_filter=sut_dict)[0]
ET.dump(sut)
provider = ConfigurationHelper.get_provider_config(sut=sut, provider_name=r"sutos", attrib=dict(name=r"Linux", subtype=r"CentOS"))
print(r"=======provider===========")
ET.dump(provider)
driver = ConfigurationHelper.get_driver_config(provider=provider, driver_name=r"socket", attrib=dict())
print(r"=======driver===========")
ET.dump(driver)
print(r"xxxx")
# print(ProviderCfgFactory.create(provider, None).driver_cfg.low_voltage)
