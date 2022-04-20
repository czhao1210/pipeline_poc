from abc import abstractmethod


class DataService(object):
    def __init__(self):
        self.__data_service = None

    @abstractmethod
    def read_frame(self, timeout, heartbeats, max_size):
        raise NotImplementedError

    @abstractmethod
    def read_until(self, pattern, timeout):
        raise NotImplementedError

    @abstractmethod
    def read(self):
        raise NotImplementedError

    @abstractmethod
    def write(self, data):
        raise NotImplementedError

