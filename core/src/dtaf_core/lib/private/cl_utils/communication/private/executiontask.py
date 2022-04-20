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
from dtaf_core.lib.private.cl_utils.communication.private.task import Task
from importlib import import_module
from dtaf_core.lib.private.cl_utils.communication.private.message_pool import send_message
import zmq
import pickle


class ExecutionTask(Task):
    """Backend task to execute command"""
    def __init__(self, src, dest, msg_type, key, msg_data, observer, group=None, target=None, name=None, args=(),
                 kwargs=None, verbose=None):
        super(ExecutionTask, self).__init__(src, dest, msg_type, key, msg_data, observer, group, target, name, args,
                                            kwargs, verbose)
        self.__msg_data = msg_data
        self.__src = src
        self.__dest = dest
        self.__msg_type = msg_type
        self.__key = key
        self.__observer = observer

    def run(self):
        # type: (None) -> None
        """
        The implementation of run of thread. It is used to execute task.
        """
        ctx = None
        try:
            try:
                func_name = self.__msg_data[r'func_name']
                mod_name = self.__msg_data[r'mod_name']
                args = pickle.loads(self.__msg_data[r'args'])
                kwargs = pickle.loads(self.__msg_data[r'kwargs'])

                mod = import_module(mod_name)
                func = getattr(mod, func_name)
                return_data = func(*args, **kwargs)
                return_data = pickle.dumps(return_data)

                msg_data = dict(
                    execute_success=True,
                    func_return=return_data,
                    err_msg=''
                )
            except Exception as ex:
                msg_data = dict(
                    execute_success=False,
                    func_return=None,
                    err_msg=str("{0}").format(ex)
                )

            json_data = dict(
                src=self.__dest,
                dest=self.__src,
                key=self.__key,
                type=r'execution_return',
                msg=msg_data
            )
            ctx = zmq.Context()
            send_message(ctx, json_data, self.__src)
            ctx.term()
            ctx = None
        except Exception as ex:
            raise ex
        finally:
            if ctx:
                ctx.term()
                ctx = None
            self.set_is_running(False)


class ExecutionReturnTask(Task):
    """Return Data to Client"""
    def __init__(self, src, dest, msg_type, key, msg_data, observer, group=None, target=None, name=None, args=(),
                 kwargs=None, verbose=None):
        super(ExecutionReturnTask, self).__init__(src, dest, msg_type, key, msg_data, observer, group, target, name, args,
                                            kwargs, verbose)
        self.__msg_data = msg_data
        self.__src = src
        self.__dest = dest
        self.__msg_type = msg_type
        self.__key = key
        self.__observer = observer

    def run(self):
        """
        The implementation of run function.
        """
        try:
            json_data = dict(
                key=self.__key,
                src=self.__src,
                dest=self.__dest,
                type=self.__msg_type,
                msg=self.__msg_data
            )
            self.__observer.post_message(json_data)
        except Exception as ex:
            raise ex
        finally:
            self.set_is_running(False)
