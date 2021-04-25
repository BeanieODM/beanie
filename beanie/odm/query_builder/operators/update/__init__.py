from abc import abstractmethod


class BaseUpdateOperator:
    @property
    @abstractmethod
    def query(self):
        ...
