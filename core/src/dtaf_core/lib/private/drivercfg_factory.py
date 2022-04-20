from importlib import import_module
from xml.etree.ElementTree import Element, tostring
import xmltodict
import xml

class DriverCfgFactory(object):
    @staticmethod
    def create(cfg_opts, log):
        if xml.etree.ElementTree.iselement(cfg_opts):
            cfg_opts = dict(xmltodict.parse(tostring(cfg_opts)))
        driver_name = list(dict(cfg_opts).keys())[0]
        package = r"dtaf_core.lib.private.driver_config.{}_driver_config".format(driver_name)
        mod_name = r"{}DriverConfig".format("".join([driver_name[0].upper(), driver_name[1:]]))
        mod = import_module(package, mod_name)
        aclass = getattr(mod, mod_name)
        return aclass(cfg_opts=cfg_opts, log=log)

