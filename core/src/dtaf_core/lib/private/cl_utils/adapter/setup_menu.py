"""
Define Data Layer to parse bios data
LOC: 800
"""
import datetime
import json
import re

from dtaf_core.lib.private.cl_utils.adapter.data_types import RET_TEST_FAIL, RET_SUCCESS, \
    RET_INVALID_INPUT, RET_ENV_FAIL, \
    BIOS_SETUP_MENU_TYPE, ReturnData, BIOS_CMD_KEY_ENTER, BIOS_CMD_KEY_DOWN, \
    BIOS_CMD_KEY_ESC, BIOS_CMD_KEY_PLUS, \
    BIOS_CMD_KEY_UP, \
    BIOS_UI_OPT_TYPE, TimeoutConfig


class BiosSetupMenuDataAdapter(object):
    """
    Bios Setup Menu related Datalayer API
    """

    def __init__(self, data_helper, screen_high, screen_width, timeout_config, cfg, logger):
        self.__logger = logger
        self.__data_helper = data_helper
        from dtaf_core.lib.private.cl_utils.adapter.private.bios_menu_helper import BiosMenuHelper
        self.__setup_menu_helper = BiosMenuHelper(screen_width, screen_high,
                                                  BIOS_SETUP_MENU_TYPE, self.__data_helper, cfg, self.__logger)
        self.__logger.debug(self.__setup_menu_helper)
        self.__timeout_config = timeout_config
        self.__cfg = cfg
        self.__logger.debug("BIOS SETUP MENU RESOLUTION: with: %d, high %d" % (screen_width, screen_high))

    @property
    def timeout_config(self):
        return self.__timeout_config

    @timeout_config.setter
    def timeout_config(self, v):
        self.__timeout_config = v

    def get_current_screen_info(self):
        return self.__setup_menu_helper.get_screen_info()

    def select(self, item_name, item_type, use_regex, timeout):
        """
        select an item on bios menu page
        :param item_name: item name to select
        :param item_type: item type (None, BIOS_UI_OPT_TYPE, BIOS_UI_DIR_TYPE, BIOS_UI_INPUT_TYPE)
        :param use_regex: whether to use regress expression to match the item (True / False)
        :param timeout: the overall timeout to receive the first data
        :return:
            RET_SUCCESS:    the target item is selected
            RET_TEST_FAIL:  item can not be found
            RET_ENV_FAIL:   any exception
            RET_INVALID_INPUT:  input parameter is not valid (data type is not correct)
        dependencies:
            bios_menu_helper.press_key
            bios_menu_helper.parse
        equivalent classes:
            valid:
                item_name (item_name on bios menu, item name which can not be found on  bios menu, non-string)
                item_type (BIOS_UI_OPT_TYPE, BIOS_UI_DIR_TYPE, BIOS_UI_INPUT_TYPE, None)
                use_regex (True, False)
                bios_menu_helper.press key return: (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
                bios_menu_helper.parse return: (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
            invalid:
                item name (Non-string)
                item type (None-string, String value out out of BIOS_UI_OPT_TYPE, BIOS_UI_DIR_TYPE, BUID_UI_INPUT_TYPE)
                use_regex: Non-boolean
                press key return: value of out defined Return value
                parse return: value of out defined Return value
        LOC: 50
        """
        try:
            self.__logger.debug("elementName={0}, type={1}, regex={2}".format(
                item_name, item_type, use_regex))
            if not item_name or use_regex is None or timeout is None or timeout < 0:
                return RET_INVALID_INPUT

            if not self.__highlight_element(
                    item_name=item_name, item_type=item_name, use_regex=use_regex,
                    timeout=timeout):
                self.__logger.error(
                    "__highlight_element return = {0}".format(
                        RET_TEST_FAIL))
                return RET_TEST_FAIL

            return_value = RET_TEST_FAIL
            ret = self.__setup_menu_helper.get_highlight()
            selName = ret.result_value[0]
            selType = ret.result_value[2]
            self.__logger.debug([selName, selType])

            if use_regex and re.search(item_name, selName) is not None and item_type is None:
                return_value = RET_SUCCESS
            elif use_regex and re.search(item_name, selName) is not \
                    None and item_type is not None and item_type == selType:
                return_value = RET_SUCCESS
            elif not use_regex and item_type and item_type == selType and selName == item_name:
                return_value = RET_SUCCESS
            elif not use_regex and not item_type and selName == item_name:
                return_value = RET_SUCCESS

            self.__logger.debug("return {0}".format(return_value))
            return return_value
        except Exception as ex:
            self.__logger.error(r'select %s' % item_name)
            self.__logger.debug("return {0} ex={1}".format(RET_ENV_FAIL, ex))
            return RET_ENV_FAIL

    def goto(self, path, use_regex, timeout_config, is_page_info):
        """
        goto the bios menu page specified in path:
        transverse the folder name in path, move highlight to that directory and press key to enter bios menu
        :param path: the path to the target bios menu page. all the directry names in path are stored in this list
            each element in list are stored as string
        :param use_regex: indicate whether to use regular expression
        :param timeout_config:
            timeout for internal operation inside bios menu
            timeout for nagivating (enter or exit bios menu page)
        :return:
            RET_SUCCESS:    reach the target bios menu page
            RET_TEST_FAIL:  the path is not accessible
            RET_ENV_FAIL:   any exception
            RET_INVALID_INPUT:  input parameter is not valid (data type is not correct)
        dependencies:
            bios_menu_helper.press_key
            bios_menu_helper.parse
            bios_menu_helper.wait_for_highlight
        equivalent classes:
            valid:
                item_name (item_name on bios menu, item name which can not be found on  bios menu, non-string)
                item_type (BIOS_UI_OPT_TYPE, BIOS_UI_DIR_TYPE, BIOS_UI_INPUT_TYPE, None)
                use_regex (True, False)
                bios_menu_helper.press key return:
                (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
                bios_menu_helper.parse return:
                (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
                bios_menu_helper.wait_for_highlight return:
                (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
                timeout_config:
                    internal_timeout:    [0, infinite)
                    navigation_timeout:    [0, infinite)
            invalid:
                item name (Non-string)
                item type (None-string, String value out out of BIOS_UI_OPT_TYPE, BIOS_UI_DIR_TYPE, BUID_UI_INPUT_TYPE)
                use_regex: Non-boolean
                press key return: value of out defined Return value
                bios_menu_helper.parse return: value of out defined Return value
                bios_menu_helper.wait_for_highlight return: value of out defined Return value
                timeout_config:
                    internal_timeout:    (negative infinite, 0)
                    navigation_timeout:    (negative infinite, 0)
        LOC: 50

        """
        try:
            self.__logger.debug(
                "goto path={0}, use_regex={1}, timeout_config={2}, is_page_info{3}".format(
                    path, use_regex, timeout_config, is_page_info))
            if (path and not isinstance(path, list)) or use_regex is None or not timeout_config or \
                    not isinstance(timeout_config, TimeoutConfig) or is_page_info is None:
                self.__logger.error("return {0} bad arguments".format(RET_INVALID_INPUT))
                return RET_INVALID_INPUT

            if path:
                for x in path:
                    if not isinstance(x, tuple) or len(x) != 2:
                        self.__logger.error("return {0} bad path".format(RET_INVALID_INPUT))
                        return RET_INVALID_INPUT
            if not path:
                return RET_SUCCESS

            if len(path) >= 2:
                for index, tmp_path in enumerate(path[:-1]):
                    if self.__highlight_element(
                            item_name=tmp_path[0],
                            item_type=tmp_path[1],
                            use_regex=use_regex,
                            timeout=timeout_config.inner_move_timeout):
                        self.__logger.debug(
                            "GOTo Page====>Highlight Page enter item [{0}] OK".format(
                                tmp_path[0]))

                        ret = self.__setup_menu_helper.press_key(BIOS_CMD_KEY_ENTER)
                        self.__logger.debug(
                            "GOTo Page ====>name [{0}] {1}".format(tmp_path[0], ret))
                        if ret != RET_SUCCESS:
                            raise Exception(
                                "GOTo Page ====>name [{0}] {1} error".format(
                                    tmp_path[0], ret))
                        ret = self.__setup_menu_helper.wait_for_highlight(
                            item_name="",
                            use_regex=use_regex,
                            timeout=timeout_config.navigation_timeout)
                        if ret.return_code != RET_SUCCESS:
                            return ret.return_code
                    else:
                        return RET_TEST_FAIL

            if self.__highlight_element(
                    item_name=path[-1][0], item_type=path[-1][1],
                    use_regex=use_regex, timeout=timeout_config.inner_move_timeout):
                self.__logger.debug(
                    "GOTo Page====>Highlight Page enter item [{0}] OK".format(path[-1][0]))

                ret = self.__setup_menu_helper.press_key(BIOS_CMD_KEY_ENTER)
                if ret != RET_SUCCESS:
                    return ret
                if is_page_info:
                    return self.__setup_menu_helper.parse(
                        timeout=timeout_config.navigation_timeout)
                else:
                    return self.__setup_menu_helper.wait_for_highlight(
                        timeout=timeout_config.navigation_timeout,
                        item_name="",
                        use_regex=False).return_code
            else:
                return RET_TEST_FAIL
        except Exception as ex:
            self.__logger.error("error return {0}, ex={1}".format(
                RET_ENV_FAIL, ex
            ))
            return RET_ENV_FAIL

    def back_to_root(self, timeout, is_page_info):
        """
        press esc key to go back to the root bios page
        :param timeout: timeout to get first data
        :param is_page_info: use to get_page_info
        :return:
            RET_SUCCESS:    reach the root menu page
            RET_TEST_FAIL:  can not go back to root menu page
            RET_ENV_FAIL:   any exception
            RET_INVALID_INPUT:  input parameter is not valid (data type is not correct)
        dependencies:
            bios_menu_helper.press_key
            bios_menu_helper.parse
            bios_menu_helper.get_title
        equivalent classes:
            valid:
                item_name (item_name on bios menu, item name which can not be found on  bios menu, non-string)
                item_type (BIOS_UI_OPT_TYPE, BIOS_UI_DIR_TYPE, BIOS_UI_INPUT_TYPE, None)
                use_regex (True, False)
                bios_menu_helper.press key return: (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
                bios_menu_helper.parse return: (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
                bios_menu_helper.get_title return: title of bios menu in string format
            invalid:
                item name (Non-string)
                item type (None-string, String value out out of BIOS_UI_OPT_TYPE, BIOS_UI_DIR_TYPE, BUID_UI_INPUT_TYPE)
                use_regex: Non-boolean
                press key return: value of out defined Return value
                parse return: value of out defined Return value
                bios_menu_helper.get_title return: None or other non-string type
        LOC: 50
        """
        try:
            self.__logger.debug(
                "back_to_root timeout={0}, is_page_info={1}".format(timeout, is_page_info))
            if timeout is None or timeout < 0 or is_page_info is None:
                return RET_INVALID_INPUT

            max_try_esc = 3
            cur_try = 0
            prev_title = ""
            while cur_try < max_try_esc:
                ret = self.__setup_menu_helper.press_key(BIOS_CMD_KEY_ESC)
                if ret != RET_SUCCESS:
                    return ret

                prev_time = datetime.datetime.now()
                if is_page_info:
                    ret = self.__setup_menu_helper.parse(timeout=timeout)
                    if RET_SUCCESS != ret:
                        return ret
                else:
                    ret = self.__setup_menu_helper.wait_for_highlight(
                        timeout, "", False)
                    try:
                        ret = self.__setup_menu_helper.wait_for_highlight(
                            timeout, "back_to_root", False)

                    except Exception as ex:
                        self.__logger.error(ex)
                    if RET_SUCCESS != ret.return_code:
                        return ret.return_code

                cur_time = datetime.datetime.now()

                ret = self.__setup_menu_helper.is_popup()
                if ret.return_code == RET_SUCCESS and ret.result_value[0]:
                    self.__logger.error("back_to_root into popup mode......")

                ret_info = self.__setup_menu_helper.get_title()
                self.__logger.debug(
                    "BACKToRoot===>CUR_TRY = [{0}], return code [{1}], title [{2}]".format(
                        cur_try,
                        ret_info.return_code,
                        ret_info.result_value))

                if ret_info.return_code == RET_SUCCESS and \
                        ret_info.result_value != prev_title:
                    prev_title = ret_info.result_value
                    cur_try = 0
                else:
                    cur_try += 1

                if ret_info.return_code == RET_SUCCESS and \
                        (cur_time - prev_time).seconds >= \
                        timeout and not is_page_info and not ret_info.result_value and cur_try > 1:
                    self.__logger.debug("BACKToRoot===>return {0}".format(RET_SUCCESS))
                    return RET_SUCCESS

            self.__logger.debug("BACKToRoot===>return {0}".format(RET_SUCCESS))
            return RET_SUCCESS
        except Exception as ex:
            self.__logger.error(
                "BACKToRoot===> return {0} ex=[{1}]".format(RET_ENV_FAIL, ex))
            return RET_ENV_FAIL

    def enter_selected_item(self, leave_bios, timeout):
        """
        press enter on selected item
        :param ignore: indicates whether to ignore the coming data
        :param timeout: timeout to get first data
        :return:
            RET_SUCCESS:    reach the selected page
            RET_TEST_FAIL:  can not go back to root menu page
            RET_ENV_FAIL:   any exception
            RET_INVALID_INPUT:  input parameter is not valid (data type is not correct)
        dependencies:
            bios_menu_helper.press_key
            bios_menu_helper.parse
        equivalent classes:
            valid:
                item_name (item_name on bios menu, item name which can not be found on  bios menu, non-string)
                item_type (BIOS_UI_OPT_TYPE, BIOS_UI_DIR_TYPE, BIOS_UI_INPUT_TYPE, None)
                use_regex (True, False)
                bios_menu_helper.press key return: (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
                bios_menu_helper.parse return: (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
            invalid:
                item name (Non-string)
                item type (None-string, String value out out of BIOS_UI_OPT_TYPE, BIOS_UI_DIR_TYPE, BUID_UI_INPUT_TYPE)
                use_regex: Non-boolean
                press key return: value of out defined Return value
                parse return: value of out defined Return value
        LOC: 20
        """
        try:
            self.__logger.debug(
                "enter_selected_item ignore={0}, timeout={0}".format(leave_bios, timeout))
            if leave_bios is None or timeout is None or timeout < 0:
                return RET_INVALID_INPUT

            ret = self.__setup_menu_helper.get_highlight()
            self.__logger.debug("highlight={0}, {1}".format(ret.return_code, ret.result_value))
            if ret.return_code != RET_SUCCESS or not ret.result_value[0]:
                self.__logger.error("return {0}".format(RET_TEST_FAIL))
                return RET_TEST_FAIL

            ret = self.__setup_menu_helper.press_key(BIOS_CMD_KEY_ENTER)
            if ret == RET_SUCCESS and not leave_bios:
                ret = self.__setup_menu_helper.wait_for_highlight(
                    timeout=timeout, item_name="", use_regex=False).return_code

            self.__logger.debug("return {0}".format(ret))
            return ret
        except Exception as ex:
            self.__logger.error("return {0}, ex={1}".format(RET_ENV_FAIL, ex))
            return RET_ENV_FAIL

    def get_selected_item(self):
        """
        get selected item in format of ReturnData
        :return:
        instance of ReturnData:
            Return Code:
                RET_SUCCESSRET_TEST_FAIL|RET_ENV_FAIL|RET_INVALID_INPUT:
                    return value should be exactly the same as
                     the most recent call of bios_menu_helper.parse|bios_menu_helper.wait_for_highlight
            return value:
                (name, type, subtitle, value)
        depencendies:
            bios_menu_helper.parse or bios_menu_helper.wait_for_highlight should be called
        equivalent classes:
            valid:
                bios_menu_helper.parse returns:
                (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
                or
                bios_menu_helper.wait_for_highlight return:
                (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
            invalid:
                bios_menu_helper.parse returns:
                None, Other values
                or
                bios_menu_helper.wait_for_highlight return:
                None, Other values
        LOC: 10
        """
        try:
            ret = self.__setup_menu_helper.get_highlight()
            if ret.return_code == RET_SUCCESS:
                ret_data = ReturnData(RET_SUCCESS,
                                      (ret.result_value[0],
                                       ret.result_value[2],
                                       ret.result_value[3],
                                       ret.result_value[1]))
            else:
                ret_data = ReturnData(ret.return_code, ("", "", "", "", ""))

            self.__logger.debug("return {0}{1}".format(ret_data.return_code, ret_data.result_value))
            return ret_data
        except Exception as ex:
            ret_data = ReturnData(RET_ENV_FAIL, ("", "", "", "", ""))
            self.__logger.debug(
                "return {0}, ex={1}".format(ret_data, ex))
            return ret_data

    def get_page_information(self):
        """
        get current page info in format of dictionary (key,value)
        :return:
            Return Data object
            return code:
                RET_SUCCESS:    if bios_menu_helper.parse or bios_menu_helper.wait_for_highlight return RET_SUCCESS
                RET_TEST_FAIL:  if bios_menu_helper.parse or bios_menu_helper.wait_for_highlight return RET_TEST_FAIL
                RET_ENV_FAIL:   if bios_menu_helper.parse or bios_menu_helper.wait_for_highlight return RET_ENV_FAIL
                RET_INVALID_INPUT:
                if bios_menu_helper.parse or bios_menu_helper.wait_for_highlight return RET_INVALID_INPUT
            return value:
                (key, value)
        dependencies:
            bios_menu_helper.parse
        equivalent classes:
            valid:
                bios_menu_helper.parse return: (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
            invalid:
                parse return: value of out defined Return value
        LOC: 10
        """
        try:
            return self.__setup_menu_helper.get_items()
        except:
            return ReturnData(RET_ENV_FAIL, [])

    def scan_current_page_items(self):
        try:
            self.__logger.debug('parse_bios_ui_items')
            item_list = []

            result, has_highlight, (hl_info, hl_position) = \
                self.get_highlight_with_position()
            if result != RET_SUCCESS or not has_highlight:
                return ReturnData(RET_TEST_FAIL, [])

            first_highlight = None
            if has_highlight:
                first_highlight = (hl_info[0], hl_position[0])
            null_count = 0
            while True:
                if not has_highlight:
                    if null_count < 10:
                        null_count += 1
                    else:
                        break
                else:
                    null_count = 0
                    if not hl_info[0].strip():
                        self.__logger.debug('lost item {0}'.format(hl_info))
                        null_count += 1
                    else:
                        if hl_info[0] not in [x[0] for x in item_list]:
                            item_list.append(hl_info)

                ret = self.press_key(BIOS_CMD_KEY_DOWN, True, self.__timeout_config.inner_move_timeout)
                if ret != RET_SUCCESS:
                    return ReturnData(ret, [])

                result, has_highlight, (
                    hl_info, hl_position) = self.get_highlight_with_position()
                if result != RET_SUCCESS or not has_highlight:
                    if result not in [RET_SUCCESS, RET_TEST_FAIL]:
                        return ReturnData(ret, [])

                    ret = self.get_title()
                    if ret.return_code != RET_SUCCESS:
                        return ReturnData(ret.return_code, [])
                    else:
                        break

                if first_highlight:
                    if first_highlight == (hl_info[0], hl_position[0]):
                        break
                else:
                    first_highlight = (hl_info[0], hl_position[0])

            self.__logger.debug('end parse_bios_ui_items {0}'.format(item_list))
            return ReturnData(RET_SUCCESS, item_list)
        except Exception as ex:
            self.__logger.error('error {0}'.format(ex))
            return ReturnData(RET_ENV_FAIL, [])

    def wait_for_popup_hightlight(self, item_name, timeout, use_regex):
        return self.__setup_menu_helper.wait_for_popup_highlight(
            item_name=item_name, timeout=timeout, use_regex=use_regex)

    def press_key(self, key_code, parse_data, timeout):
        """
        press enter on selected item
        :param key_code: key code (all non-empty data is supported)
        :param not_ignore: indicates whether to ignore the coming data
        :param timeout: timeout to get first data
        :return:
            RET_SUCCESS:    reach the selected page
            RET_TEST_FAIL:  can not go back to root menu page
            RET_ENV_FAIL:   any exception
            RET_INVALID_INPUT:  input parameter is not valid (data type is not correct)
        dependencies:
            bios_menu_helper.parse
        equivalent classes:
            valid:
                key_code: non-empty data (string, integer,...)
                timeout: [0, infinite)
                bios_menu_helper.parse return: (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
            invalid:
                key_code: None or empty data
                timeout: (negative infinite, 0)
                parse return: value of out defined Return value
        LOC: 20
        """
        try:
            self.__logger.debug("key_code {0}, not_ignore {1}, timeout{2}".format(key_code, parse_data, timeout))
            if not key_code or parse_data is None or timeout is None or timeout < 0:
                return RET_INVALID_INPUT

            ret = self.__setup_menu_helper.press_key(key_code)
            if ret != RET_SUCCESS and parse_data:
                ret = self.__setup_menu_helper.parse(timeout=timeout)

            self.__logger.debug("ret {0}".format(ret))
            return ret
        except Exception as ex:
            self.__logger.error("error {0}".format(ex))
            return RET_ENV_FAIL

    def input_text(self, text):
        """
        input text
        :param text: text to input
        :return:
            RET_SUCCESS:    input text successfully
            RET_ENV_FAIL:   fail to input
            RET_INVALID_INPUT:  text is not string
        dependencies:
            bios_menu_helper.press_key
        equivalent classes:
            valid:
                text:   string
                bios_menu_helper.press key return: (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
            invalid:
                text: non-string
                press key return: value of out defined Return value
        LOC: 10
        """
        try:
            if not text or not isinstance(text, str):
                self.__logger.debug("text /|{0}|/".format(text))
                return RET_INVALID_INPUT

            for c in text:
                ret = self.__setup_menu_helper.press_key(c)
                if ret != RET_SUCCESS:
                    return ret
                ret = self.__setup_menu_helper.parse(timeout=3)

            return RET_SUCCESS
        except Exception as ex:
            self.__logger.error(r'error message:%s' % ex)
            return RET_ENV_FAIL

    def select_from_popup(self, value, use_regex, timeout_config):
        """
        select item value from popup window
        :param value: item value to select
        :param use_regex: indicates whether to use regular expression
        :param timeout: timeout to get first data
        :return:
            RET_SUCCESS:    select the target value
            RET_TEST_FAIL:  can not find value
            RET_ENV_FAIL:   any exception
            RET_INVALID_INPUT:  input parameter is not valid (data type is not correct)
        dependencies:
            bios_menu_helper.parse
            bios_menu_helper.press_key
        equivalent classes:
            valid:
                use_regex: True / False
                timeout: [0, infinite)
                bios_menu_helper.parse return: (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
            invalid:
                use_regex: Non-boolean
                timeout: (negative infinite, 0)
                bios_menu_helper.parse return: none of (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
        LOC: 20
        """
        try:
            if not value or not timeout_config or not \
                    isinstance(timeout_config, TimeoutConfig) or use_regex is None:
                self.__logger.error("reutrn {0}".format(RET_INVALID_INPUT))
                return RET_INVALID_INPUT

            if not self.__enter_to_popup(
                    timeout=timeout_config.navigation_timeout):
                self.__logger.error("reutrn {0}".format(RET_TEST_FAIL))
                return RET_TEST_FAIL

            if not self.__highlight_popup_element(
                    value, None, use_regex=use_regex,
                    timeout=timeout_config.inner_move_timeout):
                self.__logger.error("reutrn {0}".format(RET_TEST_FAIL))
                return RET_TEST_FAIL

            ret = self.__setup_menu_helper.press_key(BIOS_CMD_KEY_ENTER)
            if ret != RET_SUCCESS:
                return ret

            ret = self.__setup_menu_helper.wait_for_highlight(timeout_config.navigation_timeout, "", False)
            self.__logger.debug("retrun {0}".format(ret.return_code))
            return ret.return_code
        except Exception as ex:
            self.__logger.debug(ex)
            return RET_ENV_FAIL

    def change_order(self, order_list, timeout_config):
        """
        change the order of item listed in popup window
        :param order_list: the ordered list of items
        :param timeout: timeout to get first data
        :return:
            RET_SUCCESS:    order changed successfully
            RET_TEST_FAIL:  can not find value
            RET_ENV_FAIL:   any exception
            RET_INVALID_INPUT:  input parameter is not valid (data type is not correct)
        dependencies:
            bios_menu_helper.parse
            bios_menu_helper.press_key
        equivalent classes:
            valid:
                order_list: [], list of string
                timeout: [0, infinite)
                bios_menu_helper.parse return: (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
            invalid:
                order_list: None List
                timeout: (negative infinite, 0)
                bios_menu_helper.parse return: none of (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
        LOC: 20
        """
        try:
            if not order_list or not isinstance(order_list, list) or not timeout_config or not \
                    isinstance(timeout_config, TimeoutConfig):
                return RET_INVALID_INPUT

            select_info = self.__setup_menu_helper.get_highlight()
            self.__logger.debug("change_order highlight {0} {1}".format(select_info.return_code,
                                                                        select_info.result_value))
            if not self.__enter_to_popup(timeout=timeout_config.navigation_timeout):
                self.__logger.error("__enter_to_popup error return {0}".format(RET_TEST_FAIL))
                return RET_TEST_FAIL
            self.__logger.error("__enter_to_popup success")

            order_list.reverse()
            for ele in order_list:
                if not self.__highlight_popup_element(
                        item_name=ele,
                        item_type=None,
                        use_regex=True,
                        timeout=timeout_config.inner_move_timeout):
                    self.__logger.error("change_order return {0}".format(RET_TEST_FAIL))
                    return RET_TEST_FAIL

                previous_layout = self.__get_order_page()
                if not previous_layout[0]:
                    self.__logger.error("change_order return {0}".format(RET_TEST_FAIL))
                    return RET_TEST_FAIL

                if not self.__change_position(
                        BIOS_CMD_KEY_PLUS,
                        timeout=timeout_config.inner_move_timeout):
                    self.__logger.error("change_order return {0}".format(RET_TEST_FAIL))
                    return RET_TEST_FAIL

                cur_layout = self.__get_order_page()
                if not cur_layout[0]:
                    self.__logger.error("change_order return {0}".format(RET_TEST_FAIL))
                    return RET_TEST_FAIL

                while previous_layout != cur_layout:
                    previous_layout = cur_layout

                    if not self.__change_position(
                            BIOS_CMD_KEY_PLUS,
                            timeout=timeout_config.inner_move_timeout):
                        self.__logger.error("change_order return {0}".format(RET_TEST_FAIL))
                        return RET_TEST_FAIL

                    cur_layout = self.__get_order_page()
                    if not cur_layout[0]:
                        self.__logger.error("change_order return {0}".format(RET_TEST_FAIL))
                        return RET_TEST_FAIL

            ret = self.__setup_menu_helper.press_key(BIOS_CMD_KEY_ENTER)
            if ret != RET_SUCCESS:
                self.__logger.error("change_order return {0}".format(ret))
                return ret

            ret = self.__setup_menu_helper.wait_for_highlight(timeout_config.inner_move_timeout, "", False)
            self.__logger.debug("change_order retrun {0}".format(ret.return_code))
            return ret.return_code
        except Exception as ex:
            self.__logger.error("change_order return {0}".format(ex))
            return RET_ENV_FAIL

    def is_check_type(self):
        """
        return the type of bios menu
        :return:
            True: if the selected item is check box
            False: if the selected item is not check box
        dependencies:
            bios_menu_helper.parse
            bios_menu_helper.press_key
        equivalent classes:
            valid:
                bios_menu_helper.parse return: (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
            invalid:
                bios_menu_helper.parse return: none of (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
        LOC: 10
        """
        ret = self.get_selected_item()
        if ret.return_code != RET_SUCCESS:
            return False

        (name, ret_type, sub, value) = ret.result_value
        return re.match('\\[[Xx ]\\]', value) and name and ret_type == BIOS_UI_OPT_TYPE

    def wait_for_setup_ui(self, timeout):
        self.__logger.debug("into function: timeout={0}".format(timeout))
        if timeout is None or timeout < 0:
            self.__logger.error("return:{0}".format(RET_INVALID_INPUT))
            return RET_INVALID_INPUT

        try:
            ret = self.__setup_menu_helper.clean_pyte()
            if ret != RET_SUCCESS:
                return ret

            ret = self.__setup_menu_helper.wait_for_highlight(
                timeout=timeout,
                item_name="",
                use_regex=False)

            if ret.return_code != RET_SUCCESS:
                return ret.return_code

            ret = self.__setup_menu_helper.get_highlight()

            return ret.return_code
        except Exception as e:
            self.__logger.error("return:{0}, Exception={1}".format(RET_ENV_FAIL, e))
            return RET_ENV_FAIL

    def wait_for_bios_setup_menu(self, timeout):
        """
        wait sut to enter bios setup menu until timeout
        :param timeout: timeout to get first data
        :return:
            RET_SUCCESS: if enter bios setup menu successfully
            RET_TEST_FAIL: if fail to enter without timeout
            RET_ENV_FAIL: invalid bios menu data received or serial disconnected
            RET_INVALID_INPUT: timeout is not a number
        dependencies:
            bios_menu_helper.parse
            bios_menu_helper.press_key
        equivalent classes:
            valid:
                timeout: [0, infinite)
                bios_menu_helper.parse return: (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
            invalid:
                timeout: (negative infinite, 0)
                bios_menu_helper.parse return: none of (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
        LOC: 20
        """
        self.__logger.debug("into function: timeout={0}".format(timeout))
        if timeout is None or timeout < 0:
            self.__logger.error("return:{0}".format(RET_INVALID_INPUT))
            return RET_INVALID_INPUT

        try:
            ret = self.__setup_menu_helper.clean_pyte()
            if ret != RET_SUCCESS:
                return ret

            ret = self.__setup_menu_helper.wait_for_highlight(
                timeout=timeout,
                item_name="",
                use_regex=False)

            self.__logger.debug('wait for highlight ok ... {0}, {1}'.format(ret.return_code,
                                                                            ret.result_value))
            if ret.return_code != RET_SUCCESS:
                return ret.return_code

            ret = self.__setup_menu_helper.get_highlight()
            return ret.return_code
        except Exception as e:
            self.__logger.error("return:{0}, Exception={1}".format(RET_ENV_FAIL, e))
            return RET_ENV_FAIL

    def enter_efishell(self, enter_config, timeout):
        """
        wait sut to enter efishell until timeout
        :param timeout: timeout to get first data
        :return:
            RET_SUCCESS: if enter bios setup menu successfully
            RET_TEST_FAIL: if fail to enter without timeout
            RET_ENV_FAIL: invalid bios menu data received or serial disconnected
            RET_INVALID_INPUT: timeout is not a number
        dependencies:
            bios_menu_helper.parse
            bios_menu_helper.press_key
        equivalent classes:
            valid:
                timeout: [0, infinite)
                bios_menu_helper.parse return: (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
            invalid:
                timeout: (negative infinite, 0)
                bios_menu_helper.parse return: none of (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
        LOC: 20
        """
        self.__logger.debug("into function: timeout={0}".format(timeout))
        if timeout is None or timeout < 0:
            self.__logger.error("return:{0}".format(RET_INVALID_INPUT))
            return RET_INVALID_INPUT
        start = datetime.datetime.now()
        try:
            if (datetime.datetime.now() - start).seconds > timeout:
                self.__logger.error("return:{0}".format(RET_TEST_FAIL))
                return RET_TEST_FAIL

            config = enter_config
            if not config or config == RET_INVALID_INPUT:
                self.__logger.error("return:{0}".format(RET_INVALID_INPUT))
                return RET_INVALID_INPUT
            try:
                config = json.loads(config)
            except:
                self.__logger.error("return:{0} config={1}".format(RET_INVALID_INPUT, config))
                return RET_INVALID_INPUT

            if not config or not isinstance(config, dict) or 'select_item' not in config.keys():
                self.__logger.error("return:{0} config error={1}".format(RET_TEST_FAIL, config))
                return RET_TEST_FAIL

            efi_path = config['path']
            if efi_path:
                efi_path = [(x, None) for x in efi_path]

            efi_node = config['select_item']
            self.__logger.debug('efi_path={0} efi_node={1}'.format(efi_path, efi_node))
            ret = self.back_to_root(self.__timeout_config.navigation_timeout, False)
            if ret != RET_SUCCESS:
                self.__logger.error("return:{0}".format(ret))
                return ret

            ret = self.goto(
                path=efi_path,
                use_regex=False,
                timeout_config=self.__timeout_config,
                is_page_info=False)
            if ret != RET_SUCCESS:
                self.__logger.error("return:{0}".format(RET_TEST_FAIL))
                return ret

            if (datetime.datetime.now() - start).seconds > timeout:
                self.__logger.error("return:{0}".format(RET_TEST_FAIL))
                return RET_TEST_FAIL

            if not self.__highlight_element(efi_node,
                                            None, False, self.__timeout_config.inner_move_timeout):
                self.__logger.error("return:{0}".format(RET_TEST_FAIL))
                return RET_TEST_FAIL

            ret = self.press_key(BIOS_CMD_KEY_ENTER, False, timeout=0)

            if (datetime.datetime.now() - start).seconds > timeout:
                self.__logger.error("return:{0}".format(RET_TEST_FAIL))
                return RET_TEST_FAIL

            self.__logger.debug("return:{0}".format(ret))
            return ret
        except Exception as e:
            self.__logger.error("return:{0}, Exception={1}".format(RET_ENV_FAIL, e))
            return RET_ENV_FAIL

    def continue_to_os(self, enter_config):

        """
        select continue menu and enter
        :param timeout: timeout to get first data
        :return:
            RET_SUCCESS: if find item and press enter successfully
            RET_TEST_FAIL: if fail to enter without timeout
            RET_ENV_FAIL: invalid bios menu data received or serial disconnected
            RET_INVALID_INPUT: timeout is not a number
        dependencies:
            bios_menu_helper.parse
            bios_menu_helper.press_key
        equivalent classes:
            valid:
                timeout: [0, infinite)
                bios_menu_helper.parse return: (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
            invalid:
                timeout: (negative infinite, 0)
                bios_menu_helper.parse return: none of (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
        LOC: 20
        """
        self.__logger.debug("into function")

        try:
            config = enter_config
            if not config or config == RET_INVALID_INPUT:
                self.__logger.error("return:{0}".format(RET_TEST_FAIL))
                return RET_TEST_FAIL

            try:
                config = json.loads(config)
                if 'press_key' in config.keys():
                    config['press_key'] = str(config['press_key'].replace('\\33', '\33')).encode(encoding='utf-8')
            except:
                self.__logger.error(
                    "11 config is null or not support return:{0} {1}".format(
                        RET_TEST_FAIL, config))
                return RET_TEST_FAIL

            if 'select_item' in config.keys():
                ret = self.back_to_root(timeout=self.__timeout_config.navigation_timeout, is_page_info=False)
                if ret != RET_SUCCESS:
                    self.__logger.error("return:{0}".format(ret))
                    return ret

                continue_path = config['path']
                if continue_path:
                    continue_path = [(x, None) for x in continue_path]

                continue_node = config['select_item']
                self.__logger.debug(
                    'continue_path = {0}, continue_node = {1}'.format(
                        continue_path, continue_node))
                ret = self.goto(
                    path=continue_path,
                    use_regex=False,
                    timeout_config=self.__timeout_config,
                    is_page_info=False)
                if ret != RET_SUCCESS:
                    self.__logger.error('reutrn {0}'.format(ret))
                    return ret

                if not self.__highlight_element(continue_node, None, False, self.__timeout_config.inner_move_timeout):
                    return RET_TEST_FAIL

                ret = self.enter_selected_item(leave_bios=True, timeout=self.__timeout_config.navigation_timeout)
            elif 'press_key' in config.keys():
                ret = self.press_key(config['press_key'], eval(config['parse']),
                                     self.__timeout_config.navigation_timeout)
            else:
                raise Exception("Config error config={0}".format(config))

            self.__logger.debug("return:{0}".format(ret))
            return ret
        except Exception as e:
            self.__logger.error("return:{0}, Exception={1}".format(RET_ENV_FAIL, e))
            return RET_ENV_FAIL

    def reboot(self, timeout, enter_config):
        """
        select reboot item trigger reboot
        :param timeout: timeout to get first data
        :return:
            RET_SUCCESS: if find item and press enter successfully
            RET_TEST_FAIL: if fail to enter without timeout
            RET_ENV_FAIL: invalid bios menu data received or serial disconnected
            RET_INVALID_INPUT: timeout is not a number
        dependencies:
            bios_menu_helper.parse
            bios_menu_helper.press_key
        equivalent classes:
            valid:
                timeout: [0, infinite)
                bios_menu_helper.parse return: (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
            invalid:
                timeout: (negative infinite, 0)
                bios_menu_helper.parse return: none of (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
        LOC: 20
        """
        self.__logger.debug("into function: timeout={0}".format(timeout))
        if timeout is None or timeout < 0:
            self.__logger.error("return:{0}".format(RET_INVALID_INPUT))
            return RET_INVALID_INPUT

        try:
            config = enter_config
            if not config or config == RET_INVALID_INPUT:
                self.__logger.error("return:{0}".format(RET_TEST_FAIL))
                return RET_TEST_FAIL

            try:

                # config = json.loads(config)
                if 'press_key' in config.keys():
                    # config['press_key'] = str(config['press_key'].replace('\\33', '\33')).encode(encoding='utf-8')
                    config['press_key'] = str(config['press_key'].replace('\\33', '\33'))
            except:
                self.__logger.error(
                    " config is null or not support return:{0} {1}".format(
                        RET_TEST_FAIL, config))
                return RET_TEST_FAIL

            if 'select_item' in config.keys():
                ret = self.back_to_root(timeout=self.__timeout_config.navigation_timeout, is_page_info=False)
                if ret != RET_SUCCESS:
                    self.__logger.error("return:{0}".format(ret))
                    return ret

                reboot_path = config['path']
                if reboot_path:
                    reboot_path = [(x, None) for x in reboot_path]
                reboot_node = config['select_item']
                self.__logger.debug(
                    'reboot_path={0}, reboot_node={1}'.format(
                        reboot_path, reboot_node))
                ret = self.goto(
                    path=reboot_path,
                    use_regex=False,
                    timeout_config=self.__timeout_config,
                    is_page_info=False)
                if ret != RET_SUCCESS:
                    self.__logger.error("return:{0}".format(ret))
                    return ret

                if not self.__highlight_element(reboot_node, None, False, self.__timeout_config.inner_move_timeout):
                    return RET_TEST_FAIL

                ret = self.enter_selected_item(True, 0)
            elif 'press_key' in config.keys():
                ret = self.press_key(config['press_key'], config['parse'], self.__timeout_config.navigation_timeout)
            else:
                raise Exception("Config error config={0}".format(config))

            self.__logger.debug("return:{0}".format(ret))
            return ret
        except Exception as e:
            self.__logger.error("return:{0}, Exception={1}".format(RET_ENV_FAIL, e))
            return RET_ENV_FAIL

    def get_title(self):
        try:
            ret_info = self.__setup_menu_helper.get_title()

            self.__logger.debug(
                'return return_code {0}, result_value {1}'.format(
                    ret_info.return_code, ret_info.result_value))
            return ret_info
        except Exception as ex:
            ret = ReturnData(RET_ENV_FAIL, '')
            self.__logger.error('return return_code {0}, result_value {1} ex {2}'.format(
                ret.return_code, ret.result_value, ex))
            return ret

    def check_item_repeat(self, item_list, new_item):
        repeat_count = 1
        if item_list and item_list[-1] == new_item:
            return True

        if new_item in item_list:
            repeat_str = \
                "".join(
                    ["{0}_{1}".format(
                        x[0], x[1]) for x in (item_list[:repeat_count - 1] + [new_item])])
            full_str = "".join(["{0}_{1}".format(x[0], x[1]) for x in item_list])
            if full_str.rfind(repeat_str) not in [0, -1]:
                return True

        return False

    def __highlight_element(self, item_name, item_type, use_regex, timeout):
        his = []
        self.__logger.debug(
            "__highlight_element item_name {0} item_type {1} use_regex {2} timeout {3}".format(
                item_name, item_type, use_regex, timeout))
        result, has_highlight, (hl_info, hl_position) = self.get_highlight_with_position()
        # if result != RET_SUCCESS:
        #     return False

        self.__logger.debug("HIGHLGHT INFO: {0}{1}".format(hl_info, hl_position))
        if has_highlight:
            if hl_info[0] == item_name or \
                    (use_regex and re.search(item_name, hl_info[0])):
                return True
            else:
                his.append((hl_info[0], hl_position[0]))

        no_highlight_count = 0
        cmd = BIOS_CMD_KEY_DOWN
        while True:
            self.__logger.debug("his list = {0}".format(his))
            self.__logger.debug("BIOS_CMD_KEY_DOWN TRY to highlight [{0}]".format(item_name))

            if self.__setup_menu_helper.press_key(cmd) != RET_SUCCESS:
                raise Exception("__highlight_element press_key error")

            ret = self.__setup_menu_helper.wait_for_highlight(
                item_name=item_name, timeout=timeout, use_regex=use_regex)

            if ret.return_code != RET_SUCCESS:
                raise Exception("__highlight_element wait_for_highlight error")

            if ret.result_value:
                self.__logger.debug(
                    "__highlight_element {0} ok".format(item_name))
                return True
            else:
                result, has_highlight, (hl_info, hl_position) = self.get_highlight_with_position()
                if result != RET_SUCCESS:
                    self.__logger.error("get hilight error")
                    return False

                self.__logger.debug("HIGHLGHT INFO: {0}{1}".format(hl_info, hl_position))
                if has_highlight:
                    if self.check_item_repeat(his, (hl_info[0], hl_position[0])):
                        break

                    his.append((hl_info[0], hl_position[0]))
                    no_highlight_count = 0
                else:
                    if no_highlight_count < 10:
                        no_highlight_count += 1
                    else:
                        self.__logger.error("no highlight count > 10 times")
                        break

        his = []
        no_highlight_count = 0
        cmd = BIOS_CMD_KEY_UP
        self.__logger.debug("BIOS_CMD_KEY_UP")
        while True:
            self.__logger.debug("his list = {0}".format(his))
            self.__logger.debug("BIOS_CMD_KEY_UP  TRY to highlight [{0}]".format(item_name))

            if self.__setup_menu_helper.press_key(cmd) != RET_SUCCESS:
                raise Exception("__highlight_element press_key error")

            ret = self.__setup_menu_helper.wait_for_highlight(
                item_name=item_name, timeout=timeout, use_regex=use_regex)

            if ret.return_code != RET_SUCCESS:
                raise Exception("__highlight_element wait_for_highlight error")

            if ret.result_value:
                self.__logger.debug(
                    "__highlight_element {0} ok".format(item_name))
                return True
            else:
                result, has_highlight, (hl_info, hl_position) = self.get_highlight_with_position()
                if result != RET_SUCCESS:
                    return False

                self.__logger.debug("HILGHT INFO: {0}, {1}".format(hl_info, hl_position))
                if has_highlight:
                    if self.check_item_repeat(his, (hl_info[0], hl_position[0])):
                        break

                    his.append((hl_info[0], hl_position[0]))
                    no_highlight_count = 0
                else:
                    if no_highlight_count < 10:
                        no_highlight_count += 1
                    else:
                        self.__logger.error("no highlight count > 10 times")
                        break

        self.__logger.debug(
            "__highlight_element {0} not finished".format(item_name))
        return False

    def __highlight_popup_element(self, item_name, item_type, use_regex, timeout):
        his = []
        no_highlight_count = 0

        self.__logger.debug(
            "__highlight_popup_element item_name {0} item_type {1} use_regex {2} timeout {3}".format(
                item_name, item_type, use_regex, timeout))
        highlight_info = self.get_highlight_with_position()
        if highlight_info[0] != RET_SUCCESS:
            return False

        self.__logger.debug("HILGHT INFO: {0}".format(highlight_info))
        if highlight_info[1]:
            if highlight_info[2][0][0] == item_name or \
                    (use_regex and re.search(item_name, highlight_info[2][0][0])):
                return True
            else:
                his.append(highlight_info[2])

        cmd = BIOS_CMD_KEY_DOWN
        self.__logger.debug("BIOS_CMD_KEY_DOWN")
        while True:
            self.__logger.debug("his list = {0}".format(his))
            self.__logger.debug("TRY to highlight [{0}]".format(item_name))

            if self.__setup_menu_helper.press_key(cmd) != RET_SUCCESS:
                raise Exception("__highlight_element press_key error")

            ret = self.__setup_menu_helper.wait_for_popup_highlight(
                item_name=item_name, timeout=timeout, use_regex=use_regex)

            if ret.return_code != RET_SUCCESS:
                raise Exception("__highlight_element wait_for_highlight error")

            if ret.result_value:
                self.__logger.debug(
                    "__highlight_element {0} ok".format(item_name))
                return True
            else:
                highlight_info = self.get_highlight_with_position()
                if highlight_info[0] != RET_SUCCESS:
                    return False

                self.__logger.debug("HILGHT INFO: {0}".format(highlight_info))
                if highlight_info[1]:
                    no_highlight_count = 0
                    if highlight_info[2] in his:
                        break
                    else:
                        his.append(highlight_info[2])
                else:
                    if no_highlight_count < 10:
                        no_highlight_count += 1
                    else:
                        self.__logger.error("no highlight count > 10 times")
                        break

        his = []
        no_highlight_count = 0
        cmd = BIOS_CMD_KEY_UP
        self.__logger.debug("BIOS_CMD_KEY_UP")
        while True:
            self.__logger.debug("his list = {0}".format(his))
            self.__logger.debug("TRY to highlight [{0}]".format(item_name))

            if self.__setup_menu_helper.press_key(cmd) != RET_SUCCESS:
                raise Exception("__highlight_element press_key error")

            ret = self.__setup_menu_helper.wait_for_popup_highlight(
                item_name=item_name, timeout=timeout, use_regex=use_regex)

            if ret.return_code != RET_SUCCESS:
                raise Exception("__highlight_element wait_for_highlight error")

            if ret.result_value:
                self.__logger.debug(
                    "__highlight_element {0} ok".format(item_name))
                return True
            else:
                highlight_info = self.get_highlight_with_position()
                if highlight_info[0] != RET_SUCCESS:
                    return False

                self.__logger.debug("HILGHT INFO: {0}".format(highlight_info))
                if highlight_info[1]:
                    no_highlight_count = 0
                    if highlight_info[2] in his:
                        break
                    else:
                        his.append(highlight_info[2])
                else:
                    if no_highlight_count < 10:
                        no_highlight_count += 1
                    else:
                        self.__logger.error("no highlight count > 10 times")
                        break

        self.__logger.debug(
            "__highlight_element {0} not finished".format(item_name))
        return False

    def __enter_to_popup(self, timeout):
        self.__logger.debug('__enter_to_popup ...')
        if RET_SUCCESS != self.__setup_menu_helper.press_key(BIOS_CMD_KEY_ENTER):
            self.__logger.debug('press_key_fail')
            return False
        self.__logger.debug('press key ok')
        ret = self.__setup_menu_helper.wait_for_popup_highlight(
            timeout, "__enter_to_popup", False)

        if RET_SUCCESS != ret.return_code:
            self.__logger.error('wait_for_popup_highlight fail')
            return False

        ret = self.__setup_menu_helper.is_popup()
        if ret.return_code != RET_SUCCESS or not ret.result_value[0]:
            self.__logger.error("enter_to_popup into popup mode......")
            return False

        if RET_SUCCESS == self.__setup_menu_helper.get_items().return_code:
            return True
        else:
            return False

    def __change_position(self, cmd, timeout):
        ret = self.__setup_menu_helper.press_key(cmd)
        if ret != RET_SUCCESS:
            return False

        ret = self.__setup_menu_helper.parse(timeout=timeout, is_popup=True)
        if ret != RET_SUCCESS:
            return False

        return True

    def __get_order_page(self):
        ret = self.__setup_menu_helper.get_items()
        if ret.return_code != RET_SUCCESS:
            self.__logger.error("return {0}".format(ret.return_code))
            return False, None, None

        page_items = ret.result_value

        ret = self.__setup_menu_helper.get_highlight_position()
        if ret.return_code != RET_SUCCESS:
            return False, None, None

        return True, page_items, ret.result_value

    def get_highlight_with_position(self):
        highlight = self.__setup_menu_helper.get_highlight()
        if highlight.return_code != RET_SUCCESS:
            return highlight.return_code, False, (None, None)

        postion = self.__setup_menu_helper.get_highlight_position()
        if postion.return_code != RET_SUCCESS:
            return postion.return_code, False, (None, None)

        if not postion.result_value != (None, None, None):
            return RET_SUCCESS, False, (None, None)

        return RET_SUCCESS, True, (highlight.result_value, postion.result_value)
