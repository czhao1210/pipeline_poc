from threading import Thread


class Task(Thread):
    """
    Task class to execute command from host or service
    """
    def __init__(self, src, dest, msg_type, key, msg_data, observer, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        super(Task, self).__init__(group, target, name, args, kwargs, verbose)
        self.__src = src
        self.__dest = dest
        self.__msg_type = msg_type
        self.__msg_data = msg_data
        self.__key = key
        self.__running = False
        self.__observer = observer

    @property
    def is_running(self):
        """
        check the status of task
        :return: True / False
        """
        # (None) => (bool)
        return self.__running

    def start(self):
        """
        start running task
        :return:
        """
        self.__running = True
        return super(Task, self).start()
        
    def set_is_running(self, state):
        """
        set the status of task
        :return:
        """
        self.__running = state

    def key(self):
        """
        get the key of task for query
        :return: Key in format of uuid string
        """
        # (None) => (str)
        return self.__key
