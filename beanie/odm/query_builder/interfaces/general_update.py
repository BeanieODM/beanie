from abc import abstractmethod
from typing import Dict, Union, Any

from beanie.odm.query_builder.fields import CollectionField
from beanie.odm.query_builder.operators.update.general import (
    Set,
    CurrentDate,
    Inc,
    Min,
    Max,
    Mul,
    Rename,
    SetOnInsert,
    Unset,
)


class GeneralUpdateMethods:
    @abstractmethod
    def _pass_update_expression(self, expression):
        ...

    def set(self, expression: Dict[Union[CollectionField, str], Any]):
        return self._pass_update_expression(Set(expression))

    def current_date(self, expression: Dict[Union[CollectionField, str], Any]):
        return self._pass_update_expression(CurrentDate(expression))

    def inc(self, expression: Dict[Union[CollectionField, str], Any]):
        return self._pass_update_expression(Inc(expression))

    def min(self, expression: Dict[Union[CollectionField, str], Any]):
        return self._pass_update_expression(Min(expression))

    def max(self, expression: Dict[Union[CollectionField, str], Any]):
        return self._pass_update_expression(Max(expression))

    def mul(self, expression: Dict[Union[CollectionField, str], Any]):
        return self._pass_update_expression(Mul(expression))

    def rename(self, expression: Dict[Union[CollectionField, str], Any]):
        return self._pass_update_expression(Rename(expression))

    def set_on_insert(
        self, expression: Dict[Union[CollectionField, str], Any]
    ):
        return self._pass_update_expression(SetOnInsert(expression))

    def unset(self, expression: Dict[Union[CollectionField, str], Any]):
        return self._pass_update_expression(Unset(expression))
