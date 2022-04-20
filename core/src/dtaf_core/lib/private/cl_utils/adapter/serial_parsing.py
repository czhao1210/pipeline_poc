import re
import time

from dtaf_core.lib.private.cl_utils.adapter.data_types import RET_ENV_FAIL, \
    RET_INVALID_INPUT, RET_SUCCESS, RET_TEST_FAIL, ReturnData
from dtaf_core.lib.private.cl_utils.adapter.private.pyte_interface.gernal_pyte_api import GernalPYTE


class SerialParsingDataAdapter(object):
    def __init__(self, data_helper, screen_height, screen_width, cfg):
        self.__data_helper = data_helper
        self.__pyte = GernalPYTE(screen_width, screen_height)
        self.__screen_height = screen_height
        self.__screen_width = screen_width
        self.__cfg = cfg

    def wait_for_text_pattern(self, text_pattern, timeout):
        try:
            base_time = time.time()
            while (time.time() - base_time) < timeout:
                data = self.__data_helper.read()
                if data:
                    try:
                        self.__pyte.feed(data)
                    except Exception as ex:
                        print('feed error !!!! {0}'.format(ex))

                display = self.__pyte.get_screen_display()
                if text_pattern and re.search(text_pattern, '\n'.join(display)):
                    return RET_SUCCESS

            if not text_pattern:
                return RET_SUCCESS

            return RET_TEST_FAIL
        except Exception as ex:
            print("wait_for_text_pattern, return {0} ex={1}".format(RET_ENV_FAIL, ex))
            return RET_ENV_FAIL

    def press_key(self, key_code):
        try:
            self.__data_helper.write(key_code)
            time.sleep(1)
            return RET_SUCCESS
        except Exception as ex:
            print("press_key, return {0} ex={1}".format(RET_ENV_FAIL, ex))
            return RET_ENV_FAIL

    def input_text(self, text, time_sep):
        if not text:
            print('text is NULL [{0}]'.format(text))
            return RET_INVALID_INPUT

        if not time_sep:
            time_sep = 1

        try:
            for c in text:
                self.__data_helper.write(c)
                base_time = time.time()
                flag = False
                while (time.time() - base_time) < time_sep:
                    data = self.__data_helper.read()
                    if data:
                        self.__pyte.feed(data)

                    display = self.__pyte.get_screen_display()
                    if re.search(r'[\s\S]+', '\n'.join(display)) and c in data:
                        flag = True
                        break

                if not flag:
                    return RET_TEST_FAIL

            return RET_SUCCESS
        except Exception as ex:
            print("input_text, return {0} ex={1}".format(RET_ENV_FAIL, ex))
            return RET_ENV_FAIL

    def get_screen(self):
        try:
            display = self.__pyte.get_screen_display()
            cursor = self.__pyte.get_cursor()
            if not cursor:
                return ReturnData(RET_SUCCESS, (display, None, None))
            else:
                return ReturnData(RET_SUCCESS, (display, (cursor.x, cursor.y), display[cursor.y]))
        except Exception as ex:
            print("get_screen, return {0} ex={1}".format(RET_ENV_FAIL, ex))
            return  ReturnData(RET_ENV_FAIL, None)

    def get_highlighted_items(self, colors, area):
        try:
            if not colors:
                print('color is not define')
                return ReturnData(RET_INVALID_INPUT, None)

            if not area:
                area = [0, 0, self.__screen_height, self.__screen_width]

            text = self.__pyte.get_text(colors, area)
            if not text:
                return ReturnData(RET_TEST_FAIL, None)

            return ReturnData(RET_SUCCESS, text)
        except Exception as ex:
            print("get_highlighted_items return {0} ex={1}".format(RET_ENV_FAIL, ex))
            return ReturnData(RET_ENV_FAIL, None)

