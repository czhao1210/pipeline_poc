from sutagent.lib.cl_utils.communication.observer import Observer
from threading import Lock
from collections import OrderedDict


def send_message(ctx, json_data, destination):
    print('send_message to {0} msg={1}'.format(destination, json_data))
    sender = None
    result = None
    try:
        sender = ctx.socket(zmq.REQ)
        # if value is -1(default), zmq.context.term will be block if any data not send success, so need set this value
        sender.setsockopt(zmq.LINGER, 0)
        sender.RCVTIMEO = 5 * 1000
        sender.SNDTIMEO = 20 * 1000
        sender.connect(destination)
        sender.send_json(json_data)
        ret = sender.recv()
        result = ret
    except Exception as ex:
        print('ex = {0} send_message to {1} msg={2}'.format(ex, destination, json_data))
    finally:
        if sender:
            sender.close()

    return result


class MessageMonitor(Observer):
    def __init__(self):
        self.__lock = Lock()
        self.__message_pool = OrderedDict()
        super(MessageMonitor, self).__init__()

    def post_message(self, msg):
        try:
            self.__lock.acquire()
            self.__message_pool[msg['key']] = msg
            while len(self.__message_pool.keys()) > 30:
                self.__message_pool.popitem(last=False)
            self.__lock.release()
        except Exception as ex:
            print('MessageMonitor.post_message ex={0}'.format(ex))

    def get_message(self, key):
        value = None
        try:
            self.__lock.acquire()
            if key in self.__message_pool.keys():
                value = self.__message_pool[key]
            self.__lock.release()
            return value
        except Exception as ex:
            print('MessageMonitor.get_message ex={0}'.format(ex))
            return value
