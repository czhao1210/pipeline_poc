""""
This module is used to define data type for APIs.
It includes below data type:
    class return_data

    return_code
"""

# Enter OS type
ENTER_OS_START_UP = 'START_UP'
ENTER_OS_RESUME = 'RESUME'

BIOS_SETUP_MENU_TYPE = r'BIOS_SETUP_MENU'
BIOS_BOOT_MENU_TYPE = r'BIOS_BOOT_MENU'

BIOS_HIGHLIGHT_INTO_POPUP = 'INTO_POPUP'
BIOS_HIGHLIGHT_BACK_TO_ROOT = 'BACK_ROOT'
BIOS_HIGHLIGHT_NORMAL = 'HIG_NORMAL'
BIOS_HIGHLIGHT_WAIT_MENU = 'WAIT_MENU'

SECTION_NAME = "BiosMenu"
NAVIGATION_TIMEOUT = 60

INTERNAL_TIMEOUT = 5

try:
    import os

    RESOLUTION = r""
    if RESOLUTION not in ["24x80", "31x100"]:
        RESOLUTION = "24x80"
    if RESOLUTION == "24x80":
        SCREEN_WIDTH = 80
        SCREEN_HIGH = 24
    elif RESOLUTION == "31x100":
        SCREEN_WIDTH = 100
        SCREEN_HIGH = 31
    else:
        SCREEN_WIDTH = 80
        SCREEN_HIGH = 24
except Exception as ex:
    SCREEN_WIDTH = 80
    SCREEN_HIGH = 24

PYTE_RESOLUTION_CONFIG_8024 = {
    "bios_boot_menu": {
        "border": {"Normal":
                       {"top": {"cnd": ".{1}[-]{5}.*[-]{5}.{1}", "pos": "[ /][-]{5}.*[-]{5}[ \\\\]"},
                        "left": "[|]",
                        "right": "[ |]",
                        "mid": "[|][-]{5}.*[-]{5}[| ]",
                        "bottom": "[ \\\\][-]{5}.*[-]{5}[ /]",
                        "border_color": ("blue", "white"),
                        "item_color": ("blue", "white"),
                        "highlight_color": ("black", "white"),
                        "position": (0, 24)}}},
    "bios_setup_menu": {
        "border": {"header":
                       {"top": "[ /]-{5}.{50}.*-{5}[ \\\\]",
                        "left": "[|]",
                        "right": "[ |]",
                        "bottom": "[ \\\\][-]{5}.{50}.*[-]{5}[ /]",
                        "border_color": ("blue", "white"),
                        "item_color": ("blue", "white"),
                        "highlight_color": ("blue", "white"),
                        "default_color": ("default", "default"),
                        "position": (0, 5)},
                   "popup":
                       {"top": {"cnd": ".{1}[-]{2}.*[-]{2}.{1}", "pos": "[/][-]{2}.*[-]{2}[ \\\\]"},
                        "left": "[|]",
                        "right": "[ |]",
                        "mid": "[|][-]{2}.*[-]{2}[| ]",
                        "bottom": "[ \\\\][-]{2}.*[-]{2}[ /]",
                        "border_color": ("blue", "white"),
                        "item_color": ("blue", "white"),
                        "highlight_color": ("cyan", "white"),
                        "default_color": ("default", "default"),
                        "position": (2, 23),
                        "min_start_col": 2},
                   "tail":
                       {"top": "[ /]-{5}.{50}.*-{5}[ \\\\]",
                        "left": "[|]",
                        "right": "[ |]",
                        "bottom": "[ \\\\]-{5}.{50}.*[ -]{5}[ /]",
                        "border_color": ("blue", "white"),
                        "item_color": ("black", "white"),
                        "highlight_color": ("black", "black"),
                        "default_color": ("default", "default"),
                        "position": (18, 24)}},
        "workspace": {"item_color": ("white", "black"),
                      "highlight_color": ("black", "white"),
                      "item_value_start_column": 30,
                      "item_type_flag": "",
                      "description_color": ("white", "blue"),
                      "description_start_column": 57,
                      "prev_page_flag": {"charset": u'^', "color": ('white', 'red')},
                      "next_page_flag": {"charset": u'v', "color": ('white', 'red')},
                      "split_bg_color": "white"
                      }
    }
}

