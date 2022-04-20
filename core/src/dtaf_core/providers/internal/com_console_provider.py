from dtaf_core.providers.internal.base_console_provider import BaseConsoleProvider


class ComConsoleProvider(BaseConsoleProvider):
    def __init__(self, cfg_opts, log):
        """
        Create a new BmcProvider object.

        :param cfg_opts: xml.etree.ElementTree.Element of configuration options for execution environment
        :param log: Logger object to use for output messages
        """
        super(ComConsoleProvider, self).__init__(cfg_opts, log)

    def __enter__(self):
        return super(ComConsoleProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(ComConsoleProvider, self).__exit__(exc_type, exc_val, exc_tb)
