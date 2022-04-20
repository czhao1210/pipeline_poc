"""
bios menu helper relies on pyte to parse serial data to construct bios menu.
It follows VT100 protocal. It provides below APIs
parse
get_highlight
get_selected_item
get_items
get_bound
get_title
get_resolution
set_resolution
LOC:800
"""

import datetime
import re
from time import sleep

from dtaf_core.lib.private.cl_utils.adapter.data_types import RET_INVALID_INPUT, RET_SUCCESS, \
    RET_ENV_FAIL, RET_TEST_FAIL
from dtaf_core.lib.private.cl_utils.adapter.data_types import ReturnData
from dtaf_core.lib.private.cl_utils.adapter.private.pyte_interface.pyte_api import PyteAPI


class BiosMenuHelper(object):
    """
    interact with bios menu and provide the basic APIs
    """
    DEFAULT_BOUNDARY = [(80, 24), (100, 31)]
    RECEIVE_FLAG = '\33[19;80H'

    def __init__(self, width, height, bios_menu_type, data_helper, cfg, logger):
        """
        initiate an instance of bios_menu_parser with a specific resolution
        bound and highlight color scheme will be configured based on the menu type
        :param width: the max width of bios menu
        :param height: the height of bios menu
        :param bios_menu_type: support (BIOS_SETUP_MENU_TYPE and BIOS_BOOT_MENU_TYPE)
        """
        self.__logger = logger
        self.__logger.debug(
            "SetupMenuHelper width = {0}, height = {1}".format(width, height))

        if (width, height) not in BiosMenuHelper.DEFAULT_BOUNDARY:
            raise Exception(
                "resolution with {0} height {1} error".format(width, height))

        self.__py_api = PyteAPI(
            width=width, height=height, bios_menu_type=bios_menu_type, resolution_config=cfg['resolution_config'],
            logger=self.__logger)
        self.__init_data()
        self.__received_data_repeat = (5, BiosMenuHelper.RECEIVE_FLAG)  # (count, repeat data)
        self.__data_helper = data_helper
        self.__parsed = False
        self.__cap = None
        self.__is_captured = False
        self.__screen_info = {}

    def clean_pyte(self):
        try:
            self.__init_data()
            self.__py_api.reset_screen()
            return RET_SUCCESS
        except Exception as ex:
            self.__logger.error("error in clean_pyte {0}".format(ex))
            return RET_ENV_FAIL

    def parse(self, timeout, is_popup=False):
        """
        parse serial data to construct bios menu in graphics
        It follows VT100 protocol.
        :param heartbeats: the max interval between two bios menu data.
        If bios menu data comes after heartbeats drains, it returns
        :param timeout:the max time to wait for the return of this API
        :return:
                RET_SUCCESS         -   heartbeats drains without no error.
                                        For those pages which continuously outputs serial data
                                        (e.g. system information page).
                                        It returns after receiving 5 duplicated data
                RET_TEST_FAIL       -   no bios menu data received within timeout
                RET_ENV_FAIL        -   any exception (e.g. serial exception)
                RET_INVALID_INPUT   -   heartbeats or timeout is negative number
        dependencies:
            g_main_serial_service.read
            pyte
        equivalent classes:
        valid: (heartbeats, timeout) - (0,infinite),(0,infinite),
        g_main_serial_service.read - (bios menu data without title info), (bios emnu data with title info), (bios popup dialog data),
            pyte - bios menu matrix from pyte
            invalid:
            (heartbeats, timeout) - (negative infinite, 0] or (negative infinite, 0]
            g_main_serial_service.read - empty
            pyte - empty matrix from pyte
        LOC: 100
        """
        self.__logger.debug(
            "parse timeout={0}".format(timeout))
        ret = RET_TEST_FAIL

        try:
            if timeout < 0:
                self.__logger.error("return: {0}".format(RET_INVALID_INPUT))
                return RET_INVALID_INPUT

            self.__init_data()
            if self.__receive_lines(timeout=timeout):
                self.__py_api.show_screen()
                if is_popup:
                    ret_code, ret_info = self.__py_api.parse_popup()
                else:
                    ret_code, ret_info = self.__py_api.parse_screen()

                self.__screen_info = ret_info
                if ret_code and ret_info["items"]:
                    self.__parsed = True

            if self.__parsed:
                ret = RET_SUCCESS
            else:
                ret = RET_TEST_FAIL

        except Exception as ex:
            self.__logger.error(
                "return: {0}, ex={1}%s".format(RET_ENV_FAIL, ex))
            self.__parsed = False
            ret = RET_ENV_FAIL

        self.__logger.debug("return: {0}".format(ret))
        return ret

    def wait_for_popup_highlight(self, timeout, item_name, use_regex):
        """
            This API is used to performance of parsing
            parse serial data to look for the specific bios item.
            It returns when a highlighted item is parsed or heartbeats drains or timeout reached.
            If the highlighted item is not the item_name, return value will be False.
            It follows VT100 protocol.
            :param heartbeats: the max interval between two bios menu data.
            If bios menu data comes after heartbeats drains, it returns
            :param timeout: the max time to wait for the return of this API
            :param item_name: the specific item name to parse
            :param use_regex: indicates whether to use regular expression.
            If True, item_name is a regex pattern
            :return:    Return Data Object
                return code:
                    RET_SUCCESS         -   heartbeats drains without no error.
                                            For those pages which continuously outputs serial data
                                            (e.g. system information page).
                                            It returns after receiving 5 duplicated data
                    RET_TEST_FAIL       -   no bios menu data received within timeout
                    RET_ENV_FAIL        -   any exception (e.g. serial exception)
                    RET_INVALID_INPUT   -   heartbeats or timeout is negative number
                return value:
                    True    -   the specific item is found
                    False   -   no found
            dependencies:
                g_main_serial_service.read
                pyte
            equivalent classes:
                valid: (heartbeats, timeout) - (0,infinite),(0,infinite),
                g_main_serial_service.read - (bios menu data without title info), (bios emnu data with title info), (bios popup dialog data),
                pyte - bios menu matrix from pyte
                item name - string type indicates an item on bios menu
                use_regex - True / False
                invalid:
                (heartbeats, timeout) - (negative infinite, 0] or (negative infinite, 0]
                g_main_serial_service.read - empty
                pyte - empty matrix from pyte
                item name - not a string
                use_regex - non-boolean type
            """
        try:
            self.__logger.debug(
                "wait_for_popup_highlight: timeout={0}, item_name={1}, use_regex={2}".format(
                    timeout, item_name, use_regex))
            if timeout < 0 or item_name is None or use_regex is None:
                return ReturnData(RET_INVALID_INPUT, False)
            ret_code, ret_info = self.__py_api.parse_popup()
            old_highlight = None
            if ret_code and ret_info["full"] and ret_info["highlight"][0]:
                old_highlight = ret_info["highlight"][1]

            prev_highlight = old_highlight
            highlight_changed = False
            prev_time = datetime.datetime.now()
            while (datetime.datetime.now() - prev_time).seconds < timeout:
                c_time = datetime.datetime.now() - prev_time
                frame_data = self.__data_helper.read_frame(min(3, timeout - c_time.seconds),
                                                           0.8, 1024 * 12)
                if not frame_data:
                    if highlight_changed:
                        break
                    else:
                        self.__logger.debug('NODATA READ [{0}.{1}]'.format(c_time.seconds, c_time.microseconds))
                        sleep(1)
                        continue
                self.__logger.debug('DATA READ [{0}.{1}] len = {2}'.format(
                    c_time.seconds, c_time.microseconds, len(frame_data)))

                self.__py_api.feed(frame_data)
                ret_code, ret_info = self.__py_api.parse_popup()
                if not ret_code:
                    sleep(1)
                    continue

                self.__parsed = True
                self.__screen_info = ret_info
                # FIXME: update popup, full, highlight, items.  move to popup info
                self.__screen_info['popup'] = True
                self.__screen_info['items'] = ret_info['items']
                self.__screen_info['highlight'] = ret_info['highlight']
                self.__screen_info['full_popup'] = ret_info['full']
                self.__logger.error("POPUP {0}".format(self.__screen_info))

                if not self.__screen_info["full_popup"]:
                    self.__logger.error("POPUP Screen is [NOT] in popup mode Continue wait...................")
                    sleep(1)
                    continue

                if not self.__screen_info["highlight"][0]:
                    self.__logger.debug("POPUP Highlight is in None Continue wait...................")
                    sleep(1)
                    continue

                if not highlight_changed:
                    if self.__highlight_change(old_highlight, self.__screen_info["highlight"][1]):
                        highlight_changed = True
                    else:
                        if self.__screen_info['items'] and self.__screen_info["highlight"][1][0] \
                                in [self.__screen_info['items'][0][0], self.__screen_info['items'][-1][0]]:
                            break

                    prev_highlight = self.__screen_info["highlight"][1]
                    self.__logger.debug('POPUP highlight changed = {0}'.format(highlight_changed))
                    sleep(0.1)
                    continue
                else:
                    if self.__highlight_change(prev_highlight, self.__screen_info["highlight"][1]):
                        prev_highlight = self.__screen_info["highlight"][1]
                        self.__logger.debug('POPUP highlight in changing')
                        sleep(0.1)
                        continue

                    if not self.__highlight_change(old_highlight, self.__screen_info["highlight"][1]):
                        highlight_changed = False
                        prev_highlight = self.__screen_info["highlight"][1]
                        sleep(0.1)
                        self.__logger.debug('POPUP highlight in not full change')
                        continue
                    else:
                        self.__logger.debug('POPUP highlight break')
                        break

            ret_data = ReturnData(
                RET_SUCCESS,
                self.__check_same_item_name(
                    self.__screen_info['highlight'][1][0],
                    item_name,
                    use_regex
                ))
            self.__logger.debug(
                'WAIT FOR [POPUP] HIGHLIGHT [{0}][{1}]'.format(
                    ret_data.return_code,
                    ret_data.result_value))
            return ret_data
        except Exception as ex:
            self.__logger.error('WAIT FOR [POPUP] HIGHLIGHT error ...{0}'.format(ex))
            ret_data = ReturnData(RET_ENV_FAIL, False)
            return ret_data

    def check_frame(self, data_list):
        search_list = [
            r'^\33\[\?25[lh]',
            r'^\33\[\d+;\d+H',
            r'^\33\[[34][0-7]m',
            r'^\33\[2J',
            r'^\33\[\d+[A-D]',
            r'^\33\[[014578]m',
            r'^\33\[[ksu]'
        ]

        if not data_list:
            return True

        pkg_data = "".join(data_list)
        index = pkg_data.rfind('\33')
        if index == -1:
            return True

        check_data = pkg_data[index:]
        for pat in search_list:
            if re.search(pat, check_data):
                return True

        return False

    def __highlight_change(self, prev_hig, cur_hig):
        try:
            ret = False
            if cur_hig and cur_hig[0] and (not prev_hig or prev_hig != cur_hig):
                ret = True
                # check next_page

            self.__logger.debug(
                '__highlight_change prev_hig[{0}], cur_hig[{1}], flag[{2}]'.format(
                    prev_hig, cur_hig, ret))
            return ret
        except Exception as ex:
            self.__logger.error('__highlight_change ex {0}'.format(ex))
            raise Exception(ex)

    def __check_same_item_name(self, hl_item_name, item_name, use_regex):
        try:
            ret = False
            if item_name:
                if use_regex:
                    self.__logger.debug('1 check same name {}<=>{}'.format(item_name, hl_item_name))
                    if re.search(item_name, hl_item_name):
                        ret = True
                else:

                    self.__logger.debug('2 check same name {}'.format(item_name))
                    if 0 == hl_item_name.find(item_name):
                        ret = True

            self.__logger.debug(
                '__check_same_item_name hl_item_name=[{0}], item_name=[{1}], return[{2}]'.format(
                    hl_item_name, item_name, ret))
            return ret
        except Exception as ex:
            self.__logger.error('__check_same_item_name ex {0}'.format(ex))
            raise Exception(ex)

    def wait_for_highlight(self, timeout, item_name, use_regex):
        """
            This API is used to performance of parsing
            parse serial data to look for the specific bios item.
            It returns when a highlighted item is parsed or heartbeats drains or timeout reached.
            If the highlighted item is not the item_name, return value will be False.
            It follows VT100 protocol.
            :param heartbeats: the max interval between two bios menu data.
            If bios menu data comes after heartbeats drains, it returns
            :param timeout: the max time to wait for the return of this API
            :param item_name: the specific item name to parse
            :param use_regex: indicates whether to use regular expression.
            If True, item_name is a regex pattern
            :return:    Return Data Object
                return code:
                    RET_SUCCESS         -   heartbeats drains without no error.
                                            For those pages which continuously outputs serial data
                                            (e.g. system information page).
                                            It returns after receiving 5 duplicated data
                    RET_TEST_FAIL       -   no bios menu data received within timeout
                    RET_ENV_FAIL        -   any exception (e.g. serial exception)
                    RET_INVALID_INPUT   -   heartbeats or timeout is negative number
                return value:
                    True    -   the specific item is found
                    False   -   no found
            dependencies:
                g_main_serial_service.read
                pyte
            equivalent classes:
                valid: (heartbeats, timeout) - (0,infinite),(0,infinite),
                g_main_serial_service.read - (bios menu data without title info), (bios emnu data with title info), (bios popup dialog data),
                pyte - bios menu matrix from pyte
                item name - string type indicates an item on bios menu
                use_regex - True / False
                invalid:
                (heartbeats, timeout) - (negative infinite, 0] or (negative infinite, 0]
                g_main_serial_service.read - empty
                pyte - empty matrix from pyte
                item name - not a string
                use_regex - non-boolean type
            """
        try:
            self.__logger.debug(
                "wait_for_highlight: timeout={0}, item_name={1}, use_regex={2}".format(
                    timeout, item_name, use_regex))
            if timeout < 0 or use_regex is None or item_name is None:
                return ReturnData(RET_INVALID_INPUT, False)

            ret_code, ret_info = self.__py_api.parse_screen()
            old_highlight = None
            if ret_code and not ret_info["popup"] and ret_info["highlight"][0]:
                old_highlight = ret_info["highlight"][1]

            prev_highlight = old_highlight
            highlight_changed = False
            prev_time = datetime.datetime.now()
            while (datetime.datetime.now() - prev_time).seconds < timeout:
                c_time = datetime.datetime.now() - prev_time
                frame_data = self.__data_helper.read_frame(min(timeout - c_time.seconds, 3),
                                                           0.8, 1024 * 128)
                if not frame_data:
                    if highlight_changed:
                        break
                    else:
                        self.__logger.debug('NODATA READ [{0}.{1}]'.format(c_time.seconds, c_time.microseconds))
                        sleep(1)
                        continue

                self.__logger.debug('DATA READ [{0}.{1}] len = {2}'.format(
                    c_time.seconds, c_time.microseconds, len(frame_data)))

                self.__py_api.feed(frame_data)
                ret_code, ret_info = self.__py_api.parse_screen()
                if not ret_code:
                    sleep(1)
                    continue

                self.__parsed = True
                self.__screen_info = ret_info
                if self.__screen_info["popup"]:
                    self.__logger.error("Screen is in popup mode Continue wait...................")
                    sleep(1)
                    continue

                if not self.__screen_info["highlight"][0]:
                    self.__logger.debug("Highlight is in None Continue wait...................")
                    sleep(1)
                    continue

                if not highlight_changed:
                    if self.__highlight_change(old_highlight, self.__screen_info["highlight"][1]):
                        highlight_changed = True

                    prev_highlight = self.__screen_info["highlight"][1]
                    sleep(0.1)
                    continue
                else:
                    if self.__highlight_change(prev_highlight, self.__screen_info["highlight"][1]):
                        prev_highlight = self.__screen_info["highlight"][1]
                        sleep(0.1)
                        continue

                    if not self.__highlight_change(old_highlight, self.__screen_info["highlight"][1]):
                        highlight_changed = False
                        prev_highlight = self.__screen_info["highlight"][1]
                        sleep(0.1)
                        continue
                    else:
                        break
            ret_data = ReturnData(
                RET_SUCCESS,
                self.__check_same_item_name(
                    self.__screen_info['highlight'][1][0],
                    item_name,
                    use_regex
                ))
            self.__logger.debug(
                'WAIT FOR HIGHLIGHT [{0}][{1}]'.format(
                    ret_data.return_code,
                    ret_data.result_value))
            return ret_data
        except Exception as ex:
            self.__logger.error('error ...{0}'.format(ex))
            ret_data = ReturnData(RET_ENV_FAIL, False)
            return ret_data

    def get_screen_info(self):
        try:
            frame_data = self.__data_helper.read_frame(1,
                                                       0.8, 1024 * 12)
            if frame_data:
                self.__py_api.feed(frame_data)

            return ReturnData(RET_SUCCESS, self.__py_api.get_screen_info())
        except Exception as ex:
            self.__logger.error('error ...{0}'.format(ex))
            ret_data = ReturnData(RET_ENV_FAIL, ())
            return ret_data

    def press_key(self, key_code):
        """
        send key code to serial port
        if ignore we will use parse timeout, and heartbeats
        :param key_code: key code to send
        :param ignore: Tree parse data from serial port, False not parse data from serial port
        :param heartbeats: heartbeats between two serail data
        :param timeout: timeout to receive serial data
        :return:
            RET_SUCCESS -   write serial port successfully
            RET_ENV_FAIL    -   exception raised or write serial failed
            RET_INVALID_INPUT   -   key_code is None
        dependencies:
            g_main_serial_service.write
        equivalent classes:
            valid input -
            key_code: Not None
            ignore: True / False
            heartbeats: (0, infinite)
            timeout: [0, infinite).
            invalid input:
            key_code: None
            ignore: not boolean
            heartbeats: (negative infinite, 0)
            timeout: (negative infinite, 0)
        LOC: 100
        """
        self.__logger.debug("press_key key_code={0}".format(key_code))
        try:
            self.__write(key_code)
            return RET_SUCCESS
        except Exception as ex:
            self.__logger.error("press_key ex={0}".format(ex))
            return RET_ENV_FAIL

    def get_highlight(self):
        """
        get the highlighted item on bios menu page
        :return: Return Data Object
            return code:
                RET_SUCCESS         -   the last parsing is sucessful
                RET_TEST_FAIL       -   the last parsing return RET_TEST_FAIL
                or RET_INVALID_INPUT
                RET_ENV_FAIL        -   the last parsing return RET_ENV_FAIL
            return value:
                tuple   -   (item_name, item_value, description)
                ("", "", "")  -   if no item highlighted
        dependency: no
        equivalent class: NA
        LOC: 10
        """
        self.__logger.debug("get_highlight")
        try:
            if self.__parsed:
                self.__logger.debug(
                    "get_highlight: info: {0}".format(self.__screen_info["highlight"]))
                if self.__screen_info["popup"]:
                    ret_data = ReturnData(
                        return_code=RET_SUCCESS,
                        result_value=(self.__screen_info["highlight"][1][0],
                                      self.__screen_info["highlight"][1][1],
                                      self.__screen_info["highlight"][1][2],
                                      ""))

                else:
                    ret_data = ReturnData(
                        return_code=RET_SUCCESS,
                        result_value=(self.__screen_info["highlight"][1][0],
                                      self.__screen_info["highlight"][1][1],
                                      self.__screen_info["highlight"][1][2],
                                      self.__screen_info["description"]))

            else:
                ret_data = ReturnData(
                    return_code=RET_TEST_FAIL, result_value=("", "", "", ""))

            self.__logger.debug(
                "get_highlight: return: {0}{1}".format(
                    ret_data.return_code, ret_data.result_value))
            return ret_data
        except Exception as ex:
            ret_data = ReturnData(return_code=RET_ENV_FAIL, result_value=("", "", "", ""))
            self.__logger.error(
                "get_highlight return: {0} {1}, ex={2}".format(
                    ret_data.return_code, ret_data.result_value, ex))
            return ret_data

    def get_highlight_position(self):
        """
        get the position of highlight

        :return:
            return data
                return code: RET_SUCCESS/RET_TEST_FAIL
                return value: position in format of (x,y, highlighted content)
        """
        self.__logger.debug("get_highlight_position")
        try:
            if self.__parsed:
                ret_data = ReturnData(
                    return_code=RET_SUCCESS,
                    result_value=self.__screen_info["highlight"][1][3])
            else:
                ret_data = ReturnData(return_code=RET_TEST_FAIL, result_value=("", "", ""))
                self.__logger.error("return: {0}".format(ret_data))

            self.__logger.debug(
                "return: {0}, {1}".format(ret_data.return_code, ret_data.result_value))
            return ret_data
        except Exception as ex:
            ret_data = ReturnData(return_code=RET_ENV_FAIL, result_value=("", "", ""))
            self.__logger.error("return: {0}, ex={1}".format(ret_data, ex))
            return ret_data

    def get_items(self):
        """
        get all items on current bios page in the format of (key, value)
        :return: Return Data Object
            return code:
                RET_SUCCESS         -   the last parsing is sucessful
                RET_TEST_FAIL       -   the last parsing return RET_TEST_FAIL
                or RET_INVALID_INPUT
                RET_ENV_FAIL        -   the last parsing return RET_ENV_FAIL
            return value:
                list  -   [(key, value),]
        dependencies:
            parse
        equavilent classes:
            valid: items is dictionary object key and value should be string (e.g. {'Memory','4G'}
            invalid: non-dictionary
        LOC: 20
        """
        self.__logger.debug("get_items")
        try:
            if self.__parsed:
                ret_data = ReturnData(RET_SUCCESS, self.__screen_info["items"])
                self.__logger.debug(
                    "return: {0} {1}".format(ret_data.return_code, ret_data.result_value))
            else:
                ret_data = ReturnData(RET_TEST_FAIL, [])
                self.__logger.debug(
                    "return: {0} {1}".format(ret_data.return_code, ret_data.result_value))

            return ret_data
        except Exception as ex:
            ret_data = ReturnData(RET_ENV_FAIL, [])
            self.__logger.error(
                "return: {0} {1}, ex={1}".format(ret_data.return_code, ret_data.result_value, ex))
            return ret_data

    def is_popup(self):
        self.__logger.debug("get_items")
        try:
            if self.__parsed:
                ret_data = ReturnData(RET_SUCCESS, (self.__screen_info["popup"],
                                                    self.__screen_info["full_popup"]))
                self.__logger.debug(
                    "is_popup return: {0} {1}".format(ret_data.return_code, ret_data.result_value))
            else:
                ret_data = ReturnData(RET_TEST_FAIL, (False, False))
                self.__logger.debug(
                    "is_popup return: {0} {1}".format(ret_data.return_code, ret_data.result_value))

            return ret_data
        except Exception as ex:
            ret_data = ReturnData(RET_ENV_FAIL, (False, False))
            self.__logger.error(
                "return: {0}{1}, ex={2}".format(ret_data.return_code, ret_data.result_value, ex))
            return ret_data

    def get_bound(self):
        """
        get the bound of bios menu.
        indicates an area where all items are selectable
        :return: Return Data Object
            return code:
                RET_SUCCESS         -   the last parsing is sucessful
                RET_TEST_FAIL       -   the last parsing return RET_TEST_FAIL
                or RET_INVALID_INPUT or no bound parsed
                RET_ENV_FAIL        -   the last parsing return RET_ENV_FAIL
            return value:
                tuple  -   (left, top, right, bottom)
        dependencies:
            bios_menu_helper.parse
        equivalent classes:
            bios_menu_helper.parse - RET_SUCCESS, RET_TEST_FAIL, RET_ENV_FAIL, RET_INVALID_INPUT
        LOC: 20
        """
        self.__logger.debug("get_bound")
        try:
            if self.__parsed:
                ret_data = ReturnData(
                    return_code=RET_SUCCESS, result_value=self.__screen_info["bound"])
                self.__logger.debug("return: {0}".format(ret_data))
            else:
                ret_data = ReturnData(
                    return_code=RET_TEST_FAIL, result_value=(None, None, None, None))
                self.__logger.debug("return: {0}".format(ret_data))

            return ret_data
        except Exception as ex:
            ret_data = ReturnData(
                return_code=RET_ENV_FAIL, result_value=(None, None, None, None))
            self.__logger.error("return: {0}, ex={1}".format(ret_data, ex))
            return ret_data

    def get_title(self):
        """
        get the title of bios menu.
        :return: Return Data Object
            return code:
                RET_SUCCESS         -   the last parsing is sucessful
                RET_TEST_FAIL       -   the last parsing return RET_TEST_FAIL
                or RET_INVALID_INPUT or no bound parsed
                RET_ENV_FAIL        -   the last parsing return RET_ENV_FAIL
            return value:
                title   -   string
        dependencies:
            self.__title (from bios_menu_helper.parse)
        equavalent class:
            valid: string (e.g. "" or "Bios Menu")
            invalid: None or Non-string
        LOC: 20
        """
        try:
            if self.__parsed:
                ret_data = ReturnData(
                    return_code=RET_SUCCESS,
                    result_value=self.__screen_info["title"])
            else:
                ret_data = ReturnData(
                    return_code=RET_TEST_FAIL,
                    result_value="")

            self.__logger.debug(
                "return: {0} {1}".format(ret_data.return_code, ret_data.result_value))
            return ret_data
        except Exception as ex:
            ret_data = ReturnData(
                return_code=RET_ENV_FAIL,
                result_value="")
            self.__logger.error(
                "return: {0} {1}, ex={1}".format(ret_data.return_code, ret_data.result_value, ex))
            return ret_data

    def get_resolution(self):
        """
        get the resolution of bios menu.
        :return: Return Data Object
            return code:
                RET_SUCCESS         -   the last parsing is sucessful
                RET_TEST_FAIL       -   the last parsing return RET_TEST_FAIL
                or RET_INVALID_INPUT or no bound parsed
                RET_ENV_FAIL        -   the last parsing return RET_ENV_FAIL
            return value:
                tuple   -   (width, height)
        equavalent class:
            valid: tuple (84,20) or (100,31)
            invalid: any other value
        LOC: 20
        """
        self.__logger.debug("get_resolution")
        try:
            ret_data = ReturnData(RET_SUCCESS, self.__py_api.get_resolution())
            self.__logger.debug("return: {0}".format(ret_data))
            return ret_data
        except Exception as ex:
            ret_data = ReturnData(RET_ENV_FAIL, (-1, -1))
            self.__logger.error("return: {0}, ex={1}".format(ret_data, ex))
            return ret_data

    def set_resolution(self, width, height):
        """
        initiate an instance of bios_menu_parser with a specific resolution
        if resolution is set successfully, bound should be updated automatically
        :param width: the max width of bios menu
        :param height: the height of bios menu
        :return:
                RET_SUCCESS         -   the last parsing is sucessful
                RET_TEST_FAIL       -   the last parsing return RET_TEST_FAIL
                or RET_INVALID_INPUT or no bound parsed
                RET_INVALID_INPUT   -   width or height is invalid input
                (currently only support (80,24) or (100,31))
        equivalent class:
            valid input:    (80,24) or (100,31)
            invalid input: any other input is invalid
        LOC: 50
        """

        self.__logger.debug("set_resolution width={0}, height={1}".format(width, height))
        if (width, height) not in BiosMenuHelper.DEFAULT_BOUNDARY:
            self.__logger.error("return: {0}".format(RET_INVALID_INPUT))
            return RET_INVALID_INPUT

        try:
            self.__py_api.set_resolution(width=width, height=height)
            self.__init_data()
            self.__logger.debug("return: {0}".format(RET_SUCCESS))

            return RET_SUCCESS
        except Exception as ex:
            self.__logger.error("return: {0}, ex={1}".format(RET_ENV_FAIL, ex))
            return RET_ENV_FAIL

    def __init_data(self):
        """
        init some common data
        :return:
        """
        self.__parsed = False
        self.__screen_info = {
            "title": "",
            "highlight": (False, ("", "", "", (None, None, None))),
            "bound": (0xFFFF, 0xFFFF, 0, 0),
            "description": "",
            "popup": False,
            "items": [],
            "full": False
        }

    def __receive_lines(self, timeout):
        """
        parse function call this function to read data from serial read queue,
        read full data and return
        :param heartbeats:
        :param timeout:
        :return: length of received data
        """
        try:
            self.__logger.debug("__receive_data")
            prev_time = datetime.datetime.now()
            rcv_data = ""

            while (datetime.datetime.now() - prev_time).seconds < timeout:
                cur_rcv_data = self.__data_helper.read()
                if cur_rcv_data:
                    self.__logger.debug(
                        "TIMEOUT:[%d][%s]" % ((datetime.datetime.now() - prev_time).seconds,
                                              cur_rcv_data.replace("\33", "\\33")))
                    rcv_data = "".join([rcv_data, cur_rcv_data])
                    self.__py_api.feed(cur_rcv_data)
                else:
                    sleep(1)
                    continue

            self.__logger.debug(
                "__receive_data return len({0}), data[{1}]".format(
                    len(rcv_data),
                    rcv_data.replace("\33", "\\33")))
            return len(rcv_data)
        except Exception as ex:
            self.__logger.error("__receive_data ex={0}".format(ex))
            raise Exception(ex)

    def __check_highlight_change(self, prev_hig, cur_hig):
        self.__logger.debug('__check_highlight_change')
        try:
            if not cur_hig[0]:
                return False

            if prev_hig == cur_hig:
                return False

            if prev_hig:
                pat = re.compile('^%s' % cur_hig[0])
                if prev_hig[0] and cur_hig[3][0] == prev_hig[3][0] and pat.search(prev_hig[0]):
                    return False

            if cur_hig[0]:
                return True
            else:
                return False
        except Exception as ex:
            self.__logger.debug('ex {0}'.format(ex))
            raise Exception(ex)

    def __check_value(self, data, name, use_regex):
        """
        check data equal to name or regex data, name
        :param data:
        :param name:
        :param use_regex:
        :return: True equal, False not equal
        """
        self.__logger.debug(
            "__check_value data={0}, name={1}, use_regex={2}".format(data, name, use_regex))
        ret = False
        try:
            if use_regex:
                pat = re.compile(name)
                if pat.search(data):
                    ret = True
            else:
                if data and name and data == name:
                    ret = True

            self.__logger.debug("__check_value return {0}".format(ret))
            return ret
        except Exception as ex:
            self.__logger.error("__check_value ex={0}".format(ex))
            raise Exception(ex)

    def __write(self, key_code):
        """
        write data to serial port
        :param key_code:  wanted write to serial
        :return:
        """
        try:
            self.__data_helper.write(key_code)
        except Exception as ex:
            self.__logger.error("__write ex={0}".format(ex))
            raise Exception(ex)

    def __check_repeat(self, data):
        """
        check repeat data not larger to count
        :param data:
        :return: True is larger to count, False
        """
        self.__logger.debug("__check_repeat")
        try:
            pos = 0
            count = 0
            while True:
                self.__logger.debug("repeat count = %d" % count)
                cur_pos = data[pos:].find(self.__received_data_repeat[1])
                if cur_pos > -1:
                    pos += (cur_pos + len(self.__received_data_repeat[1]))
                    count += 1
                else:
                    break

                if count >= self.__received_data_repeat[0]:
                    self.__logger.debug("__check_repeat return True")
                    return True

            self.__logger.debug("__check_repeat return False")
            return False
        except Exception as ex:
            self.__logger.debug("__check_repeat ex={0}".format(ex))
            raise Exception(ex)
