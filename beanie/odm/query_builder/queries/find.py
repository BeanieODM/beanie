from typing import Dict, Union, Any

from beanie.odm.cursor import Cursor
from beanie.odm.query_builder.fields import CollectionField
from beanie.odm.query_builder.operators.find.logical import AND
from beanie.odm.query_builder.queries.cursor import BaseCursorQuery
from beanie.odm.query_builder.queries.update import (
    UpdateQuery,
    UpdateMany,
    UpdateOne,
)


class FindQuery:
    UpdateQueryType = UpdateQuery

    def __init__(self, document_class):
        self.document_class = document_class
        self.find_expressions = []

    @property
    def filter_query(self):
        return AND(*self.find_expressions).query

    def set(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.UpdateQueryType(
            document_class=self.document_class, filter_query=self.filter_query
        ).set(expression=expression)

    def current_date(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.UpdateQueryType(
            document_class=self.document_class, filter_query=self.filter_query
        ).current_date(expression=expression)

    def inc(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.UpdateQueryType(
            document_class=self.document_class, filter_query=self.filter_query
        ).inc(expression=expression)

    def min(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.UpdateQueryType(
            document_class=self.document_class, filter_query=self.filter_query
        ).min(expression=expression)

    def max(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.UpdateQueryType(
            document_class=self.document_class, filter_query=self.filter_query
        ).max(expression=expression)

    def mul(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.UpdateQueryType(
            document_class=self.document_class, filter_query=self.filter_query
        ).mul(expression=expression)

    def rename(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.UpdateQueryType(
            document_class=self.document_class, filter_query=self.filter_query
        ).rename(expression=expression)

    def set_on_insert(
        self, expression: Dict[Union[CollectionField, str], Any]
    ):
        return self.UpdateQueryType(
            document_class=self.document_class, filter_query=self.filter_query
        ).set_on_insert(expression=expression)

    def unset(self, expression: Dict[Union[CollectionField, str], Any]):
        return self.UpdateQueryType(
            document_class=self.document_class, filter_query=self.filter_query
        ).unset(expression=expression)


class FindMany(BaseCursorQuery, FindQuery):
    UpdateQueryType = UpdateMany

    @property
    def cursor(self):
        cursor = self.document_class.get_motor_collection().find(
            filter=self.filter_query,
            projection=self.document_class._get_projection(),
        )
        return Cursor(motor_cursor=cursor, model=self.document_class)

    def find_many(self, *args):
        self.find_expressions += args
        return self


class FindOne(FindQuery):
    UpdateQueryType = UpdateOne

    def find_one(self, *args):
        self.find_expressions += args
        return self

    def __await__(self):
        document = yield from self.document_class.get_motor_collection().find_one(  # noqa
            filter=self.filter_query,
            projection=self.document_class._get_projection(),
            # session=session,
        )
        if document is None:
            return None
        return self.document_class.parse_obj(document)
