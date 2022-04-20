from sutagent.lib.cl_utils.communication.task import Task
from importlib import import_module
from sutagent.lib.cl_utils.communication.message_pool import send_message
import pickle


class ExecutionTask(Task):
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
        ctx = None
        try:
            try:
                func_name = self.__msg_data[r'func_name']
                mod_name = self.__msg_data[r'mod_name']
                args = pickle.loads(self.__msg_data[r'args'])
                kwargs = pickle.loads(self.__msg_data[r'kwargs'])

                mod = import_module(mod_name)
                func = getattr(mod, func_name)

                print(r'execute func %s' % func.__name__)
                return_data = func(*args, **kwargs)
                return_data = pickle.dumps(return_data)

                msg_data = dict(
                    execute_success=True,
                    func_return=return_data,
                    err_msg=''
                )
            except Exception as ex:
                print(r'ExecutionTask: ex={0}, {1}'.format(ex, self.__msg_data))
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
            print('stop ExecutionTask... {0}'.format(self.__key))
        except Exception as ex:
            print('ExecutionTask {0}'.format(ex))
        finally:
            if ctx:
                ctx.term()
                ctx = None
            self.set_is_running(False)


class ExecutionReturnTask(Task):
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
        try:
            json_data = dict(
                key=self.__key,
                src=self.__src,
                dest=self.__dest,
                type=self.__msg_type,
                msg=self.__msg_data
            )
            self.__observer.post_message(json_data)
            print('ExecutionReturnTask: {0}'.format(json_data))
        except Exception as ex:
            print('ExecutionReturnTask: ex={0}'.format(ex))
        finally:
            self.set_is_running(False)
