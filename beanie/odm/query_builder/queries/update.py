from typing import Dict, Union, Any, Type

from beanie.odm.query_builder.fields import CollectionField


class UpdateQuery:
    def __init__(self, document_class: Type["Document"], filter_query=None):
        self.document_class = document_class
        self.filter_query = filter_query
        self.update_query = {}

    def base_expression(
        self, expression: Dict[Union[CollectionField, str], Any], operator: str
    ):
        existed_expression = self.update_query.get(operator) or {}
        self.update_query[operator] = existed_expression.update(expression)
        return self

    def set(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.base_expression(expression=expression, operator="$set")

    def current_date(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.base_expression(
            expression=expression, operator="$currentDate"
        )

    def inc(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.base_expression(expression=expression, operator="$inc")

    def min(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.base_expression(expression=expression, operator="$min")

    def max(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.base_expression(expression=expression, operator="$max")

    def mul(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.base_expression(expression=expression, operator="$mul")

    def rename(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.base_expression(expression=expression, operator="$rename")

    def set_on_insert(
        self, expression: Dict[Union[CollectionField, str], Any]
    ):
        return self.base_expression(
            expression=expression, operator="$setOnInsert"
        )

    def unset(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.base_expression(expression=expression, operator="$unset")


class UpdateMany(UpdateQuery):
    def update_many(self, update_query):
        self.update_query.update(update_query)

    def __await__(self):
        yield self.document_class.get_motor_collection().update_many(
            self.filter_query, self.update_query
        )


class UpdateOne(UpdateQuery):
    def update_one(self, update_query):
        self.update_query.update(update_query)

    def __await__(self):
        yield self.document_class.get_motor_collection().update_one(
            self.filter_query,
            self.update_query,
            # session=
        )
