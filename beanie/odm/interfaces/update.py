from abc import abstractmethod
from typing import Dict, Union, Any

from beanie.odm.fields import CollectionField
from beanie.odm.operators.update.general import (
    Set,
    CurrentDate,
    Inc,
)


class UpdateMethods:
    @abstractmethod
    def update(self, *args):
        ...

    def set(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.update(Set(expression))

    def current_date(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.update(CurrentDate(expression))

    def inc(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.update(Inc(expression))
