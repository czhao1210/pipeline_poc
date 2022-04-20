from abc import abstractmethod

class Observer(object):

    @abstractmethod
    def post_message(self, msg):
        pass
