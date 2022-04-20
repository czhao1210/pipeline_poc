#!/usr/bin/env python
"""
#################################################################################
# INTEL CONFIDENTIAL
# Copyright Intel Corporation All Rights Reserved.
#
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material may contain trade secrets and proprietary
# and confidential information of Intel Corporation and its suppliers and
# licensors, and is protected by worldwide copyright and trade secret laws and
# treaty provisions. No part of the Material may be used, copied, reproduced,
# modified, published, uploaded, posted, transmitted, distributed, or disclosed
# in any way without Intel's prior express written permission.
#
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
#################################################################################
"""
from abc import ABCMeta

from six import add_metaclass

from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.drivers.internal.simics_driver import SimicsDriver
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.private.cl_utils.adapter.data_types import TimeoutConfig
from dtaf_core.lib.private.context import ContextInstance as _ContextInstance
from dtaf_core.lib.private.globals.data_type import ReturnData
from dtaf_core.lib.private.globals.return_code import RET_ENV_FAIL, RET_INVALID_INPUT
from dtaf_core.lib.private.provider_config.bios_setupmenu_provider_config import BiosSetupmenuProviderConfig
from dtaf_core.providers import bios_menu
from xml.etree.ElementTree import Element


@add_metaclass(ABCMeta)
class SimicsBiosSetupmenuProvider(bios_menu.BiosSetupMenuProvider):
    def __init__(self, cfg_opts, log):
        super(SimicsBiosSetupmenuProvider, self).__init__(cfg_opts, log)
        self.__width = self._config_model.width
        self.__height = self._config_model.height
        self.__logger = log
        self.buffer_name = 'setupment_buffer_{}'.format(self._config_model.driver_cfg.host)
        driver_cfg = None
        if isinstance(self._cfg, Element):
            driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                               driver_name=self._config_model.driver_cfg.name)
        elif isinstance(self._cfg, dict):
            driver_cfg = self._cfg["driver"]

        self.__driver = DriverFactory.create(driver_cfg, logger=log)  # type: SimicsDriver
        self.__driver.register(buffer_name=self.buffer_name)
        self.__adapter = _ContextInstance.get(
            serial_service=self.__driver.SerialChannel,
            is_host_service=False, logger=log, buffer_name=self.buffer_name, width=self.__width, high=self.__height).data_adapter[
            'setup_menu']
        self.__data_adapter = _ContextInstance.get(
            serial_service=self.__driver.SerialChannel, logger=self.__logger,
            buffer_name=self.buffer_name, width=self.__width, high=self.__height).data_adapter['entry_menu']
        self.__driver.start()

    def press(self, input_key):

        """
        Press F1 to F12
        :param input_key:
        :return:
        """
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return self.__data_adapter.press(input_key)

    def press_key(self, key_code, not_ignore, timeout):
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return self.__adapter.press_key(key_code, not_ignore, timeout)

    def wait_for_entry_menu(self, timeout):
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return self.__data_adapter.wait_for_entrymenu(r'Press \[F2\]', timeout)

    def get_current_screen_info(self):
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return self.__adapter.get_current_screen_info()

    def select(self, item_name, item_type, use_regex, timeout):
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return self.__adapter.select(item_name, item_type, use_regex, timeout)

    def goto(self, path, use_regex, timeout_config, is_page_info):
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return self.__adapter.goto(
            path, use_regex, timeout_config, is_page_info)

    def back_to_root(self, timeout, is_page_info):
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return self.__adapter.back_to_root(timeout, is_page_info)

    def enter_selected_item(self, ignore, timeout):
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return self.__adapter.enter_selected_item(ignore, timeout)

    def get_selected_item(self):
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return self.__adapter.get_selected_item()

    def get_page_information(self):
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return self.__adapter.get_page_information()

    def scan_current_page_items(self):
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        try:
            return self.__adapter.scan_current_page_items()
        except Exception as ex:
            self.__logger.error('error {0}'.format(ex))
            return ReturnData(RET_ENV_FAIL, [])

    def wait_for_popup_hightlight(self, item_name, timeout, use_regex):
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return self.__adapter.wait_for_popup_hightlight(
            item_name, timeout, use_regex)

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
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return self.__adapter.input_text(text)

    def select_from_popup(self, value, use_regex):
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
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        try:
            return self.__adapter.select_from_popup(value, use_regex, TimeoutConfig(10, 10, 10))
        except Exception as ex:
            self.__logger.debug(ex)
            return RET_ENV_FAIL

    def change_order(self, order_list):
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
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        try:
            return self.__adapter.change_order(order_list, TimeoutConfig(10, 10, 10))
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
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return self.__adapter.is_check_type()

    def wait_for_bios_ui(self, timeout):
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        self.__logger.debug("into function: timeout={0}".format(timeout))
        if timeout is None or timeout < 0:
            self.__logger.error("return:{0}".format(RET_INVALID_INPUT))
            return RET_INVALID_INPUT

        try:
            return self.__adapter.wait_for_bios_ui(timeout)
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
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        self.__logger.debug("into function: timeout={0}".format(timeout))
        if timeout is None or timeout < 0:
            self.__logger.error("return:{0}".format(RET_INVALID_INPUT))
            return RET_INVALID_INPUT

        try:
            return self.__adapter.wait_for_bios_setup_menu(timeout)
        except Exception as e:
            self.__logger.error("return:{0}, Exception={1}".format(RET_ENV_FAIL, e))
            return RET_ENV_FAIL

    def enter_efishell(self, timeout):
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
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        self.__logger.debug("into function: timeout={0}".format(timeout))
        if timeout is None or timeout < 0:
            self.__logger.error("return:{0}".format(RET_INVALID_INPUT))
            return RET_INVALID_INPUT
        try:
            entry = self._config_model.efishell_entry  # type: BiosSetupmenuProviderConfig.Entry
            config = dict(select_item=entry.select_item, path=entry.path)
            return self.__adapter.enter_efishell(timeout=timeout, enter_config=config)
        except Exception as e:
            self.__logger.error("return:{0}, Exception={1}".format(RET_ENV_FAIL, e))
            return RET_ENV_FAIL

    def continue_to_os(self):
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
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        self.__logger.debug("into function")

        try:
            entry = self._config_model.continue_entry  # type: BiosSetupmenuProviderConfig.Entry
            config = dict(select_item=entry.select_item, path=entry.path)
            return self.__adapter.continue_to_os(config)
        except Exception as e:
            self.__logger.error("return:{0}, Exception={1}".format(RET_ENV_FAIL, e))
            return RET_ENV_FAIL

    def reboot(self, timeout):
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
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        self.__logger.debug("into function: timeout={0}".format(timeout))
        if timeout is None or timeout < 0:
            self.__logger.error("return:{0}".format(RET_INVALID_INPUT))
            return RET_INVALID_INPUT

        try:
            entry = self._config_model.reset_entry  # type: BiosSetupmenuProviderConfig.Reset
            self.__logger.debug('reboot ==== > {}'.format(entry))
            config = dict(press_key=entry.press_key, parse=entry.parse)
            self.__logger.debug('reboot ==== > {}'.format(config))
            return self.__adapter.reboot(timeout, config)
        except Exception as e:
            self.__logger.error("return:{0}, Exception={1}".format(RET_ENV_FAIL, e))
            return RET_ENV_FAIL

    def get_title(self):
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        try:
            return self.__adapter.get_title()
        except Exception as ex:
            ret = ReturnData(RET_ENV_FAIL, '')
            self.__logger.error('return return_code {0}, result_value {1} ex {2}'.format(
                ret.return_code, ret.result_value, ex))
            return ret

    def check_item_repeat(self, item_list, new_item):
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return self.__adapter.check_item_repeat()

    def get_highlight_with_position(self):
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return self.__adapter.get_highlight_with_position()
