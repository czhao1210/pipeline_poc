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
import functools
from base64 import b64encode


def singleton(cls):
    """
    Singleton decorator

    :param cls: Python class object to enforce as a singleton
    :return: Instance of cls.
    """

    instance = {}

    def get_instance(*args, **kwargs):
        """
        Get the singleton instance of the class, and instantiate it if wasn't already.

        :param args: Positional arguments passed to the constructor of the class
        :param kwargs: Nominal arguments passed to the constructor of the class
        :return: Instance of cls associated with this singleton function
        """
        if cls not in instance.keys():
            instance[cls] = cls(*args, **kwargs)
        return instance[cls]

    return get_instance


def Shared(**kw):
    __instances = dict()
    __keys = kw["key"]
    if isinstance(kw["key"], str):
        __keys = [kw["key"]]

    def _cls(cls):
        @functools.wraps(cls)
        def _wrapper(*args, **kwargs):
            __ser_key = b64encode((":".join(["{}".format(kwargs[k]) for k in __keys])).encode()).decode()
            if __ser_key not in __instances.keys():
                __instances[__ser_key] = cls(*args, **kwargs)
            return __instances[__ser_key]

        return _wrapper

    return _cls
