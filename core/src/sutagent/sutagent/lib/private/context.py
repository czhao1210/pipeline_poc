"""
    Initialize the operating environment.
"""
import os
from sutagent.lib.private.log_logger import sparklogger
from sutagent.lib.private.serial_helper import SerialHelper as _SerialHelper
from sutagent.lib.configuration import configuration
from sutagent.lib.cl_utils.adapter.capture_data import OutputCapture


def _print_sut_info(sut_list):
    '''
        print sut info
    '''
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
        else:
            print('pdu is not config')


class ContextInstance(object):
    '''
        Initialize and create a running environment.
    '''
    __instance = None
    __data_adapter = {}
    __cluster_session = None
    __cluster_context = None

    @staticmethod
    def get(serial_service=None, is_host_service=False):
        '''
            Singleton pattern, instantiation ContextInstance class.
        '''
        if not ContextInstance.__instance:
            ContextInstance.__instance = ContextInstance(serial_service=serial_service,
                                                         is_host_service=is_host_service)

        return ContextInstance.__instance

    def __init__(self, serial_service, is_host_service=False):
        '''
            :param:serial_service:serial_service object
            :param:is_host_service:Used to distinguish whether or not host_service.
        '''
        self.__cluster_mode = configuration.is_cluster_mode()
        self.__is_host_service = is_host_service
        sparklogger.debug('init ContextInstance {0}'.format(serial_service))
        sparklogger.debug('init ContextInstance self.__cluster_mode {0}'.
                          format(self.__cluster_mode))
        self.__serial_service = serial_service
        if not self.__cluster_mode:
            self.__state_file = configuration.state_file()
            self.__create_seirial_adapter()

        else:
            self.__create_cluster_adapter()

    @property
    def state_file(self):
        '''
            RETURN SUT STATE
        '''
        return self.__state_file

    @property
    def cluster_mode(self):
        '''
            RETURN CALSTER MODE
        '''
        return self.__cluster_mode

    def __create_cluster_adapter(self):
        '''
            If env is cluster,this fun be called.
        '''
        if self.__data_adapter:
            return

        if not self.__cluster_context:
            raise Exception('create cluster ctx fail')

        sut = self.__cluster_context.pickup_sut()
        if not sut:
            raise Exception('pick sut fail')
        sut._SUT__sol_log_raw_data = configuration.main_log_raw_data()
        sut._SUT__sol_log_name = os.path.join(configuration.get_log_path(),
                                              'main_{0}.log'.format(sut.addr.replace('.', '_')))
        sut._SUT__sol_read_timeout = 1
        self.__state_file = os.path.join(os.path.dirname(configuration.state_file()),
                                         'state_{0}.tmp'.format(sut.addr.replace('.', '_')))
        sparklogger.debug('CURRENT: state file : {0}'.format(self.__state_file))

        _print_sut_info([sut])

    def __create_seirial_adapter(self):
        '''
            if env is not cluster,communication use serial port,this fun will be called to create
            seirial adapter.
        '''
        if self.__is_host_service:
            sparklogger.debug('be called by host_service,seirial will not be created')
            return True
        if self.__data_adapter:
            sparklogger.debug('date_adapter be created,env is cluster,not do thing.return True '
                              'and end fun')
            return True

        if not self.__serial_service:
            raise Exception('error ... serial_service is None')

        self.__data_adapter['data_service'] = self.__serial_service
        self.__data_adapter['data_helper'] = _SerialHelper(self.__data_adapter['data_service'])

    @property
    def data_adapter(self):
        '''
            get data_adapter value
        '''
        return self.__data_adapter

    def set_output_capture(self, capture_list):
        '''
            set output capture
        '''
        try:
            oc_ret = OutputCapture(capture_list)
            self.__data_adapter['data_service'].set_output_capture(oc_ret)
            return True
        except Exception as ex:
            sparklogger.error('set_output_capture error from {0}'.format(ex))
            return False

    def delete(self):
        '''
        delete cluster context
        '''
        if self.cluster_mode and self.__cluster_context:
            self.__cluster_context.delete()
        # if self.cluster_mode and self.__virtual_media:
        #     self.__virtual_media.umount_virtual_media()
