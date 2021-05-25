from abc import abstractmethod
from typing import Any, Dict, Union, Mapping

from beanie.odm.operators import BaseOperator


class BaseUpdateOperator(BaseOperator):
    @property
    @abstractmethod
    def query(self) -> Union[Dict[str, Any], Mapping[str, Any]]:
        ...
