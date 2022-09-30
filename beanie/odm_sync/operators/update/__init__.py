from abc import abstractmethod
from typing import Any, Mapping

from beanie.odm_sync.operators import BaseOperator


class BaseUpdateOperator(BaseOperator):
    @property
    @abstractmethod
    def query(self) -> Mapping[str, Any]:
        ...
