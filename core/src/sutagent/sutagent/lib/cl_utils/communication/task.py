from threading import Thread


class Task(Thread):
    def __init__(self, src, dest, msg_type, key, msg_data, observer, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        super(Task, self).__init__(group, target, name, args, kwargs)
        self.__src = src
        self.__dest = dest
        self.__msg_type = msg_type
        self.__msg_data = msg_data
        self.__key = key
        self.__running = False
        self.__observer = observer

    @property
    def is_running(self):
        return self.__running

    def start(self):
        self.__running = True
        return super(Task, self).start()
        
    def set_is_running(self, state):
        self.__running = state

    def key(self):
        return self.__key