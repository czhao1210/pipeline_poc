
#
# Serial Service module
# as a threading service, serial service will consecutively receive serial data in whole tread life cycle.
# if the match pattern is set, this service will compare with each serial line data and push it into the
# formatted queue if matched.
# DataLayer modules can get pushed data through formatted queue's get API.
#

from sutagent.lib.private.shared_data import SerialOutputCapture
import time
from serial import Serial, SerialException
from sutagent.lib.private.log_logger import sparklogger
import threading
from datetime import datetime
from time import sleep
from sutagent.lib.configuration import configuration
import os

portNotOpenError = SerialException('serial port has not been opened')


class SerialService(threading.Thread):

    # stop flag, if and only if stop API is called, this flag will set as true. default is true.
    __is_stop = True

    # save serial log to this path, it is set by setSerialLogPath API
    __serial_log_path = None

    def __init__(self, port, baudrate, serial_log_path):
        '''
        invoke Thread __init__ function to initialization thread. Open serial port. it serial log path doesn't exist
        create and open it.
        :param port: serial port name
        :param serial_log_path: serial log will be saved into this file.
        :return:
        :exception serialException, open serial port error, Access denied or port not exist.

        :dependence: Serial
        :black box equivalent class: Serial object is successfully created.
                                     SerialException
        '''
        super(SerialService, self).__init__()
        self.__port_name = port
        self.__baudrate = baudrate
        self.__serial_log_path = serial_log_path
        self.__input_buffer = ''
        self.__stop = True
        self.__lock = threading.Lock()
        self.__port = None
        self.__pause = False
        self.__buffer_size = 1024 * 12
        if serial_log_path:
            self.__log_fp = open(serial_log_path, 'w+')
        self.__open_serial()
        self.__capture_serial_output = None
        self.__log_raw_data = configuration.main_log_raw_data()
        self.__log_write = threading.Lock()
        self.sut_agent_service = False

    def __open_serial(self):
        if self.__port:
            self.__port.close()
        self.__port = Serial(self.__port_name, baudrate=self.__baudrate, timeout=1)
        sparklogger.debug('serial port[{}] has been opened'.format(self.__port_name))

    def xonxoff(self, flag):
        '''
        enable or disable software control flow. this flag will set to serial port's xonxoff property.
        :param flag: bool value. True means enable software control flow. False means disable.
        :return:
        :exception ValueError

        :dependence: port.xonxoff
        :black box equivalent class: flag = True, flag = False, flag is not bool value

        '''
        if not isinstance(flag, bool):
            raise ValueError('input type error, should bool value')
        if not self.__port:
            raise portNotOpenError
        self.__port.xonxoff = flag
        sparklogger.debug('change software control flow:{}'.format(flag))

    def read(self):
        '''
        read all data from serial service data buffer. if there is no data return ''. read API will clean up service
        side data buffer.
        before access data buffer, it will acquire a threading mutex lock, after got the data, should clean up buffer,
        then release the mutex lock. finally return got data.
        :return string data

        :dependence:
        :black box equivalent class:
        :estimated LOC: 30
        '''
        if not self.__port:
            raise portNotOpenError

        try:
            self.__lock.acquire()
            data = self.__input_buffer
            self.__input_buffer = ''
            return data
        except Exception as ex:
            sparklogger.error('read error from {0}'.format(ex))
            return ''
        finally:
            self.__lock.release()

    def write(self, data):
        '''
        write data to serial port.
        :param data: data string you want to write to serial port
        :return:
        :exception: SerialException, IO operation error, raise this exception.
                    SerialTimeoutException: when write timeout
        '''
        if not self.__port:
            raise portNotOpenError

        if self.__log_fp:
            self.write_log(True, self.sut_agent_service, data)

        # n = self.__port.write(data.encode('utf-8'))
        n = self.__port.write(data)
        sparklogger.debug("wrote data length {0}".format(n))

    def write_log(self, send, sendframe, data):
        try:
            # sparklogger.debug('write log{0} {1} {2}'.format(send, sendframe, data.replace('\33', '\\33')))
            if sendframe:
                return

            if data and self.__log_fp:
                if not self.__log_raw_data:
                    # sparklogger.debug('ro')
                    log_data = '===>{0} [{1}]: [{2}]{3}'.format(
                        datetime.now(), 'SEND' if send else 'RECV',
                        data, os.linesep)
                else:
                    # sparklogger.debug('rx')
                    log_data = data

                self.__log_write.acquire()
                self.__log_fp.write('{0}'.format(log_data))
                self.__log_write.release()
                self.__log_fp.flush()
        except Exception as ex:
            sparklogger.debug(ex)
            pass

    def run(self):
        '''
        set __is_stop as False. looping read serial data 1 byte by 1 byte and put it into a string buffer, the buffer size
        is 4096 bytes. before append read data into the buffer, this function should acquire the same threading mutex lock
        with "read" function, then will check if the data size in buffer is bigger than 4096 bytes, if yes, should pop the
        first day and append new data into buffer, else directly append data into buffer. then release the mutex lock.

        each data got from serial port should be wrote into serial log file which is already opened in Serial Service
        constructor.

        break the loop if __is_stop flag is True.

        :return
        :dependence: serial.read

        :black box equivalent class: serial.read = 1 byte data, serial.read = ""
        :estimated LOC: 150
        '''
        self.__stop = False
        log_line = ''

        try:
            while not self.__stop:
                data = None
                self.__lock.acquire()
                try:
                    if self.__pause:
                        sleep(0.2)
                    else:
                        length = self.__port.in_waiting
                        if length > 0:
                            data = self.__port.read(length)
                except Exception as ex:
                    sparklogger.error(ex)
                    raise ex
                finally:
                    self.__lock.release()

                if not data:
                    sleep(0)
                    continue
                self.__lock.acquire()
                try:
                    if self.__capture_serial_output:
                        self.__capture_serial_output.feed(data)
                    data_len = len(data)
                    in_total_size = len(self.__input_buffer) + data_len
                    if in_total_size > self.__buffer_size:
                        self.__input_buffer = self.__input_buffer[data_len:] + data
                    else:
                        if not isinstance(self.__input_buffer, bytes):
                            self.__input_buffer = self.__input_buffer.encode('utf-8')
                        self.__input_buffer += data

                    if self.__log_fp:
                        if not isinstance(log_line, bytes):
                            log_line = log_line.encode('utf-8')
                        log_line += data
                        # if there is an EOL, write into file
                        if log_line.endswith(os.linesep.encode('utf-8')) or len(log_line) >= 1024:
                            self.write_log(False, self.sut_agent_service, log_line)
                            log_line = ''
                except Exception as ex:
                    sparklogger.error(ex)
                finally:
                    self.__lock.release()
        # except Exception, ex:
        #     sparklogger.error(ex)
        finally:
            self.__stop = True
            if self.__port:
                self.__port.close()
                self.__port = None
            if self.__log_fp:
                self.write_log(False, self.sut_agent_service, log_line)
                self.__log_fp.close()
                self.__log_fp = None
            sparklogger.info('serial service is stopped.')

    def stop(self):
        '''
        set serial service __is_stop flag as true to terminate this thread. wait the thread to terminate,
        then close serial port. finally, should close serial log file handler.

        :param:
        :return:

        :dependence: serial.close, file.close
        :black box equivalent class:
        :estimated LOC: 20
        '''
        if not self.__stop:
            sparklogger.info('stop serial service')
            self.__stop = True
            self.join()

    def pause(self):
        try:
            self.__lock.acquire()
            self.__pause = True
            if self.__port:
                self.__port.close()
            self.__port = None
        except Exception as ex:
            sparklogger.error('serial pause error {0}'.format(ex))
        finally:
            self.__lock.release()

    def resume(self):
        try:
            self.__lock.acquire()
            self.__input_buffer = ''
            self.__pause = False
            self.__open_serial()
        except Exception as ex:
            sparklogger.error('serial resume error{0}'.format(ex))
        finally:
            self.__lock.release()

    def set_output_capture(self, capture):
        ret = False
        try:
            self.__lock.acquire()
            self.__capture_serial_output = capture
            ret = True
        except Exception as ex:
            sparklogger.error('set_output_capture error from {0}'.format(ex))
            self.__capture_serial_output = None
            ret = False
        finally:
            self.__lock.release()
            return ret
