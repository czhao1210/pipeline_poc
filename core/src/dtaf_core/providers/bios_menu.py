#!/usr/bin/env python
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
from abc import ABCMeta, abstractmethod

from six import add_metaclass

from dtaf_core.providers.base_provider import BaseProvider


@add_metaclass(ABCMeta)
class BiosMenuProvider(BaseProvider):
    """
    Class that manipulate BIOS Menu UI for testing

    This class cannot be used directly, instead, this interface is applied to the subclasses, with a different subclass
    communication (SOL, Serial) This makes the dependency on specific hardware setups easier to
    identify.
    """
    DEFAULT_CONFIG_PATH = "suts/sut/providers/bios_bootmenu"

    def __init__(self, cfg_opts, log):
        """
        Create a new BiosMenuProvider object

        :param self._log: Logger object to use for debug and info messages
        :param cfg_opts: Dictionary of configuration options for execution environment.
        """
        super(BiosMenuProvider, self).__init__(cfg_opts, log)


@add_metaclass(ABCMeta)
class BiosBootMenuProvider(BiosMenuProvider):

    DEFAULT_CONFIG_PATH = "suts/sut/providers/bios_bootmenu"

    """
    Class that manipulate BIOS Menu UI for testing

    This class cannot be used directly, instead, this interface is applied to the subclasses, with a different subclass communication (SOL, Serial). This makes the dependency on specific hardware setups easier to identify.
    """
    DEFAULT_CONFIG_PATH = "suts/sut/providers/bios_bootmenu"
    def __init__(self, cfg_opts, log):
        """
        Create a new BiosMenuProvider object

        :param self._log: Logger object to use for debug and info messages
        :param cfg_opts: Dictionary of configuration options for execution environment.
        """
        super(BiosBootMenuProvider, self).__init__(cfg_opts, log)

    @abstractmethod
    def select(self, item_name, item_type, timeout, use_regex):
        # type:(str, str, int, bool) -> str
        """
        select an item on bios boot menu page

        :param item_name: item name to select
        :param item_type: item type (None, BIOS_UI_OPT_TYPE, BIOS_UI_DIR_TYPE, BIOS_UI_INPUT_TYPE)
        :param timeout: the overall timeout to receive the first data
        :param use_regex: whether to use regress expression to match the item (True / False)
        :return: True / False verify whether the specified item can be selected
        :raise NotImplementedError:  if it has not been implemented yet.
        :raise DriverIOError: if command execution failed in driver
        :raise TimeoutException: fail to respond before timeout
        :raise ItemNotFoundException: fail to find the specific item
        """
        raise NotImplementedError

    def enter_selected_item(self, timeout, ignore_output):
        # type:(int, bool) -> bool
        """
        enter the selected item on bios menu page

        :param timeout: the overall timeout to receive the first data
        :param ignore_output: indicate whether to ignore the output after enter. It is usually used for the item to enter different env (e.g. EFISHell)
        :return: True / False successfully enter the bios item
        :raise NotImplementedError:  if it has not been implemented yet.
        :raise DriverIOError: if command execution failed in driver
        :raise TimeoutException: fail to respond before timeout
        :raise ItemNotFoundException: no valid item is selected
        """
        raise NotImplementedError

    def get_selected_item(self):
        # type:() -> tuple
        """
        get selected item in format of ReturnData
        :return:    (name, type, subtitle, value)
        :raise NotImplementedError:  if it has not been implemented yet.
        :raise DriverIOError: if command execution failed in driver
        :raise TimeoutException: fail to respond before timeout
        :raise ItemNotFoundException: no valid item is selected.
        """
        raise NotImplementedError

    def get_page_information(self):
        # type:() -> list
        """
        get information on current bios menu page in format of list ([(name, value),...])

        :return:    a list of bios item in format of (name, value). It will be [] if no information.
        :raise NotImplementedError:  if it has not been implemented yet.
        :raise DriverIOError: if command execution failed in driver
        """
        raise NotImplementedError

    def wait_for_bios_boot_menu(self, timeout):
        # type:(int) -> bool
        """
        wait sut to enter bios setup menu until timeout

        :param timeout: timeout to wait
        :return:
            True    -   sut entered bios boot menu before timeout
            False   -   sut didn't bios boot menu withing timeout
        :raise NotImplementedError:  if it has not been implemented yet.
        :raise DriverIOError: if command execution failed in driver
        :raise TimeoutException: fail to respond due to HW / SW defects in core library.
        """
        raise NotImplementedError

    def enter_efishell(self, timeout):
        # type: (int) -> bool
        """
        move to UEFI Shell from bios menu

        :param timeout:
        :return:
            True    -   sut entered bios boot menu before timeout
            False   -   sut didn't bios boot menu withing timeout
        :raise NotImplementedError:  if it has not been implemented yet.
        :raise DriverIOError: if command execution failed in driver
        :raise TimeoutException: fail to respond due to HW / SW defects in core library.
        """
        raise NotImplementedError

    def reboot(self, timeout):
        # type: (int) -> str
        """
        reboot

        :param timeout:    the api call is expected to return within timeout
        :return:    True / False if reboot started
        :raise NotImplementedError:  if it has not been implemented yet.
        :raise IOError: if any unexpected/corrupted data found
        :raise EnvironmentError: if communication connection corrupted
        """
        raise NotImplementedError


