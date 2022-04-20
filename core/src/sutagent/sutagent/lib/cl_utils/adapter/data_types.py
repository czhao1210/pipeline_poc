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


