"""
Define Data Layer to parse bios data
LOC: 500
"""

from json import loads
from re import search

from dtaf_core.lib.private.cl_utils.adapter.data_types import BIOS_BOOT_MENU_TYPE, RET_SUCCESS, RET_INVALID_INPUT, \
    RET_ENV_FAIL, RET_TEST_FAIL, BIOS_CMD_KEY_ENTER, ReturnData, BIOS_CMD_KEY_CTRL_ALT_DELETE, BIOS_CMD_KEY_DOWN, \
    BIOS_CMD_KEY_UP
from dtaf_core.lib.private.cl_utils.adapter.private.bios_menu_helper import BiosMenuHelper
import datetime


class BiosBootMenuDataAdapter(object):
    """
    Bios Boot Menu Data Layer
    handle the interaction between serial and APIs
    """

    def __init__(self, data_helper, screen_high, screen_width, navigation_timeout, internal_timeout, cfg, logger):
        self.__logger = logger
        self.__data_helper = data_helper
        self.__boot_menu_helper = BiosMenuHelper(screen_width, screen_high,
                                                 BIOS_BOOT_MENU_TYPE, self.__data_helper, cfg, self.__logger)

        self.__logger.debug(self.__boot_menu_helper)
        self.navigation_timeout = navigation_timeout
        self.internal_timeout = internal_timeout
        self.__cfg = cfg
        self.__logger.debug("BIOS SETUP MENU RESOLUTION: with: %d, high %d" %
                            (screen_width, screen_high))
        self.__logger.debug("BIOS SETUP MENU TIMEOUT: navigation_timeout: {0}, "
                            "internal_timeout: {1}".format(navigation_timeout, internal_timeout))

    def select(self, item_name, item_type, timeout, use_regex):
        """
        select an item on bios boot menu page
        :param item_name: item name to select
        :param item_type: item type (None, BIOS_UI_OPT_TYPE, BIOS_UI_DIR_TYPE, BIOS_UI_INPUT_TYPE)
        :param timeout: the overall timeout to receive the first data
        :param use_regex: whether to use regress expression to match the item (True / False)
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
                timeout:    [0, infinite)
            invalid:
                item name (Non-string)
                item type (None-string, String value out out of BIOS_UI_OPT_TYPE, BIOS_UI_DIR_TYPE, BUID_UI_INPUT_TYPE)
                use_regex: Non-boolean
                press key return: value of out defined Return value
                parse return: value of out defined Return value
                timeout: (negative infinite, 0)
        LOC: 50
        """
        self.__boot_menu_helper.parse(timeout=timeout)
        try:
            self.__logger.debug("elementName={0}, type={1}, regex={2}".format(
                item_name, item_type, use_regex))
            if not item_name or use_regex is None or timeout < 0 or timeout is None:
                return RET_INVALID_INPUT

            if not self.__highlight_element(
                    item_name=item_name, item_type=item_name, use_regex=use_regex,
                    timeout=timeout):
                self.__logger.error(
                    "111 __highlight_element return = {0}".format(
                        RET_TEST_FAIL))
                return RET_TEST_FAIL

            return_value = RET_TEST_FAIL
            ret = self.__boot_menu_helper.get_highlight()
            selName = ret.result_value[0]
            selType = ret.result_value[2]

            if use_regex and search(item_name, selName) is not None and item_type is None:
                return_value = RET_SUCCESS
            elif use_regex and search(item_name, selName) is not None and \
                    item_type is not None and item_type == selType:
                return_value = RET_SUCCESS
            elif not use_regex and item_type and item_type == selType and selName == item_name:
                return_value = RET_SUCCESS
            elif not use_regex and not item_type and selName == item_name:
                return_value = RET_SUCCESS

            self.__logger.debug("return {0}".format(return_value))
            return return_value
        except Exception as ex:
            self.__logger.error(r'biosAPI.select %s' % item_name)
            self.__logger.debug("return {0} ex={1}".format(RET_ENV_FAIL, ex))
            return RET_ENV_FAIL

    def press_key(self, key_code, parse_data, timeout):
        try:
            if timeout is None or timeout < 0 or parse_data is None:
                return RET_INVALID_INPUT

            ret = self.__boot_menu_helper.press_key(key_code)
            if ret == RET_SUCCESS and parse_data:
                ret = self.__boot_menu_helper.parse(timeout=timeout)

            self.__logger.debug(" ok return {0}".format(ret))
            return ret
        except Exception as ex:
            self.__logger.error(" fail return {0}, ex={1}".format(RET_ENV_FAIL, ex))
            return RET_ENV_FAIL

    def enter_selected_item(self, timeout, ignore_output):
        """
        enter the selected item on bios menu page
        :param timeout: the overall timeout to receive the first data
        :param ignore_output: indicate whether to ignore the output after enter.
        it is usually used for the item to enter different env (e.g. EFISHell)
        :return:
            RET_SUCCESS -   enter item successfully.
            RET_TEST_FAIL   -  no item is selected. enter selected item, ignore_output=False, but no output
            RET_ENV_FAIL    -   any exception occurs
            RET_INVALID_INPUT   -   ignore_output is not boolean
        dependencies:
            bios_menu_helper.press_key
            bios_menu_helper.parse
            bios_menu_helper.get_highlight
        equivalent classes:
            timeout: >=0
            ignore_output: True, False
            bios_menu_helper.press_key:
                RET_SUCCESS, RET_TEST_FAIL, RET_ENV_FAIL,   RET_INVALID_INPUT
            bios_menu_helper.parse:
                RET_SUCCESS, RET_TEST_FAIL, RET_ENV_FAIL,   RET_INVALID_INPUT
            bios_menu_helper.get_highlight:
                string type
        LOC: 30
        """
        try:
            if timeout is None or timeout < 0 or ignore_output is None:
                return RET_INVALID_INPUT

            ret = self.__boot_menu_helper.get_highlight()
            self.__logger.debug("highlight={0}, {1}".format(ret.return_code, ret.result_value))

            if ret.return_code != RET_SUCCESS or not ret.result_value[0]:
                self.__logger.error("return {0}".format(RET_TEST_FAIL))
                return RET_TEST_FAIL

            ret = self.__boot_menu_helper.press_key(BIOS_CMD_KEY_ENTER)
            if ret == RET_SUCCESS:
                self.__logger.debug("return {0}".format(ret))
                return RET_SUCCESS
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
            self.__boot_menu_helper.parse(timeout=10)
            return self.__boot_menu_helper.get_highlight()
        except Exception as ex:
            ret_data = ReturnData(
                return_code=RET_ENV_FAIL, result_value=("", "", "", ""))
            self.__logger.debug(
                "return {0}, ex={1}".format(ret_data, ex))
            return ret_data

    def get_page_information(self):
        """
        get information on current bios menu page in format of list: [(name, value),...]
        :return:
        instance of ReturnData:
            return code:
                RET_SUCCESSRET_TEST_FAIL|RET_ENV_FAIL|RET_INVALID_INPUT:
                    return value should be exactly the same as
                     the most recent call of bios_menu_helper.parse|bios_menu_helper.wait_for_highlight
            return value:
                an instance of list in format of (name, value).
                 if return code is not RET_SUCCESS, return value should be []
        equivalent classes:
            valid:
                bios_menu_helper.parse return:
                (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
                or
                bios_menu_helper.wait_for_highlight return:
                (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
            invalid:
                bios_menu_helper.parse return:
                None, Other values
                or
                bios_menu_helper.wait_for_highlight return:
                None, Other values
        LOC: 10
        """
        try:
            return self.__boot_menu_helper.get_items()
        except:
            return ReturnData(RET_ENV_FAIL, [])

    def wait_for_bios_boot_menu(self, timeout):
        """
        wait sut to enter bios setup menu until timeout
        :param timeout: timeout to wait
        :return:
            RET_SUCCESS: if enter bios setup menu successfully
            RET_TEST_FAIL: if fail to enter without timeout
            RET_ENV_FAIL: invalid bios menu data received or serial disconnected
            RET_INVALID_INPUT: timeout is not a number
        dependencies:
            bios_menu_helper.parse or bios_menu_helper.wait_for_highlight should be called
        equivalent classes:
            valid:
                bios_menu_helper.parse returns:
                (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
                or
                bios_menu_helper.wait_for_highlight return:
                (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL, RET_INVALID_INPUT)
                timeout -   [0, infinite),
            invalid:
                bios_menu_helper.parse returns:
                None, Other values
                or
                bios_menu_helper.wait_for_highlight return:
                None, Other values
                timeout -   (negative infinite, 0)
        LOC: 20
        """
        self.__logger.debug("into function: timeout={0}".format(timeout))
        if timeout is None or timeout < 0:
            self.__logger.error("return:{0}".format(RET_INVALID_INPUT))
            return RET_INVALID_INPUT

        try:
            ret = self.__boot_menu_helper.clean_pyte()
            if RET_SUCCESS != ret:
                return ret

            ret = self.__boot_menu_helper.wait_for_highlight(
                timeout=timeout,
                item_name="wait_for_bios_boot_menu",
                use_regex=False)

            if ret.return_code != RET_SUCCESS:
                return ret.return_code

            ret = self.__boot_menu_helper.get_highlight()

            return ret.return_code
        except Exception as ex:
            self.__logger.error("return:{0}, Exception={1}".format(RET_ENV_FAIL, ex))
            return RET_ENV_FAIL

    def enter_efishell(self, enter_config, timeout):
        """
        transition from current state to EFIShell
        it will choose Launch EFIShell to enter efi
        :param timeout:
        :return:
            RET_SUCCESS: if enter efishell successfully
            RET_TEST_FAIL: if can not enter efishell within timeout, or can not find the LAUNCH option
            RET_ENV_FAIL: external excpeption
        dependencies:
            bios_menu_helper.press_key
            bios_menu_helper.get_highlight
        equivalent classes:
            valid:
                timeout, return of press_key, return of get_highlight:
                [0, infinite), (RET_SUCCESS, RET_ENV_FAIL, RET_TEST_FAIL),
                (string:item name, string:item type, string: subtitle, string: value)
            invalid:
                (negative infinite, 0), (other value), [Non-tuple, or non-string item inside tuple)
        LOC:
            50
        """
        self.__logger.debug("timeout={0}".format(timeout))
        if timeout is None or timeout < 0:
            self.__logger.error("return:{0}".format(RET_INVALID_INPUT))
            return RET_INVALID_INPUT

        try:
            config = enter_config
            if not config or config == RET_INVALID_INPUT:
                self.__logger.error("return:{0}".format(RET_TEST_FAIL))
                return RET_TEST_FAIL
            try:
                config = loads(config)
            except Exception as ex:
                self.__logger.error("return:{0} config={1}".format(RET_TEST_FAIL, config))
                return RET_TEST_FAIL

            if not config or not isinstance(config, dict) or 'select_item' not in config.keys():
                self.__logger.error("return:{0} config error={1}".format(RET_TEST_FAIL, config))
                return RET_TEST_FAIL

            if not self.__highlight_element(
                    item_name=config['select_item'],
                    item_type=None,
                    use_regex=False,
                    timeout=timeout):
                return RET_TEST_FAIL

            return self.__boot_menu_helper.press_key(BIOS_CMD_KEY_ENTER)
        except Exception as ex:
            self.__logger.error("return:{0}, Exception={1}".format(RET_ENV_FAIL, ex))
            return RET_ENV_FAIL

    def reboot(self, timeout):
        """
        reboot to entry menu
        return RET_SUCCESS when the text content of entry menu, which is 'F2 to enter bios setup menu' is found
        :param timemout:
        :return:
            RET_SUCCESS: if entry menu is reached.
            RET_TEST_FAIL: if can not reach entry menu within timeout
            RET_ENV_FAIL: serial disconnect
        dependencies:
            g_main_serial_service.write
        equivalent classes:
            timeout: >= 0, < 0
            g_main_serial_service.write return_value:    No exception or any exception raised
        LOC: 20
        """
        self.__logger.debug("timeout={0}".format(timeout))
        if timeout is None or timeout < 0:
            self.__logger.error("return:{0}".format(RET_INVALID_INPUT))
            return RET_INVALID_INPUT

        try:
            ret = self.__boot_menu_helper.press_key(BIOS_CMD_KEY_CTRL_ALT_DELETE)

            self.__logger.debug("return:{0}".format(ret))
            return ret
        except Exception as ex:
            self.__logger.error("return:{0}, Exception={1}".format(RET_ENV_FAIL, ex))
            return RET_ENV_FAIL

    def __highlight_element(self, item_name, item_type, use_regex, timeout):
        his = []

        start_time = datetime.datetime.now()
        self.__logger.debug(
            "__highlight_element {0} {1} {2} {3}".format(
                item_name, item_type, use_regex, timeout))
        highlight = self.__boot_menu_helper.get_highlight()
        self.__logger.debug("highlight: {}".format(highlight))
        if item_name not in [r'UEFI Internal Shell']:
            if highlight.return_code == RET_SUCCESS:
                if highlight.result_value[0] == item_name:
                    self.__logger.debug(
                        "__highlight_element {0} ok".format(item_name))
                    return True
                elif use_regex:
                    if search(item_name, highlight.result_value[0]):
                        self.__logger.debug(
                            "__highlight_element {0} ok".format(item_name))
                        return True

        cmd = BIOS_CMD_KEY_DOWN
        self.__logger.debug("BIOS_CMD_KEY_DOWN")
        duplicated_count = 0
        max_duplicated = 10
        while True:
            self.__logger.debug("his list = {0}".format(his))
            self.__logger.debug("try to highlight {0} cur is {1}".format(item_name, highlight.result_value[0]))
            if self.__boot_menu_helper.press_key(cmd) != RET_SUCCESS:
                if item_name in [r'UEFI Internal Shell'] and (datetime.datetime.now() - start_time).seconds < int(
                        timeout):
                    continue
                return False

            ret = self.__boot_menu_helper.wait_for_highlight(
                item_name=item_name, timeout=timeout, use_regex=use_regex)

            if ret.return_code != RET_SUCCESS:
                if item_name in [r'UEFI Internal Shell'] and (datetime.datetime.now() - start_time).seconds < int(
                        timeout):
                    continue
                return False

            if ret.result_value:
                self.__logger.debug(
                    "__highlight_element {0} ok".format(item_name))
                return True
            else:
                self.__logger.debug(
                    "__highlight_element {0} failed".format(item_name))
                highlight = self.__boot_menu_helper.get_highlight()
                if highlight.return_code == RET_SUCCESS and highlight.result_value[0]:
                    if highlight.result_value[0] in his:
                        if duplicated_count < max_duplicated:
                            duplicated_count += 1
                        else:
                            break
                    else:
                        his.append(highlight.result_value[0])
                else:
                    break

        his = []
        cmd = BIOS_CMD_KEY_UP
        self.__logger.debug("BIOS_CMD_KEY_UP")
        duplicated_count = 0
        while True:
            self.__logger.debug("his list = {0}".format(his))
            self.__logger.debug("try to highlight {0} cur is {1}".format(item_name, highlight.result_value))
            if self.__boot_menu_helper.press_key(cmd) != RET_SUCCESS:
                return False

            ret = self.__boot_menu_helper.wait_for_highlight(
                item_name=item_name, timeout=timeout, use_regex=use_regex)

            if ret.return_code != RET_SUCCESS:
                return False

            if ret.result_value:
                self.__logger.debug(
                    "__highlight_element {0} ok".format(item_name))
                return True
            else:
                highlight = self.__boot_menu_helper.get_highlight()
                if (highlight.return_code == RET_SUCCESS and highlight.result_value):
                    if highlight.result_value in his:
                        if duplicated_count < max_duplicated:
                            duplicated_count += 1
                        else:
                            break
                    else:
                        his.append(highlight.result_value)
                else:
                    break
        self.__logger.debug(
            "__highlight_element {0} not finished".format(item_name))
        return False
