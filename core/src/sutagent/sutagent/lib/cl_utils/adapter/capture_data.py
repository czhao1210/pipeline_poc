
import re
import time
from sutagent.lib.private.log_logger import sparklogger
import threading
from sutagent.lib.cl_utils.adapter.data_types import RET_SUCCESS, RET_ENV_FAIL, RET_TEST_FAIL


def performance(f):
    def fn(*args, **kw):
        t_start = time.time()
        r = f(*args, **kw)
        t_end = time.time()
        return r

    return fn


class OutputCapture(object):
    def __init__(self, capture_list):
        self.__lock = threading.Lock()
        self.__buffer = ''
        self.__capture_list = capture_list
        self.__check_result = []
        self.__return_on_detection = False

    @performance
    def feed(self, cur_data):
        try:
            self.__lock.acquire()
            check_max_len = 1024 * 4
            check_list = self.__capture_list

            if check_list:
                length = len(self.__buffer)
                c_len = len(cur_data)
                if check_max_len < length + c_len:
                    self.__buffer = self.__buffer[check_max_len + c_len - length:] + cur_data
                else:
                    self.__buffer += cur_data

                for check_str, use_regex, return_on_dec in check_list:
                    if use_regex:
                        ret = self.__match_string(check_str)
                        if ret and return_on_dec:
                            self.__return_on_detection = True
                    else:
                        if self.__buffer.find(check_str) != -1:
                            if check_str not in self.__check_result:
                                self.__check_result.append(self.__buffer)

                            if return_on_dec:
                                self.__return_on_detection = True

        finally:
            self.__lock.release()
            return

    def __match_string(self, check_string):
        s_pos = 0
        flag = False
        while True:
            reg = re.search(check_string, self.__buffer, s_pos)
            if not reg:
                break

            flag = True
            find_str = self.__buffer[reg.regs[0][0]:reg.regs[0][1]]
            if find_str not in self.__check_result:
                self.__check_result.append(find_str)

            s_pos += reg.regs[0][1]

        return flag

    def clean(self):
        ret = RET_TEST_FAIL
        try:
            self.__lock.acquire()
            self.__capture_list = None
            self.__check_result = []
            self.__return_on_detection = False
            self.__buffer = ''

            ret = RET_SUCCESS
        except Exception as ex:
            sparklogger.error('clean error from {0}'.format(ex))
            self.__capture_list = None
            ret = RET_ENV_FAIL
        finally:
            self.__lock.release()
            return ret

    def return_on_detection(self):
        ret = False
        try:
            self.__lock.acquire()
            ret = self.__return_on_detection
        finally:
            self.__lock.release()
            return ret

    def get_result(self):
        ret = ([], False)
        try:
            self.__lock.acquire()
            ret = (self.__check_result,
                   self.__return_on_detection)
        finally:
            self.__lock.release()
            return ret
