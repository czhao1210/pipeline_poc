"""
    Initialize the operating environment.
"""

from dtaf_core.lib.exceptions import DriverIOError
from dtaf_core.lib.private.cl_utils.adapter.capture_data import OutputCapture
from dtaf_core.lib.private.cl_utils.adapter.data_types import TimeoutConfig
from dtaf_core.lib.private.cl_utils.adapter.entry_menu import EntryMenuDataAdapter as _EntryMenuDataAdapter
from dtaf_core.lib.private.cl_utils.adapter.resolution_config import PYTE_RESOLUTION_CONFIG_10031, \
    PYTE_RESOLUTION_CONFIG_8024
from dtaf_core.lib.private.cl_utils.adapter.serial_parsing import \
    SerialParsingDataAdapter as _SimpleSerialAPIDataAdapter
from dtaf_core.lib.private.cl_utils.adapter.setup_menu import BiosSetupMenuDataAdapter as _BiosSetupMenuDataAdapter
from dtaf_core.lib.private.globals.data_type import NAVIGATION_TIMEOUT, INTERNAL_TIMEOUT
from dtaf_core.lib.private.serial_helper import SerialHelper as _SerialHelper


def _print_sut_info(sut_list):
    """
        print sut info
    """
    for idx, sut in enumerate(sut_list):
        print('sut index:', idx)
        print('sut.name:', sut.name)
        print('sut.addr:', sut.addr)
        print('sut.bind_port:', sut.bind_port)
        if sut.bmc:
            print('sut.bmc.addr:', sut.bmc.addr)
            print('sut.bmc.username:', sut.bmc.username)
            print('sut.bmc.password:', sut.bmc.password)
            print('sut.bmc.port:', sut.bmc.port)
        else:
            print('bmc not config')
        if sut.pdus:
            for idx, pdu in enumerate(sut.pdus):
                print('pdu index: ', idx)
                print('pdu.addr:', pdu.addr)
                print('pdu.power_port:', pdu.power_port)
                print('pdu.username:', pdu.username)
                print('pdu.password:', pdu.password)


class ContextInstance(object):
    """
        Initialize and create a running environment.
    """
    __instance = None
    __data_adapter = {}
    __cluster_session = None
    __cluster_context = None

    @staticmethod
    def get(serial_service=None, is_host_service=False, logger=None, width=80, high=24, buffer_name=None):
        """
        Singleton pattern, instantiation ContextInstance class.
        """
        if not ContextInstance.__instance:
            ContextInstance.__instance = ContextInstance(serial_service=serial_service,
                                                         is_host_service=is_host_service, logger=logger,
                                                         buffer_name=buffer_name, width=width, high=high)

        return ContextInstance.__instance

    def __init__(self, serial_service, is_host_service=False, logger=None,
                 width=80, high=24, buffer_name=None):
        """
            :param:serial_service:serial_service object
            :param:is_host_service:Used to distinguish whether or not host_service.
        """
        self.__logger = logger
        self.buffer_name = buffer_name
        self.__is_host_service = is_host_service
        self.__screen_width = width
        self.__screen_high = high
        self.__logger = logger
        self.__logger.debug('init ContextInstance {0}'.format(serial_service))
        self.__serial_service = serial_service
        self.__create_serial_adapter()

    def __create_serial_adapter(self):
        """
            if env is not cluster,communication use serial port,this fun will be called to create
            seirial adapter.
        """
        if self.__is_host_service:
            self.__logger.debug('be called by host_service,seirial will not be created')
            return True
        if self.__data_adapter:
            self.__logger.debug('date_adapter be created,env is cluster,not do thing.return True '
                                'and end fun')
            return True

        if not self.__serial_service:
            raise DriverIOError('error ... serial_service is None')

        self.__data_adapter['data_service'] = self.__serial_service
        self.__data_adapter['data_helper'] = _SerialHelper(self.__data_adapter['data_service'], self.__logger,
                                                           self.buffer_name)

        self.__data_adapter['setup_menu'] = _BiosSetupMenuDataAdapter(
            data_helper=self.__data_adapter['data_helper'],
            screen_high=self.__screen_high,
            screen_width=self.__screen_width,
            timeout_config=TimeoutConfig(
                navigation_timeout=NAVIGATION_TIMEOUT, inner_move_timeout=INTERNAL_TIMEOUT,
                total_timeout=900),
            cfg=dict(
                resolution_config=dict(
                    PYTE_RESOLUTION_CONFIG_8024=PYTE_RESOLUTION_CONFIG_8024,
                    PYTE_RESOLUTION_CONFIG_10031=PYTE_RESOLUTION_CONFIG_10031)),
            logger=self.__logger
        )
        from dtaf_core.lib.private.cl_utils.adapter.boot_menu import BiosBootMenuDataAdapter as _BiosBootMenuDataAdapter
        self.__data_adapter['boot_menu'] = _BiosBootMenuDataAdapter(
            data_helper=self.__data_adapter['data_helper'],
            screen_high=self.__screen_high,
            screen_width=self.__screen_width,
            navigation_timeout=NAVIGATION_TIMEOUT,
            internal_timeout=INTERNAL_TIMEOUT,
            cfg=dict(
                resolution_config=dict(
                    PYTE_RESOLUTION_CONFIG_8024=PYTE_RESOLUTION_CONFIG_8024,
                    PYTE_RESOLUTION_CONFIG_10031=PYTE_RESOLUTION_CONFIG_10031)),
            logger=self.__logger
        )
        self.__data_adapter['entry_menu'] = \
            _EntryMenuDataAdapter(data_helper=self.__data_adapter['data_helper'], logger=self.__logger)
        self.__data_adapter['simple_serial_parsing'] = \
            _SimpleSerialAPIDataAdapter(self.__data_adapter['data_helper'], self.__screen_high,
                                        self.__screen_width, {})

    @property
    def data_adapter(self):
        """
            get data_adapter value
        """
        return self.__data_adapter

    def set_output_capture(self, capture_list):
        """
            set output capture
        """
        try:
            oc_ret = OutputCapture(capture_list)
            self.__data_adapter['data_service'].set_output_capture(oc_ret)
            return True
        except Exception as ex:
            self.__logger.error('set_output_capture error from {0}'.format(ex))
            return False

    def delete(self):
        """
        delete cluster context
        """
        pass
