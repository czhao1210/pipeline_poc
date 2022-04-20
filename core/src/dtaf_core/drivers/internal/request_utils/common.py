import functools

from dtaf_core.lib.exceptions import DriverIOError


class HandleResponse(object):
    def __init__(self, response_type='status_code', need_allocate=False):
        """
        This decorator is used to handle http(https) returns

        :param response_type: type of the response body
        :raise DriverIOError: if response status code is failed
        """
        self.response_type = response_type
        self.need_allocate = need_allocate

    def __call__(self, func):
        @functools.wraps(func)
        def inner(obj, *args, **kwargs):
            if self.need_allocate and not obj.allocated:
                raise DriverIOError('you should allocate success first')
            res = func(obj, *args, **kwargs)
            if res.status_code == obj.STATUS_CODE.BAD_REQUEST:
                raise DriverIOError(obj.to_dict(res.json()).get('_message'))
            if self.response_type == 'status_code':
                return res.status_code == obj.STATUS_CODE.SUCCESS
            elif self.response_type == 'json':
                return res.json()
            elif self.response_type:
                return getattr(res, self.response_type)
            else:
                return res

        return inner
