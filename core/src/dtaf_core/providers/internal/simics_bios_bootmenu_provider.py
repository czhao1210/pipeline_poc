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

from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.lib.private.cl_utils.adapter.data_types import RET_SUCCESS
from dtaf_core.lib.private.context import ContextInstance as _ContextInstance
from dtaf_core.providers.bios_menu import BiosBootMenuProvider
from dtaf_core.drivers.internal.simics_driver import SimicsDriver
from dtaf_core.lib.private.provider_config.bios_bootmenu_provider_config import BiosBootmenuProviderConfig
from xml.etree.ElementTree import Element, tostring
import xmltodict


@add_metaclass(ABCMeta)
class SimicsBiosBootmenuProvider(BiosBootMenuProvider):
    def __init__(self, cfg_opts, log):
        super(SimicsBiosBootmenuProvider, self).__init__(cfg_opts, log)
        self.__width = self._config_model.width
        self.__height = self._config_model.height
        self.__logger = log
        self.buffer_name = 'bootmenu_buffer_{}'.format(self._config_model.driver_cfg.host)
        driver_cfg = None
        if isinstance(self._cfg, Element):
            driver_cfg = ConfigurationHelper.get_driver_config(provider=self._cfg,
                                                               driver_name=self._config_model.driver_cfg.name)
        elif isinstance(self._cfg, dict):
            driver_cfg = self._cfg["driver"]
        self.__driver = DriverFactory.create(driver_cfg, self.__logger)  # type: SimicsDriver
        self.__driver.register(buffer_name=self.buffer_name)
        self.__adapter = \
            _ContextInstance.get(self.__driver.SerialChannel, logger=self.__logger, buffer_name=self.buffer_name,
                                 width=self.__width, high=self.__height).data_adapter[
                'boot_menu']
        self.__data_adapter = \
            _ContextInstance.get(self.__driver.SerialChannel, logger=self.__logger,
                                 buffer_name=self.buffer_name, width=self.__width, high=self.__height).data_adapter[
                'entry_menu']
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

    def press_key(self, input_key, not_ignore=True, timeout=15):
        """
        Press keys other than F1 to F12
        :param key_code:
        :param parse_data:
        :param timeout:
        :return:
        """
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return self.__data_adapter.press_key(input_key)

    def wait_for_entry_menu(self, timeout):
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return self.__data_adapter.wait_for_entrymenu(r'Press \[F7\]', timeout)

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
                item_name (item_name on bios menu, item name which can not be found on
                    bios menu, non-string)
                item_type (BIOS_UI_OPT_TYPE, BIOS_UI_DIR_TYPE, BIOS_UI_INPUT_TYPE, None)
                use_regex (True, False)
                bios_menu_helper.press key return: (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL,
                    RET_INVALID_INPUT)
                bios_menu_helper.parse return: (RET_SUCCESS, RET_ENV_TEST, RET_TEST_FAIL,
                    RET_INVALID_INPUT)
                timeout:    [0, infinite)
            invalid:
                item name (Non-string)
                item type (None-string, String value out out of BIOS_UI_OPT_TYPE, BIOS_UI_DIR_TYPE,
                    BUID_UI_INPUT_TYPE)
                use_regex: Non-boolean
                press key return: value of out defined Return value
                parse return: value of out defined Return value
                timeout: (negative infinite, 0)
        LOC: 50
        """
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return RET_SUCCESS == self.__adapter.select(item_name, item_type, timeout, use_regex)

    def enter_selected_item(self, timeout, ignore_output):
        """
        enter the selected item on bios menu page
        :param timeout: the overall timeout to receive the first data
        :param ignore_output: indicate whether to ignore the output after enter.
        it is usually used for the item to enter different env (e.g. EFISHell)
        :return:
            RET_SUCCESS -   enter item successfully.
            RET_TEST_FAIL   -  no item is selected. enter selected item, ignore_output=False,
                but no output
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
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return RET_SUCCESS == self.__adapter.enter_selected_item(timeout, ignore_output)

    def get_selected_item(self):
        """
        get selected item in format of ReturnData
        :return:
        instance of ReturnData:
            Return Code:
                RET_SUCCESSRET_TEST_FAIL|RET_ENV_FAIL|RET_INVALID_INPUT:
                    return value should be exactly the same as
                     the most recent call of bios_menu_helper.parse|bios_menu_helper.
                        wait_for_highlight
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
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return self.__adapter.get_selected_item().result_value

    def get_page_information(self):
        """
        get information on current bios menu page in format of list: [(name, value),...]
        :return:
        instance of ReturnData:
            return code:
                RET_SUCCESSRET_TEST_FAIL|RET_ENV_FAIL|RET_INVALID_INPUT:
                    return value should be exactly the same as
                     the most recent call of bios_menu_helper.parse|bios_menu_helper.
                        wait_for_highlight
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
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return self.__adapter.get_page_information()

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
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return RET_SUCCESS == self.__adapter.wait_for_bios_boot_menu(timeout)

    def enter_efishell(self, timeout):
        """
        transition from current state to EFIShell
        it will choose Launch EFIShell to enter efi
        :param timeout:
        :return:
            RET_SUCCESS: if enter efishell successfully
            RET_TEST_FAIL: if can not enter efishell within timeout, or can not find the LAUNCH
                option
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
        self.__driver.start()
        entry = self._config_model.efishell_entry  # type: BiosBootmenuProviderConfig.Entry
        config = dict(select_item=entry.select_item, path=entry.path)
        return RET_SUCCESS == self.__adapter.enter_efishell(
            enter_config=config, timeout=timeout)

    def reboot(self, timeout):
        """
        reboot to entry menu
        return RET_SUCCESS when the text content of entry menu, which is 'F2 to enter bios
            setup menu' is found
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
        self.__driver.start()
        self.__driver.register(buffer_name=self.buffer_name)
        return RET_SUCCESS == self.__adapter.reboot(timeout)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__driver.stop()

    def __enter__(self):
        self.__driver.start()
        return self

    def close(self):
        self.__driver.stop()
