"""
Define Data Layer to parse entry menu data from serial port output
"""

import re
from dtaf_core.drivers.internal.base_serial import SerialBufferSet


class EntryMenuDataAdapter(object):
    def __init__(self, data_helper, logger):
        self.__logger = logger
        self.__data_helper = data_helper

    def press(self, input_key):
        """
            press F2 or F7 to enter BIOSSetupmenu or BIOSbootmenu.
            :param str: the only valid input is F1~F12
            :return: RET_SUCCESS: press successfully
                     RET_ENV_FAIL: press failed.
                     RET_INVALID_INPUT: input str is wrong
            dependency: g_main_serial_service.write(str)
            black box equivalent class: str=F2,F7,F6; g_main_serial_service.write(str)=SerialException,SerialTimeoutException
            estimated LOC = 10
        """
        if input_key not in ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
                             "ENTER", "UP", "DOWN", "ESC"]:
            self.__logger.error('Invalid input from {0}'.format(input_key))
            return False

        try:
            import dtaf_core.lib.private.globals.bios_menu_types as types
            str_format = eval("types.BIOS_CMD_KEY_" + input_key)
            self.__logger.debug('WRITE: [{0}] start'.format(str_format))
            self.__data_helper.write(str_format)
            self.__logger.debug('WRITE: [{0}] end'.format(str_format))
            return True
        except Exception as ex:
            self.__logger.error('press key {0} error from {1}'.format(input_key, ex))
            return False

    def wait_for_entrymenu(self, entry_flag, timeout):
        """
            parse serial output log to check if [F2] or [F7] occurred.
            :param timeout: timeout to check entering to entry menu, secs which is larger than 0
            :return: RET_SUCCESS: entry menu is entered.
                     RET_TEST_FAIL: entry menu is not entered after timeout.
                     RET_INVALID_INPUT: input timeout is wrong
            dependency: g_main_serial_service.read()
            black box equivalent class: timeout>0, timeout<=0; g_main_serial_service.read()=[F2],[F6]
            estimated LOC = 30
        """
        try:
            self.__data_helper.clean_buffer()
        except Exception as ex:
            self.__logger.error('wait for entrymenu clean buffer faild !  {}'.format(ex))

        if not isinstance(timeout, int) or not entry_flag or timeout < 0:
            self.__logger.error('Invalid input ...{0}, {1}'.format(entry_flag, timeout))
            return False

        try:
            data = self.__data_helper.read_until(entry_flag, timeout)
            detail = re.search(entry_flag, data)
            return detail
        except Exception as ex:
            self.__logger.error('wait_for_entrymenu fail from {0}'.format(ex))
            return False

    def press_key(self, input_key):
        """
        Press keys other than F1 to F12
        :param key_code:
        :param parse_data:
        :param timeout:
        :return:
        """
        try:
            import dtaf_core.lib.private.globals.bios_menu_types as types
            if input_key in ['ENTER', 'ESC', 'UP', 'DOWN', 'RIGHT',
                             'LEFT', 'PAGEUP', 'PAGEDOWN', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10',
                             'F11', 'F12', 'Y', 'N',
                             'DELETE', 'HOME', 'END', 'INSERT', 'SPACE', 'BACKSPACE', 'CTRL_ALT_DELETE', 'CTRL', 'ALT',
                             'SHIFT', 'PLUS', 'MINUS']:
                str_format = eval("types.BIOS_CMD_KEY_" + input_key)
            else:
                str_format = input_key
            self.__logger.debug('WRITE: [{0}]'.format(str_format))
            self.__data_helper.write(str_format)
            return True
        except Exception as ex:
            self.__logger.error('press key {0} error from {1}'.format(input_key, ex))
            return False