PYTE_RESOLUTION_CONFIG_10031 = {
    "bios_boot_menu": {
        "border": {"Normal":
                       {"top": {"cnd": ".{1}[-]{5}.*[-]{5}.{1}", "pos": "[ /][-]{5}.*[-]{5}[ \\\\]"},
                        "left": "[|]",
                        "right": "[ |]",
                        "mid": "[|][-]{5}.*[-]{5}[| ]",
                        "bottom": "[ \\\\][-]{5}.*[-]{5}[ /]",
                        "border_color": ("blue", "white"),
                        "item_color": ("blue", "white"),
                        "highlight_color": ("black", "white"),
                        "position": (0, 31)}}},
    "bios_setup_menu": {
        "border": {"header":
                       {"top": "[ /]-{5}.{70}.*-{5}[ \\\\]",
                        "left": "[|]",
                        "right": "[ |]",
                        "bottom": "[ \\\\][-]{5}.{70}.*[-]{5}[ /]",
                        "border_color": ("blue", "white"),
                        "item_color": ("blue", "white"),
                        "highlight_color": ("blue", "white"),
                        "default_color": ("default", "default"),
                        "position": (0, 6)},
                   "popup":
                       {"top": {"cnd": ".{1}[-]{2}.*[-]{2}.{1}", "pos": "[ /][-]{2}.*[-]{2}[ \\\\]"},
                        "left": "[|]",
                        "right": "[ |]",
                        "mid": "[|][-]{2}.*[-]{2}[| ]",
                        "bottom": "[ \\\\][-]{2}.*[-]{2}[ /]",
                        "border_color": ("blue", "white"),
                        "item_color": ("blue", "white"),
                        "highlight_color": ("cyan", "white"),
                        "default_color": ("default", "default"),
                        "position": (2, 30),
                        "min_start_col": 2},
                   "tail":
                       {"top": "[ /]-{5}.{70}.*-{5}[ \\\\]",
                        "left": "[|]",
                        "right": "[ |]",
                        "bottom": "[ \\\\]-{5}.{70}.*[ -]{5}[ /]",
                        "border_color": ("blue", "white"),
                        "item_color": ("black", "white"),
                        "highlight_color": ("black", "black"),
                        "default_color": ("default", "default"),
                        "position": (25, 31)}},
        "workspace": {"item_color": ("white", "black"),
                      "highlight_color": ("black", "white"),
                      "item_value_start_column": 36,
                      "item_type_flag": "",
                      "description_color": ("white", "blue"),
                      "description_start_column": 70,
                      "prev_page_flag": {"charset": u'^', "color": ('white', 'red')},
                      "next_page_flag": {"charset": u'v', "color": ('white', 'red')},
                      "split_bg_color": "white"
                      }
    }
}

# OS Message
TYPE_EXECUTE = 'EXECUTE'
TYPE_KILL = 'KILL'
TYPE_REBOOT = 'REBOOT'
TYPE_SHUTDOWN = 'SHUTDOWN'
TYPE_STANDBY = 'STANDBY'
TYPE_HIBERNATE = 'HIBERNATE'
TYPE_DELETE = 'DELETE'
TYPE_EXECUTE_ASYNC = 'EXECUTE_ASYNC'

TYPE_ENTEROS = 'ENTEROS'
TYPE_RESPONSE = 'RESPONSE'


class ReturnData(object):
    """
    This class defines the return data of API

    It is recommended to return this object,
    in the case that return code is not enough to specify the result of APIs
    """

    def __init__(self, return_code, result_value):
        """
        initialize return data object

        :param return_code: return code see below return_code.py for details.

        :param result_value: should be the result of APIs. It depends on API design.

        Some APIs may return the bios related data in this APIs.
        """
        self.__return_code = return_code
        self.__return_value = result_value

    @property
    def return_code(self):
        """
        the property of return code

        :return: return code
        """
        return self.__return_code

    @property
    def result_value(self):
        """
        the property of result value

        :return: result value
        """
        return self.__return_value

    def __cmp__(self, other):
        if other.return_code == self.return_code and \
                other.result_value == self.result_value:
            return True
        return False


class BiosMenuTimeout(object):
    """
    This Class defines time out configuration of API

    including timeout and hearbeats when operation inside a bios menu page (move highlight, input text)

    including timeout and hearbeats when enter or exist a bios menu page
    """

    def __init__(self, timeout_internal, timeout_navigation):
        """
        initialize Bios Menu Timeout object

        :param timeout_internal: timeout to get the first data for internal action in a bios menu page
        (e.g. move highlight, input text)

        :param timeout_navigation: timeout to get the first data when navigating bios page
        """
        self.__internal_timeout = timeout_internal
        self.__navigation_timeout = timeout_navigation

    @property
    def internal_timeout(self):
        """
        the property of internal timeout

        :return:
        """
        return self.__internal_timeout

    @property
    def navigation_timeout(self):
        """
        timeout when navigating

        :return:
        """
        return self.__navigation_timeout
