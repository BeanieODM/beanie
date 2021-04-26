from abc import abstractmethod

from beanie.odm.query_builder.operators import BaseOperator


class BaseUpdateOperator(BaseOperator):
    @property
    @abstractmethod
    def query(self):
        ...
