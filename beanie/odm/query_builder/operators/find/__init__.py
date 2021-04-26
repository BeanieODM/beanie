from abc import abstractmethod

from beanie.odm.query_builder.operators import BaseOperator


class BaseFindOperator(BaseOperator):
    @property
    @abstractmethod
    def query(self):
        ...