@add_metaclass(ABCMeta)
class BiosSetupMenuProvider(BiosMenuProvider):
    DEFAULT_CONFIG_PATH = "suts/sut/providers/bios_setupmenu"
    """
    Class that manipulate BIOS Menu UI for testing

    This class cannot be used directly, instead, this interface is applied to the subclasses, with a different subclass
    communication (SOL, Serial) This makes the dependency on specific hardware setups easier to
    identify.
    """
    DEFAULT_CONFIG_PATH = "suts/sut/providers/bios_setupmenu"
    def __init__(self, cfg_opts, log):
        """
        Create a new BiosMenuProvider object

        :param self._log: Logger object to use for debug and info messages
        :param cfg_opts: Dictionary of configuration options for execution environment.
        """
        super(BiosSetupMenuProvider, self).__init__(cfg_opts, log)

    def get_current_screen_info(self):
        # type:() -> list
        """
        get all the information on current screen for user to collect information

        :return: a list of information on page
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise IOError: if any unexpected/corrupted data found
        :raise EnvironmentError: if communication connection corrupted  
        """
        raise NotImplementedError

    def wait_for_entry_menu(self, timeout):
        # type:(int) -> bool
        """
        wait SUT to enter entry menu. F2 is expected to input once SUT is in entry menu.

        :param timeout:  timeout to wait for the entry menu
        :return: True / False  whether we get into entry menu successfully.
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise IOError: if any unexpected/corrupted data found
        :raise EnvironmentError: if communication connection corrupted
        :raise TimeoutException: if API call gets timeout due to hardware or software defect
        """
        raise NotImplementedError

    def select(self, item_name, item_type, use_regex, timeout):
        # type:(str, str, bool, int) -> str
        """
        select an item on bios menu page

        :param item_name: item name to select
        :param item_type: item type (None, BIOS_UI_OPT_TYPE, BIOS_UI_DIR_TYPE, BIOS_UI_INPUT_TYPE)
        :param use_regex: whether to use regress expression to match the item (True / False)
        :param timeout: the overall timeout to receive the first data
        :return:
            True -  Bios Setup Menu is selected
            False - Not item found in the specified path
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise IOError: if any unexpected/corrupted data found
        :raise EnvironmentError: if communication connection corrupted
        :raise TimeoutException: if API call gets timeout
        """
        raise NotImplementedError

    def goto(self, path, use_regex, timeout_config, is_page_info):
        # type:(list, bool, tuple, bool) -> bool
        """
        goto the bios menu page specified in path:
        transverse the folder name in path, move highlight to that directory and press key to enter bios menu

        :param path: the path to the target bios menu page.
                all the directry names in path are stored in this list
                each element in list are stored as string
        :param use_regex: indicate whether to use regular expression
        :param timeout_config:
            timeout for internal operation inside bios menu
            timeout for nagivating (enter or exit bios menu page)
        :param is_page_info:
            flag to indicate whether to parse page info
        :return:    True / False
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise IOError: if any unexpected/corrupted data found
        :raise EnvironmentError: if communication connection corrupted
        :raise TimeoutException: if API call gets timeout
        """
        raise NotImplementedError

    def back_to_root(self, timeout, is_page_info):
        # type:(int, bool) -> bool
        """
        press esc key to go back to the root bios page

        :param timeout: timeout to get first data
        :param is_page_info: flag to indicate whether to parse page info
        :return:    True / False  return False if already in root page.
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise IOError: if any unexpected/corrupted data found
        :raise EnvironmentError: if communication connection corrupted
        :raise TimeoutException: if API call gets timeout
        """
        raise NotImplementedError

    def enter_selected_item(self, ignore, timeout):
        # type:(bool, int) -> bool
        """
        press enter on selected item

        :param ignore: indicates whether to ignore the coming data
        :param timeout: timeout to get first data
        :return:    True / False
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise IOError: if any unexpected/corrupted data found
        :raise EnvironmentError: if communication connection corrupted
        :raise TimeoutException: if API call gets timeout
        """
        raise NotImplementedError

    def get_selected_item(self):
        # type:() -> tuple
        """
        get selected item in format of ReturnData.
        :return: (name, type, subtitle, value) name - bios knobs name on UI, type - option, directory, Unknown Type; subtitle - the information shown on the right panel; value - knobs value
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise DriverIOError: if command execution failed in driver
        :raise ItemNotFoundException: not valid item is selected
        """
        raise NotImplementedError

    def get_page_information(self):
        # type:() -> ReturnData
        """
        get current page info in format of dictionary (key,value)

        :return:    page information in a list of (key, value)
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise IOError: if any unexpected/corrupted data found
        :raise EnvironmentError: if communication connection corrupted
        """
        raise NotImplementedError

    def scan_current_page_items(self):
        # type:() -> ReturnData
        """
        scan the current page for bios items information

        :return:    None
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise IOError: if any unexpected/corrupted data found
        :raise EnvironmentError: if communication connection corrupted
        """
        raise NotImplementedError

    def wait_for_popup_hightlight(self, item_name, timeout, use_regex):
        # type:(str, int, bool) -> bool
        """
        wait for a bios popup when selecting the bios item

        :param item_name:  provide the bios item name which triggered the popup
        :param timeout: timeout to wait for popup
        :param use_regex: flag whether to use regular expression
        :return:    True / False
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise IOError: if any unexpected/corrupted data found
        :raise EnvironmentError: if communication connection corrupted
        :raise TimeoutException: if API call gets timeout
        """
        raise NotImplementedError

    def press_key(self, key_code, not_ignore, timeout):
        # type:(str, bool, int) -> bool
        """
        press enter on selected item

        :param key_code: key code (all non-empty data is supported)
        :param not_ignore: indicates whether to ignore the coming data
        :param timeout: timeout to get first data
        :return:    True / False
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise IOError: if any unexpected/corrupted data found
        :raise EnvironmentError: if communication connection corrupted
        :raise TimeoutException: if API call gets timeout
        """
        raise NotImplementedError

    def input_text(self, text):
        # type:(str) -> bool
        """
        input text

        :param text: text to input
        :return:    True / False
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise IOError: if any unexpected/corrupted data found
        :raise EnvironmentError: if communication connection corrupted
        """
        raise NotImplementedError

    def select_from_popup(self, value, use_regex):
        # type:(str, bool, tuple) -> str
        """
        select item value from popup window

        :param value: item value to select
        :param use_regex: indicates whether to use regular expression
        :param timeout_config: timeout to get first data
        :return:
            True - item is selected
            False - the specified item not found
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise IOError: if any unexpected/corrupted data found
        :raise EnvironmentError: if communication connection corrupted
        :raise TimeoutException: if API call gets timeout
        """
        raise NotImplementedError

    def change_order(self, order_list):
        # type:(list, tuple) -> bool
        """
        change the order of item listed in popup window

        :param order_list: the ordered list of items
        :return:    True / False
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise IOError: if any unexpected/corrupted data found
        :raise EnvironmentError: if communication connection corrupted
        :raise TimeoutException: if API call gets timeout
        """
        raise NotImplementedError

    def is_check_type(self):
        # type: () -> bool
        """
        return whether it is check type

        :return:
            True: if the selected item is check box
            False: if the selected item is not check box
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise ItemNotFoundException: No valid item is selected
        """
        raise NotImplementedError

    def wait_for_bios_setup_menu(self, timeout):
        # type: (int) -> bool
        """
        wait sut to enter bios setup menu until timeout

        :param timeout: timeout to get first data
        :return: True / False
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise DriverIOError: if command execution failed in driver
        :raise TimeoutException: fail to respond before timeout
        """
        raise NotImplementedError

    def enter_efishell(self, timeout):
        # type: (int) -> bool
        """
        wait sut to enter efishell until timeout

        :param timeout: timeout to get first data
        :return:    True / False
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise IOError: if any unexpected/corrupted data found
        :raise EnvironmentError: if communication connection corrupted
        :raise TimeoutException: if API call gets timeout
        """
        raise NotImplementedError

    def continue_to_os(self):
        # type: () -> bool
        """
        select continue menu and enter

        :return:    True / False
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise DriverIOError: if command execution failed in driver
        """
        raise NotImplementedError

    def reboot(self, timeout):
        # type: (int) -> str
        """
        select reboot item trigger reboot

        :param timeout: timeout to get first data
        :return:    None
        :raise NotImplementedError:  if it ha not been implemented yet.
        :raise DriverIOError: if command execution failed in driver
        :raise TimeoutException: fail to respond before timeout
        """
        raise NotImplementedError

    def get_title(self):
        # type: () -> str
        """
        get title of current bios page

        :return: title of bios page in format of text
        :raise NotImplementedError:  if it ha not been implemented yet.
        """
        raise NotImplementedError
