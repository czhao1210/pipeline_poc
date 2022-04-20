#
# CommonLib init model
#
# This model provides init() and delete() function.
#
import os
import socket
from sutagent.lib.private.serial_service import SerialException, SerialService
from sutagent.lib.configuration import configuration
from sutagent.lib.private.log_logger import sparklogger
from sutagent.lib.private.log_handler import LogHandler
from sutagent.lib.globals.data_type import TYPE_DELETE
_cluster_mode = configuration.is_cluster_mode()
_presilicon = configuration.is_presilicon()

if _presilicon:
    from sutagent.lib.cl_utils.communication.session import delete as cl_communication_delete
    from sutagent.lib.cl_utils.communication.session import init as cl_communication_init

# Serial port variables definition
g_main_serial_service = None
g_sutagent_serial_service = None

g_socket_server = None
IP_ADDRESS = configuration.get_value('SUT Connection', 'ip')
IP_PORT = 11111
BUFFER_SIZE = 1030
conn_type = configuration.get_value('SUT Connection', 'connection')


def init(entity=None):
    """
    Generate two instances of SerialService for dataLayer.
    One is for main serial service, the other is for sutAgent serial service.
    If the main serial port is configured as the same port of the sutAgent serial port, then generate only one instance.
    :param: None
    :return: None

    dependency: configuration.get_value()
                SerialService.start()

    black box equivalent class :
                                 Main port is None but sutAgent port is not None;
                                 Main port is not None but sutAgent port is None;
                                 Main port is the same as sutAgent port;
                                 Main port is not the same as sutAgent port;
                                 Serial raise SerialException;
                                 Serial raise ValueError.

    estimated LOC = 30
    """
    global g_main_serial_service
    global g_sutagent_serial_service
    # cl_communication_init('127.0.0.1', configuration.get_cl_host_client_port())
    if entity:
        sparklogger.info('$$$$ init-1 entity:{}'.format(entity))
        main_port_name = configuration.get_main_port_name(entity)
        sparklogger.info('main_port_name...... {0}'.format(main_port_name))
        main_baudrate = configuration.get_value('Main Serial Port Configuration', 'baudrate')
        sutagent_port_name = configuration.get_sutagent_port_name(entity)
        sparklogger.info('sutagent_port_name...... {0}'.format(sutagent_port_name))
        sutagent_baudrate = configuration.get_value('SUTAgent Serial Port Configuration', 'baudrate')

        if not main_port_name:
            sparklogger.error(r'can\'t get Main Serial Port')
            raise ValueError



        log_path = os.getenv('CAF_CASE_LOG_PATH') if os.getenv('CAF_CASE_LOG_PATH') else os.getenv('LC_RESULT_PATH')
        if not log_path:
            if configuration.is_windows_host():
                log_path = r'C:\Temp'
            elif configuration.is_linux_host():
                log_path = r'/tmp'
            else:
                sparklogger.error('platform {0} not config'.format(configuration.host_platform()))

            if not os.path.exists(log_path):
                os.mkdir(log_path)
        main_serial_service_log = os.path.join(log_path, 'main.log')
        sutagent_serial_service_log = os.path.join(log_path, 'sutagent.log')

        try:
            g_main_serial_service = SerialService(main_port_name, main_baudrate, main_serial_service_log)
            g_main_serial_service.setDaemon(True)
            g_main_serial_service.start()

            if main_port_name.lower() == sutagent_port_name.lower():
                g_sutagent_serial_service = g_main_serial_service
            else:
                if sutagent_port_name:
                    g_sutagent_serial_service = SerialService(sutagent_port_name, sutagent_baudrate,
                                                              sutagent_serial_service_log)
                    g_sutagent_serial_service.setDaemon(True)
                    g_sutagent_serial_service.start()
            g_sutagent_serial_service.sut_agent_service = True
        except Exception:
            sparklogger.error(r'init raise error')
            raise
    else:

        #if configuration.is_presilicon() and configuration.is_linux_host():
         #   return
        main_port_name = configuration.get_main_port_name()
        main_baudrate = configuration.get_value('Main Serial Port Configuration', 'baudrate')
        sutagent_port_name = configuration.get_sutagent_port_name()
        sutagent_baudrate = configuration.get_value('SUTAgent Serial Port Configuration', 'baudrate')

        if not main_port_name:
            sparklogger.error(r'can\'t get Main Serial Port')
            raise ValueError
        log_path = configuration.get_log_path()
        main_serial_service_log = os.path.join(log_path, 'main.log')
        sutagent_serial_service_log = os.path.join(log_path, 'sutagent.log')

        try:

            g_main_serial_service = SerialService(main_port_name, main_baudrate, main_serial_service_log)
            g_main_serial_service.setDaemon(True)
            g_main_serial_service.start()

            if main_port_name.lower() == sutagent_port_name.lower():
                g_sutagent_serial_service = g_main_serial_service
            else:
                if sutagent_port_name:
                    g_sutagent_serial_service = SerialService(sutagent_port_name, sutagent_baudrate,
                                                              sutagent_serial_service_log)
                    g_sutagent_serial_service.setDaemon(True)
                    g_sutagent_serial_service.start()
            g_sutagent_serial_service.sut_agent_service = True
        except Exception:
            sparklogger.error(r'init raise error')
            raise


def delete():
    """
    Delete the instances of SerialService for dataLayer.
    If there are two serial port instances, call SerialService.stop() twice.
    :param: None
    :return:

    dependency: SerialService.stop()

    black box equivalent class : Two serial service need to be closed;
                                 Only one serial service needs to be closed.

    estimated LOC = 30
    """

    sparklogger.info('stop serial services')
    global g_main_serial_service
    global g_sutagent_serial_service
    if g_main_serial_service:
        g_main_serial_service.stop()
        g_main_serial_service = None
    if g_sutagent_serial_service:
        g_sutagent_serial_service.stop()
        g_sutagent_serial_service = None

    sparklogger.info('filter Local logs by date')
    try:
        LogHandler.log_processor()
    except Exception as ex:
        sparklogger.info('LogHandler.log_processor .error...... {0}'.format(ex))
