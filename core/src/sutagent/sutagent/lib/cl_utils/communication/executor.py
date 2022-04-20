import time
from threading import Lock
from threading import Thread
from sutagent.lib.cl_utils.communication.executiontask import ExecutionTask, ExecutionReturnTask
from sutagent.lib.cl_utils.communication.message_pool import MessageMonitor


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
        super(ExecutionService, self).__init__(group, target, name, args, kwargs)

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

        print('local_address', self.bind_address, 'bind_port', self.bind_port)
        self.__receiver.RCVTIMEO = 1000
        # if value is -1(default), zmq.contex.term will be block if any data not send success, so need set this value
        self.__receiver.setsockopt(zmq.LINGER, 0)
        self.__task_pool = []
        self.__stop = False
        self.__monitor = MessageMonitor()
        self.setDaemon(True)
        self.start()

    def get_message(self, key):
        return self.__monitor.get_message(key)

    def stop(self):
        print(r'ExecutionService: stopped')
        self.__lock.acquire()
        self.__stop = True
        self.__lock.release()
        ExecutionService.__service = None

    def run(self):
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
            print('ExecutionService: {0}'.format(ex))
        finally:
            print('ExecutionService: doing stopping...')
            try:
                for __task in self.__task_pool:
                    if not __task.is_running:
                        print('remove task', __task.key())
                        __task.join()
                        self.__task_pool.remove(__task)
            except Exception as ex:
                print('ExecutionService: stop task error {0}'.format(ex))

            if self.__receiver:
                self.__receiver.close()
            if self.__context:
                self.__context.term()

            print('ExecutionService is stopped')

    def __process_msg(self, json_data):
        try:
            print('process_msg {0}'.format(json_data))
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
            if msg_type == r'execution':
                task = ExecutionTask(src, dest, msg_type, key, msg_data, self.__monitor)
            elif msg_type == r'execution_return':
                task = ExecutionReturnTask(src, dest, msg_type, key, msg_data, self.__monitor)
            else:
                print('msg_type error. {0}'.format(msg_type))

            if task:
                task.setDaemon(True)
                task.start()
            self.__task_pool.append(task)
            print('process_msg {0} Done....'.format(json_data))
        except Exception as ex:
            print('ExecutionService.__process_msg ex={0}'.format(ex))
