from xml.etree import ElementTree
import xmltodict
class BaseDriverConfig(object):
    def __init__(self, cfg_opts, log):
        super(BaseDriverConfig, self).__init__()
        self.__cfg = cfg_opts
        self.__log = log
        if ElementTree.iselement(cfg_opts):
            self.__cfg = xmltodict.parse(ElementTree.tostring(cfg_opts))
        self.__name = list(self.__cfg.keys())[0]

    @property
    def name(self):
        return self.__name

    def __enter__(self):
        """
        Enter resource context for this driver.

        :return: Resource to use (usually self)
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit resource context for this driver.

        :param exc_type: Exception type
        :param exc_val: Exception value
        :param exc_tb: Exception traceback
        :return: None
        """
        pass  # Note: DO NOT return a "True" value if you override this function. Otherwise, exceptions will be hidden!

