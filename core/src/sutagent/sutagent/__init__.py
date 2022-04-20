from sutagent.lib.private.log_logger import sparklogger
import platform
import os
import six
from serial import Serial, SerialException

if six.PY2:
    import ConfigParser
if six.PY34 or six.PY3:
    import configparser as ConfigParser


class SutConfig:
    class Impl:
        def __init__(self):
            self._conf = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sut_agent.ini')
            self._config = ConfigParser.ConfigParser()
            # self._config.read(conf)
            # self._serial = self._get_config("SUT","Serial")
            self._serial = ''

        def _get_config(self, section, option):
            self._config.read(self._conf)
            return self._config.get(section, option)

        def is_windows(self):
            return platform.system().lower() == "windows"

        def is_linux(self):
            return platform.system().lower() == "linux"

        @property
        def serial_port(self):
            self._serial = self._get_config('SUT', 'Serial')
            if not self._serial:
                if self.is_linux():
                    self._serial = r"/dev/ttyS0"
                elif self.is_windows():
                    self._serial = r"COM1"
            print("serial port={}".format(self._serial))
            return self._serial

    __instance = None

    def __init__(self):
        if SutConfig.__instance is None:
            SutConfig.__instance = SutConfig.Impl()

    def __getattr__(self, attr):
        return getattr(SutConfig.__instance, attr)

    def __setattr__(self, attr, value):
        setattr(SutConfig.__instance, attr, value)


SUTAGENT_SERIAL_PORT = None
IP_ADDRESS = SutConfig()._get_config('SUT', 'ip')
IP_PORT = int(SutConfig()._get_config('SUT', 'port'))
BUFFER_SIZE = 1030
serial = eval(SutConfig()._get_config('SUT', 'serial_enable'))
network = eval(SutConfig()._get_config('SUT', 'network_enable'))

portNotOpenError = SerialException('serial port has not been opened')


class SerialPort(object):

    def __init__(self, port_name):
        self.port = Serial(port=port_name, baudrate='115200', xonxoff=True, timeout=1)

    def read(self):
        if not self.port:
            raise portNotOpenError

        data = ''
        length = self.port.in_waiting
        if length > 0:
            data = self.port.read(length)

        return data

    def write(self, data):
        if not self.port:
            raise portNotOpenError

        n = self.port.write(data)
        return n

    def close(self):
        if self.port:
            self.port.close()
            self.port = None


def init():
    global SUTAGENT_SERIAL_PORT
    if SUTAGENT_SERIAL_PORT is None:
        sparklogger.debug("open sut agent serial port on [{}]".format(SutConfig().serial_port))
        # SUTAGENT_SERIAL_PORT = Serial(port=SutConfig().serial_port, baudrate='115200', xonxoff=True, timeout=1)
        SUTAGENT_SERIAL_PORT = SerialPort(SutConfig().serial_port)


def delete():
    global SUTAGENT_SERIAL_PORT
    if SUTAGENT_SERIAL_PORT is not None:
        sparklogger.debug("close sut agent serial port")
        SUTAGENT_SERIAL_PORT.close()
        SUTAGENT_SERIAL_PORT = None


import os
import sys
import argparse


def write_cfg(section, option, value, config):
    ini_config_parser = ConfigParser.ConfigParser()
    ini_config_parser.read(config)
    ini_config_parser.set(section, option, value)
    with open(config, 'w') as fp:
        ini_config_parser.write(fp)


def sutagent_cfg(section, option, value):
    sutagent_ini = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sut_agent.ini')
    write_cfg(section, option, value, sutagent_ini)


def sut_cfg(section, option, value):
    sut_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib/configuration/SUT_config.cfg')
    write_cfg(section, option, value, sut_config)


def main():
    """Entry point for the application script"""
    sutagent_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sut_agent.py')
    parser = argparse.ArgumentParser(description='sutagent client')
    parser.add_argument(
        '--win_port', default='COM1',
        help="Specify serial port, default is COM1.")
    parser.add_argument(
        '--lin_port', default='/dev/ttyS0',
        help="Specify serial port, default is /dev/ttyS0.")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    if platform.system().lower() == "windows":
        sutagent_cfg('SUT', 'serial', args.win_port.upper())
        sut_cfg('Main Serial Port Configuration', 'port', args.win_port.upper())
        sut_cfg('SUTAgent Serial Port Configuration', 'port', args.win_port.upper())
    elif platform.system().lower() == "linux":
        sutagent_cfg('SUT', 'serial', args.lin_port)
        sut_cfg('Main Serial Port Configuration', 'port_linux', args.lin_port)
        sut_cfg('SUTAgent Serial Port Configuration', 'port_linux', args.lin_port)

    ret = os.system('python {}'.format(sutagent_file))
    sys.exit(ret)


if __name__ == '__main__':
    main()
