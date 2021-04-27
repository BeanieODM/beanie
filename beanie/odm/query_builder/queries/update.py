from typing import Type

from beanie.odm.query_builder.interfaces.update import (
    UpdateExtraMethodsInterface,
)
from beanie.odm.query_builder.operators.update import BaseUpdateOperator
from beanie.odm.query_builder.queries.parameters import FindParameters


class UpdateQuery(UpdateExtraMethodsInterface):
    def __init__(
        self, document_class: Type["Document"], find_parameters: FindParameters
    ):
        self.document_class = document_class
        self.find_parameters = find_parameters
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
        yield from self.document_class.get_motor_collection().update_many(
            self.find_parameters.get_filter_query(), self.update_query
        )


class UpdateOne(UpdateQuery):
    def update_one(self, *args):
        return self.update(*args)

    def __await__(self):
        yield from self.document_class.get_motor_collection().update_one(
            self.find_parameters.get_filter_query(),
            self.update_query,
            # session=
        )
