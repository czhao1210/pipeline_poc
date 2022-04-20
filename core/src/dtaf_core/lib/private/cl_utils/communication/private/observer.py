from abc import abstractmethod


class Observer(object):
    """
    abstract class to define interface of observer
    """

    @abstractmethod
    def post_message(self, msg):
        """
        post message to service
        :param msg: message
        :return: None
        """
        pass
