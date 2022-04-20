import datetime
import re
import time

from dtaf_core.lib.private.cl_utils.adapter.helper.data_helper import DataService as _DataService


class FilterSerial(object):

    instance = None

    def __init__(self):
        self.filter_data_list = None

    def set_filter_data(self, filter_data_list):
        self.filter_data_list = filter_data_list

    def clear_filter_data(self):
        self.filter_data_list = None

    @staticmethod
    def get():
        if FilterSerial.instance==None:
            FilterSerial.instance = FilterSerial()
        return FilterSerial.instance



class SerialHelper(_DataService):
    def __init__(self, data_service, logger, buffer_name):
        super(SerialHelper, self).__init__()
        self.__data_service = data_service
        self.__logger = logger
        self.buffer_name = buffer_name

    def __filter_utf_8(self, data):
        filter_pattern = r'[^\x00-\x7f]'
        while re.search(filter_pattern, data):
            self.__logger.error('utf-8 is not expected here .....')
            data = re.sub(filter_pattern, '', data)

        return data

    def __filter_dirty_data(self, data):
        if not FilterSerial.get().filter_data_list:
            return data
        for keyword in FilterSerial.get().filter_data_list:
            if keyword in data:
                self.__logger.error("data is corrupted for some reason ....")
                return None
        return data

    def __trim_frame_tail(self, data):
        if not data:
            return data

        index = data.rfind('\33')
        if index != -1:
            self.__logger.debug(
                'trim_frame_tail:[{0}]'.format(data[index:].replace('\33', '\\33')))
            data = data[:index]

        if data:
            index = data.rfind('\33')
            if index != -1:
                # if re.search(r'\33\[[34][0-7]m\33\[[34][0-7]m'.encode('unicode-escape').decode('utf-8'), data[index + 1:]):
                if re.search(r'\\33\[[34][0-7]m\\33\[[34][0-7]m', data[index + 1:]):
                    self.__logger.debug(
                        'trim_frame_tail:[{0}]'.format(data[index:].replace('\33', '\\33')))
                    data = data[:index]

        return data

    def __trim_frame_head(self, data):
        if not data:
            return data

        index = data.find('\33')
        if index not in [0, -1]:
            self.__logger.debug('trim_frame_head:[{0}]'.format(data[:index].replace('\33', '\\33')))
            return data[index:]

        return data

    def read_frame(self, timeout, heartbeats, max_size):
        recv_data_list = []
        recv_data = ""
        total_len = 0
        dt = datetime.datetime.now()
        sep = None

        while (datetime.datetime.now() - dt).seconds < timeout:
            data = self.__data_service.read_from(buffer_name=self.buffer_name)
            if data:
                sep = time.time()
                recv_data_list.append(data)
                total_len += len(data)
                if total_len > max_size:
                    recv_data = self.__trim_frame_tail("".join(recv_data_list))
                    recv_data = self.__trim_frame_head(recv_data)
                    self.__logger.debug('larger package %d' % total_len)
                    break
            else:
                if sep and (time.time() - sep) > heartbeats:
                    recv_data = "".join(recv_data_list)
                    break
        if not recv_data:
            recv_data = "".join(recv_data_list)
        recv_data = self.__filter_utf_8(recv_data)
        return self.__filter_dirty_data(recv_data)

    def read_until(self, pattern, timeout):
        """

        :param pattern: if pattern is set, func will be return if pattern is find in output string else will be wait timeout
        :param timeout:
        :return:
        """
        recv_data = ''
        dt = datetime.datetime.now()
        while (datetime.datetime.now() - dt).seconds < timeout:
            data = self.__slower_read(0.3)
            if data:
                data = data.replace('\33', '\\33')
                recv_data += data

            if pattern and re.search(pattern, recv_data):
                break

        return recv_data

    def __slower_read(self, timeout):
        dt = time.time()
        recv_data = ''
        while (time.time() - dt) < timeout:
            data = self.__data_service.read_from(buffer_name=self.buffer_name)

            if data:
                recv_data += data
        return recv_data

    def read(self):
        return self.__data_service.read_from(buffer_name=self.buffer_name)

    def write(self, data):
        self.__data_service.write(data)

    def clean_buffer(self):
        self.__data_service.clean_buffer(buffer_name=self.buffer_name)