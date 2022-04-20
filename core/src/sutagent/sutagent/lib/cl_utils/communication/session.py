import uuid
import pickle
from threading import Lock
from datetime import datetime
from sutagent.lib.cl_utils.communication.executor import ExecutionService, ReceiveService
import time
from sutagent.lib.cl_utils.communication.message_pool import send_message


def init(local_address, port):
    '''

    :param local_address: bind local address
        default is '127.0.0.1'
    :param port:  bind local port
        default is bind a random port
    :return:
    '''
    ReceiveService.set(ExecutionService.get(local_address, port))


def delete():
    srv = ReceiveService.get()
    if srv:
        srv.stop()
        srv.join()


class Session(object):
    def __init__(self, target_address):
        self.__lock = Lock()
        print('Create session to {0} ...'.format(target_address))
        self.__context = zmq.Context()
        temp = target_address.split('//')[1]
        address = temp.split(':')[0]
        port = target_address.split(':')[2]
        init(address, port)
        bind_ip = ReceiveService.get().bind_address
        self.__bind_port = ReceiveService.get().bind_port
        self.__p2p_addr = r'tcp://{0}:{1}'.format(bind_ip, self.__bind_port)
        self.__bind_addr = r'tcp://{0}:{1}'.format(bind_ip, self.__bind_port)
        self.__target_address = target_address
        self.__session_id = "{0}-{1}".format(self.__bind_port, uuid.uuid1())
        self.__internal_id = 0
        print('Create session to {0} done....'.format(target_address))

    def __del__(self):
        self.__close()

    @property
    def context(self):
        return self.__context

    @property
    def bind_port(self):
        return self.__bind_port

    @property
    def bind_address(self):
        return self.__bind_addr

    @property
    def dest_address(self):
        return self.__target_address

    @property
    def src_address(self):
        return self.__p2p_addr

    def execute_async(self, func_name, mod_name, *args, **kwargs):
        try:
            key = self.__generate_key()
            json_data = dict(src=self.__p2p_addr,
                             dest=self.__target_address,
                             type=r'execution',
                             key=key,
                             msg=dict(func_name=func_name, mod_name=mod_name,
                                      args=pickle.dumps(args), kwargs=pickle.dumps(kwargs)))

            if send_message(self.__context, json_data, self.__target_address):
                return dict(result=True, key=key)
            else:
                return dict(result=False, key=key)
        except Exception as ex:
            print('execute_async ex= {0} session id = {1}'.format(ex, self.__session_id))
            return dict(result=False, key=None)

    def close(self):
        return self.__close()

    def __generate_key(self):
        self.__lock.acquire()
        key = u"{0}-{1}".format(self.__session_id, '%05d' % self.__internal_id)
        self.__internal_id = (self.__internal_id + 1) % 10000
        self.__lock.release()
        return key

    def __close(self):
        try:
            print('Session close to {0} ...'.format(self.__target_address))
            if self.__context:
                self.__context.term()
            self.__context = None
            print('Session close to {0} ok...'.format(self.__target_address))
        except Exception as ex:
            print('Session close ex={0} session id ={1}'.format(ex, self.__session_id))


def wait_for_message(key, timeout):
    try:
        ret = None
        start = datetime.now()
        while not ret and (datetime.now() - start).seconds <= timeout:
            ret = ReceiveService().get().get_message(key)
            time.sleep(0.1)

        if ret and 'msg' in ret.keys():
            msg_data = ret['msg']
            if 'execute_success' in msg_data.keys() and msg_data['execute_success']:
                if 'func_return' in msg_data.keys():
                    try:
                        func_return = pickle.loads(msg_data[r'func_return'])
                    except Exception as ex:
                        print('pickle func_return exception {0}'.format(ex))
                        func_return = msg_data[r'func_return']

                    return dict(result=True, value=func_return)
                else:
                    print('not find func_return in msg_data {0}'.format(msg_data))

            if 'err_msg' in msg_data.keys():
                print('err_msg={0}'.format(msg_data['err_msg']))

        return dict(result=False, value=None)
    except Exception as ex:
        print('wait_for_message key={0}, ex={1}'.format(key, ex))
        return dict(result=False, value=None)
