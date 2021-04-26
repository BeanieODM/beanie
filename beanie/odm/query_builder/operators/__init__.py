from abc import abstractmethod
from collections import Mapping


class BaseOperator(Mapping):
    @property
    @abstractmethod
    def query(self) -> dict:
        ...

    def __getitem__(self, item):
        return self.query[item]

    def __iter__(self):
        return iter(self.query)

    def __len__(self):
        return len(self.query)

    def __repr__(self):
        return repr(self.query)

    def __str__(self):
        return str(self.query)
