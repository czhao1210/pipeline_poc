""""
This module is used to define data type for APIs.
It includes below data type:
    class return_data

    return_code
"""

# Enter OS type
ENTER_OS_START_UP = 'START_UP'
ENTER_OS_RESUME = 'RESUME'
# OS Message
TYPE_EXECUTE = 'EXECUTE'
TYPE_KILL = 'KILL'
TYPE_REBOOT = 'REBOOT'
TYPE_SHUTDOWN = 'SHUTDOWN'
TYPE_STANDBY = 'STANDBY'
TYPE_HIBERNATE = 'HIBERNATE'
TYPE_DELETE = 'DELETE'
TYPE_EXECUTE_ASYNC = 'EXECUTE_ASYNC'
TYPE_OPEN_FOR_WRITE = 'OPEN_FOR_WRITE'
TYPE_OPEN_FOR_READ = 'OPEN_FOR_READ'
TYPE_WRITE = 'WRITE'
TYPE_READ = 'READ'
TYPE_CLOSE = 'CLOSE'

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
        else:
            return False
