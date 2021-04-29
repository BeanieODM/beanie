from typing import Type

from beanie.odm.interfaces.update import (
    UpdateMethods,
)
from beanie.odm.operators.update import BaseUpdateOperator


class UpdateQuery(UpdateMethods):
    def __init__(self, document_model: Type["Document"], find_query: dict):
        self.document_model = document_model
        self.find_query = find_query
        self.update_expressions = []

    def _pass_update_expression(self, expression):
        self.update_expressions.append(expression)
        return self

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
        yield from self.document_model.get_motor_collection().update_many(
            self.find_query, self.update_query
        )


class UpdateOne(UpdateQuery):
    def update_one(self, *args):
        return self.update(*args)

    def __await__(self):
        yield from self.document_model.get_motor_collection().update_one(
            self.find_query,
            self.update_query,
            # session=
        )
