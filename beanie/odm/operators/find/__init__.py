from abc import abstractmethod

from beanie.odm.operators import BaseOperator


class BaseFindOperator(BaseOperator):
    @property
    @abstractmethod
    def query(self):
        ...
