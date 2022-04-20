from importlib import import_module


class DriverCfgFactory(object):
    @staticmethod
    def create(cfg_opts, log):
        package = r"drivers.internal.{}_driver".format(cfg_opts.tag)
        mod_name = r"{}Driver".format("".join([cfg_opts.tag[0].upper(), cfg_opts.tag[1:]]))
        mod = import_module(package, mod_name)
        aclass = getattr(mod, mod_name)
        return aclass(cfg_opts=cfg_opts, log=log)
