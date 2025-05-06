from abc import abstractmethod
from collections.abc import Mapping
from typing import Any

from beanie.odm.operators import BaseOperator


class BaseUpdateOperator(BaseOperator):
    @property
    @abstractmethod
    def query(self) -> Mapping[str, Any]: ...
