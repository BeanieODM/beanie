from abc import abstractmethod
from typing import Any, Mapping

from beanis.odm.operators import BaseOperator


class BaseUpdateOperator(BaseOperator):
    @property
    @abstractmethod
    def query(self) -> Mapping[str, Any]:
        ...
