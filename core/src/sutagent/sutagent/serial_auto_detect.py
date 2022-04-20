from sutagent.lib.private.log_logger import sparklogger
from sutagent.lib.globals.data_type import *
from sutagent import init, delete
from serial.tools import list_ports
import os
import re
import json
import platform
import six
if six.PY2:
    import ConfigParser
if six.PY3 or six.PY34:
    import configparser as ConfigParser


class SerialAutoDetect:

    __config = ConfigParser.ConfigParser()
    __config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sut_agent.ini')
    __config.read(__config_file)
    serial_auto_detect = __config.get('SUT', 'Serial_auto_detect')

    @classmethod
    def seek_available_port(cls):
        '''
        enumerate each port and traverse it to instance serial obj, handshake communication by serial_transport module
        :return:True if port available else False
        :dependence:serial_transport.py
        :black box equivalent class:  Message.send raise a TransportError,Message.send raise an Exception
                                    list_ports.comports == 0,list_ports.comports == 1,list_ports.comports > 1
        '''
        send_ack = {TYPE_ENTEROS: [platform.system(), ENTER_OS_START_UP]}
        json_str = json.dumps(send_ack)
        __ports = (i[0] for i in list_ports.comports())
        detected = False
        for port in __ports:
            if cls.__write_port_to_config(port):
                init()
                from sutagent.lib.private import serial_transport
                if six.PY34 or six.PY3:
                    from imp import reload
                reload(serial_transport)
                try:
                    serial_transport.Message.send(json_str)
                    detected = True
                    break
                except Exception as ex:
                    sparklogger.error('[{0} ERROR]: {1}'.format(port, ex))
                finally:
                    delete()
        return detected

    @classmethod
    def __write_port_to_config(cls, port_name):
        '''
        save port into file
        :param port_name: like COM1,COM2,ttyS0,ttyS1,ttyUSB0,ttyUSB1
        :return:Ture if write successfully else False
        :black box equivalent class: pattern matched,pattern is not matched
        '''
        pat = re.compile((r'COM\d+|/dev/ttyS\d+|/dev/ttyUSB\d+'))
        m = pat.match(port_name)
        if m:
            cls.__config.set('SUT', 'Serial', port_name)
            with open(cls.__config_file, 'w') as fp:
                cls.__config.write(fp)
            if port_name == cls.__config.get('SUT', 'Serial'):
                return True
            else:
                sparklogger.error('Fail to write {} to config'.format(port_name))
                return False
        else:
            sparklogger.warning('[{}] port name format is incorrected'.format(port_name))
            return False

    @classmethod
    def set_config(cls, section, option, value):
        cls.__config.set(section, option, value)
        with open(cls.__config_file, 'w') as fp:
            cls.__config.write(fp)
