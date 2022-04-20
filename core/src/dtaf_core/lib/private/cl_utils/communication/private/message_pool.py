import zmq
from dtaf_core.lib.private.cl_utils.communication.private.observer import Observer
from threading import Lock
from collections import OrderedDict


def send_message(ctx, json_data, destination):
    sender = None
    result = None
    try:
        sender = ctx.socket(zmq.REQ)
        sender.setsockopt(zmq.LINGER, 0)
        sender.RCVTIMEO = 5 * 1000
        sender.SNDTIMEO = 20 * 1000
        sender.connect(destination)
        sender.send_json(json_data)
        ret = sender.recv()
        result = ret
    except Exception as ex:
        pass
    finally:
        if sender:
            sender.close()

    return result


class MessageMonitor(Observer):
    """
    This class is used to monitor the message and response between host and service
    """
    def __init__(self):
        self.__lock = Lock()
        self.__message_pool = OrderedDict()
        super(MessageMonitor, self).__init__()

    def post_message(self, msg):
        """
        send message to service
        :param msg: message to send
        :return:
        """
        # (str) => None
        try:
            self.__lock.acquire()
            self.__message_pool[msg['key']] = msg
            while len(self.__message_pool.keys()) > 30:
                self.__message_pool.popitem(last=False)
            self.__lock.release()
        except Exception as ex:
            pass

    def get_message(self, key):
        """
        get message by key
        :param key: use key to query message from service
        :return:  None
        """
        # (str) => None
        value = None
        try:
            self.__lock.acquire()
            if key in self.__message_pool.keys():
                value = self.__message_pool[key]
            self.__lock.release()
            return value
        except Exception as ex:
            return value
