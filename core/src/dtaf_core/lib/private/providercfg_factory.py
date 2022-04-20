from importlib import import_module
import xml
from xml.etree.ElementTree import Element, tostring
import xmltodict

class ProviderCfgFactory(object):
    @staticmethod
    def create(cfg_opts, log):
        cfg_dict = cfg_opts

        # if isinstance(cfg_opts, Element):
        if xml.etree.ElementTree.iselement(cfg_opts):
            cfg_dict = xmltodict.parse(tostring(cfg_opts))
        provider_name = list(dict(cfg_dict).keys())[0]
        package = r"dtaf_core.lib.private.provider_config.{}_provider_config".format(provider_name)
        provider_name_sections = provider_name.split("_")
        provider_class_name = "".join(map(lambda x: x.capitalize(), provider_name_sections))
        mod_name = r"{}ProviderConfig".format(provider_class_name)
        mod = import_module(package, mod_name)
        aclass = getattr(mod, mod_name)
        return aclass(cfg_opts=cfg_dict, log=log)
