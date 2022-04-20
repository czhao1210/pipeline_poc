'''
data_types
'''


"""
SUCCESS
"""
RET_SUCCESS = r'SUCCESS'

"""
TEST FAILURE (Suspected)
UNKNOWN FAILURE
"""
RET_TEST_FAIL = r'TEST_FAIL'
"""
ENV FAILURE
"""
RET_ENV_FAIL = r'ENV_FAIL'
"""
input parameters are invalid
"""
RET_INVALID_INPUT = r'INVALID_INPUT'

BIOS_UI_OPT_TYPE = r'OPTION_TYPE'
BIOS_UI_DIR_TYPE = r'DIR_TYPE'
BIOS_UI_INPUT_TYPE = r'INPUT_TYPE'
BIOS_UI_POPUP_TYPE = r'POPUP_TYPE'
BIOS_UI_VALUE_TYPE = r'VALUE_TYPE'

BIOS_SETUP_MENU_TYPE = r'BIOS_SETUP_MENU'
BIOS_BOOT_MENU_TYPE = r'BIOS_BOOT_MENU'

BIOS_CMD_KEY_ENTER = '\r'
BIOS_CMD_KEY_ESC = '\33'+' '
BIOS_CMD_KEY_UP = '\33'+'[A'
BIOS_CMD_KEY_DOWN = '\33'+'[B'
BIOS_CMD_KEY_RIGHT = '\33'+'[C'
BIOS_CMD_KEY_LEFT = '\33'+'[D'
BIOS_CMD_KEY_PAGEUP = '\33'+'?'
BIOS_CMD_KEY_PAGEDOWN = '\33'+'/'
BIOS_CMD_KEY_F1 = '\33'+'1'
BIOS_CMD_KEY_F2 = '\33'+'2'
BIOS_CMD_KEY_F3 = '\33'+'3'
BIOS_CMD_KEY_F4 = '\33'+'4'
BIOS_CMD_KEY_F5 = '\33'+'5'
BIOS_CMD_KEY_F6 = '\33'+'6'
BIOS_CMD_KEY_F7 = '\33'+'7'
BIOS_CMD_KEY_F8 = '\33'+'8'
BIOS_CMD_KEY_F9 = '\33'+'9'
BIOS_CMD_KEY_F10 = '\33'+'0'
BIOS_CMD_KEY_F11 = '\33'+'!'
BIOS_CMD_KEY_F12 = '\33'+'@'
BIOS_CMD_KEY_Y = 'y'
BIOS_CMD_KEY_N = 'n'
BIOS_CMD_KEY_DELETE = '\33'+'-'
BIOS_CMD_KEY_HOME = '\33'+'h'
BIOS_CMD_KEY_END = '\33' + 'k'
BIOS_CMD_KEY_INSERT = '\33' + '+'
BIOS_CMD_KEY_SPACE = ' '
BIOS_CMD_KEY_BACKSPACE = '\10'
BIOS_CMD_KEY_CTRL_ALT_DELETE = '\33R\33r\33R'
BIOS_CMD_KEY_CTRL = '\21'
BIOS_CMD_KEY_ALT = '\22'
BIOS_CMD_KEY_SHIFT = '\20'
BIOS_CMD_KEY_PLUS = '\20' + '+'
BIOS_CMD_KEY_MINUS = '\20' + '-'


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


class TimeoutConfig(object):
    """
    This Class defines time out configuration of API

    including timeout and hearbeats when operation inside a bios menu page (move highlight, input text)

    including timeout and hearbeats when enter or exist a bios menu page
    """
    def __init__(self, total_timeout, navigation_timeout, inner_move_timeout):
        """
        initialize Bios Menu Timeout object

        :param internal_timeout: timeout to get the first data for internal action in a bios menu page
        (e.g. move highlight, input text)

        :param navigation_timeout: timeout to get the first data when navigating bios page
        """
        self.__total_timeout = total_timeout
        self.__navigation_timeout = navigation_timeout
        self.__inner_move_timeout = inner_move_timeout

    @property
    def inner_move_timeout(self):
        """
        the property of inner_move_timeout

        :return:
        """
        return self.__inner_move_timeout

    @property
    def navigation_timeout(self):
        """
        timeout when navigating

        :return:
        """
        return self.__navigation_timeout

    @property
    def total_timeout(self):
        return self.__total_timeout
