__author__ = 'zhuguozx'
import datetime
import re
from sutagent.lib.private.log_logger import sparklogger
import time

from sutagent.lib.cl_utils.adapter.data_helper import DataService as _DataService


class Filter_serial(object):
    def __init__(self):
        self.filter_data_list = None

    def set_filter_data(self, filter_data_list):
        self.filter_data_list = filter_data_list

    def clear_filter_data(self):
        self.filter_data_list = None


filter_serial = Filter_serial()


class SerialHelper(_DataService):
    def __init__(self, data_service):
        super(SerialHelper, self).__init__()
        self.__data_service = data_service

    def __filter_utf_8(self, data):
        filter_pattern = r'[^\x00-\x7f]'
        while re.search(filter_pattern, data):
            sparklogger.error('filter utf-8 .....')
            data = re.sub(filter_pattern, '', data)

        return data

    def __filter_dirty_data(self, data):
        if not filter_serial.filter_data_list:
            return data
        for keyword in filter_serial.filter_data_list:
            if keyword in data:
                sparklogger.error("filter dirty data ....")
                return None
        return data

    def __trim_frame_tail(self, data):
        try:
            if not data:
                return data

            index = data.rfind('\33')
            if index != -1:
                sparklogger.debug(
                    'trim_frame_tail:[{0}]'.format(data[index:].replace('\33', '\\33')))
                data = data[:index]

            if data:
                index = data.rfind('\33')
                if index != -1:
                    if re.search('\33\[[34][0-7]m\33\[[34][0-7]m', data[index + 1:]):
                        sparklogger.debug(
                            'trim_frame_tail:[{0}]'.format(data[index:].replace('\33', '\\33')))
                        data = data[:index]

            return data
        except Exception as ex:
            sparklogger.error('__trim_frame_tail {0}'.format(ex))
            raise Exception(ex)

    def __trim_frame_head(self, data):
        try:
            if not data:
                return data

            index = data.find('\33')
            if index not in [0, -1]:
                sparklogger.debug('trim_frame_head:[{0}]'.format(data[:index].replace('\33', '\\33')))
                return data[index:]

            return data
        except Exception as ex:
            sparklogger.error('__trim_frame_head {0}'.format(ex))
            raise Exception(ex)

    def read_frame(self, timeout, heartbeats, max_size):
        try:
            recv_data_list = []
            recv_data = ""
            total_len = 0
            dt = datetime.datetime.now()
            sep = None

            while (datetime.datetime.now() - dt).seconds < timeout:
                data = self.__data_service.read()
                if data:
                    sep = time.time()
                    recv_data_list.append(data)
                    total_len += len(data)
                    if total_len > max_size:
                        recv_data = self.__trim_frame_tail("".join(recv_data_list))
                        recv_data = self.__trim_frame_head(recv_data)
                        sparklogger.debug('larger package %d' % total_len)
                        break
                else:
                    if sep and (time.time() - sep) > heartbeats:
                        recv_data = "".join(recv_data_list)
                        break
            recv_data = self.__filter_utf_8(recv_data)
            return self.__filter_dirty_data(recv_data)
        except Exception as ex:
            sparklogger.error('read_frame {0}'.format(ex))
            raise Exception(ex)

    def read_until(self, pattern, timeout):
        '''

        :param pattern: if pattern is set, func will be return if pattern is find in output string else will be wait timeout
        :param timeout:
        :return:
        '''
        recv_data = ''
        try:
            dt = datetime.datetime.now()
            while (datetime.datetime.now() - dt).seconds < timeout:
                data = self.__slower_read(1)
                if data:
                    sparklogger.debug('SERIAL DATA: {0}'.format(data.replace('\33', '\\33')))
                    recv_data += data

                if pattern and re.search(pattern, recv_data):
                    break

            return recv_data
        except Exception as ex:
            sparklogger.error('SerialHelper.read_until ex {0}'.format(ex))
            raise Exception(ex)

    def __slower_read(self, timeout):
        dt = time.time()
        recv_data = ''
        while (time.time() - dt) < timeout:
            data = self.__data_service.read()
            if data:
                recv_data += data

        # print 'slower read end...'
        return recv_data

    def read(self):
        try:
            return self.__data_service.read()
        except Exception as ex:
            sparklogger.error('SerialHelper.read ex {0}'.format(ex))
            raise Exception(ex)

    def write(self, data):
        try:
            self.__data_service.write(data)
        except Exception as ex:
            sparklogger.error('SerialHelper.write ex {0}'.format(ex))
            raise Exception(ex)
