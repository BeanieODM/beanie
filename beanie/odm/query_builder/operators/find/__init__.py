from abc import abstractmethod


class BaseFindOperator:
    @property
    @abstractmethod
    def query(self):
        ...
