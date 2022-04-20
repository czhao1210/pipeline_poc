import time
from threading import Lock
from threading import Thread
import zmq
from dtaf_core.lib.private.cl_utils.communication.private.executiontask import ExecutionTask, ExecutionReturnTask
from dtaf_core.lib.private.cl_utils.communication.private.message_pool import MessageMonitor


class ReceiveService(object):
    __service = None

    @classmethod
    def set(cls, service):
        cls.__service = service

    @classmethod
    def get(cls):
        return cls.__service


class ExecutionService(Thread):
    __service = None
    __lock = Lock()
    __bind_port = None

    EXECUTION_RETURN_TYPE = "execution_return"
    EXECUTION_TYPE = "execution"

    @staticmethod
    def get(local_address, port):
        if not ExecutionService.__service:
            ExecutionService.__service = ExecutionService(local_address, port)
        return ExecutionService.__service

    @property
    def bind_port(self):
        return self.__bind_port

    @property
    def bind_address(self):
        return self.__bind_ip

    @property
    def address(self):
        return self.__address

    def __init__(self, local_address, bind_port, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        super(ExecutionService, self).__init__(group, target, name, args, kwargs, verbose)

        self.__context = zmq.Context()
        self.__receiver = self.__context.socket(zmq.REP)
        if not local_address:
            local_address = '127.0.0.1'

        self.__bind_ip = local_address
        if bind_port:
            self.__address = r'tcp://{0}:{1}'.format(local_address, bind_port)
            self.__receiver.bind(self.__address)
            self.__bind_port = bind_port
        else:
            self.__bind_port = self.__receiver.bind_to_random_port('tcp://{0}'.format(local_address),
                                                                   min_port=60000, max_port=61000,
                                                                   max_tries=100)
            self.__address = r'tcp://{0}:{1}'.format(local_address, self.__bind_port)

        self.__receiver.RCVTIMEO = 1000
        self.__receiver.setsockopt(zmq.LINGER, 0)
        self.__task_pool = []
        self.__stop = False
        self.__monitor = MessageMonitor()
        self.setDaemon(True)
        self.start()

    def get_message(self, key):
        """
        get message from remote host
        :param key: query message with key
        :return: message
        """
        # (str) => (str)
        return self.__monitor.get_message(key)

    def stop(self):
        """
        stop message service
        :return:
        """
        self.__lock.acquire()
        self.__stop = True
        self.__lock.release()
        ExecutionService.__service = None

    def run(self):
        """
        overridden function of thread
        :return:
        """
        try:
            while True:
                self.__lock.acquire()
                if self.__stop:
                    self.__lock.release()
                    break
                self.__lock.release()
                try:
                    json_data = self.__receiver.recv_json()
                    self.__process_msg(json_data)
                    self.__receiver.send("OK")
                except zmq.error.Again as error:
                    pass
                time.sleep(0.05)

        except Exception as ex:
            pass
        finally:
            try:
                for __task in self.__task_pool:
                    if not __task.is_running:
                        __task.join()
                        self.__task_pool.remove(__task)
            except Exception as ex:
                pass

            if self.__receiver:
                self.__receiver.close()
            if self.__context:
                self.__context.term()

    def __process_msg(self, json_data):
        try:
            for __task in self.__task_pool:
                if not __task.is_running:
                    __task.join()
                    self.__task_pool.remove(__task)

            msg_type = json_data['type']
            src = json_data['src']
            dest = json_data['dest']
            msg_data = json_data['msg']
            key = json_data['key']

            task = None
            if msg_type == ExecutionService.EXECUTION_TYPE:
                task = ExecutionTask(src, dest, msg_type, key, msg_data, self.__monitor)
            elif msg_type == ExecutionService.EXECUTION_RETURN_TYPE:
                task = ExecutionReturnTask(src, dest, msg_type, key, msg_data, self.__monitor)

            if task:
                task.setDaemon(True)
                task.start()
            self.__task_pool.append(task)
        except Exception as ex:
            pass
