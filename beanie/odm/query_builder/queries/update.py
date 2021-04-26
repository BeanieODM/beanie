from typing import Dict, Union, Any, Type

from beanie.odm.query_builder.fields import CollectionField
from beanie.odm.query_builder.operators.update import BaseUpdateOperator
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


class UpdateQuery:
    def __init__(self, document_class: Type["Document"], filter_query=None):
        self.document_class = document_class
        self.filter_query = filter_query
        self.update_expressions = []

    def set(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.update_expressions.append(Set(expression))

    def current_date(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.update_expressions.append(CurrentDate(expression))

    def inc(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.update_expressions.append(Inc(expression))

    def min(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.update_expressions.append(Min(expression))

    def max(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.update_expressions.append(Max(expression))

    def mul(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.update_expressions.append(Mul(expression))

    def rename(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.update_expressions.append(Rename(expression))

    def set_on_insert(
        self, expression: Dict[Union[CollectionField, str], Any]
    ):
        return self.update_expressions.append(SetOnInsert(expression))

    def unset(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.update_expressions.append(Unset(expression))

    @property
    def update_query(self):
        query = {}
        for expression in self.update_expressions:
            if isinstance(expression, BaseUpdateOperator):
                query.update(expression.query)
            elif isinstance(expression, dict):
                query.update(expression)
            else:
                raise Exception  # TODO come up with exception
        return query

    def update(self, *args):
        self.update_expressions += args
        return self


class UpdateMany(UpdateQuery):
    def update_many(self, *args):
        return self.update(*args)

    def __await__(self):
        yield from self.document_class.get_motor_collection().update_many(
            self.filter_query, self.update_query
        )


class UpdateOne(UpdateQuery):
    def update_one(self, *args):
        return self.update(*args)

    def __await__(self):
        yield from self.document_class.get_motor_collection().update_one(
            self.filter_query,
            self.update_query,
            # session=
        )
