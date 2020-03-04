from abc import ABC, abstractmethod


class BaseHandler(ABC):
    def __init__(self):
        pass

    def handle(self, body):
        assert isinstance(body, dict)
        result_code, msg = self._handle(body)
        assert isinstance(result_code, int)
        assert isinstance(msg, str)
        return result_code, msg

    @abstractmethod
    def _handle(self, body):
        """
        return: result_code, msg
        """