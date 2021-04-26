from typing import Dict, Union, Any, Optional, List, Tuple

from beanie.odm.models import SortDirection
from beanie.odm.query_builder.fields import CollectionField
from beanie.odm.query_builder.operators.find.logical import And
from beanie.odm.query_builder.queries.cursor import BaseCursorQuery
from beanie.odm.query_builder.queries.delete import (
    DeleteQuery,
    DeleteMany,
    DeleteOne,
)
from beanie.odm.query_builder.queries.replace import ReplaceOne
from beanie.odm.query_builder.queries.update import (
    UpdateQuery,
    UpdateMany,
    UpdateOne,
)


class FindQuery:
    UpdateQueryType = UpdateQuery
    DeleteQueryType = DeleteQuery

    def __init__(self, document_class):
        self.document_class = document_class
        self.find_expressions = []

    @property
    def filter_query(self):
        return And(*self.find_expressions)

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

    def update(self, *args):
        return self.UpdateQueryType(
            document_class=self.document_class, filter_query=self.filter_query
        ).update(*args)

    def delete(self, *args):
        return self.DeleteQueryType(
            document_class=self.document_class, filter_query=self.filter_query
        )


class FindMany(BaseCursorQuery, FindQuery):
    UpdateQueryType = UpdateMany
    DeleteQueryType = DeleteMany

    def __init__(self, document_class):
        super(FindMany, self).__init__(document_class=document_class)
        self.sort_expressions = []
        self.skip_number = 0
        self.limit_number = 0
        self.init_cursor(return_model=document_class)

    @property
    def motor_cursor(self):
        return self.document_class.get_motor_collection().find(
            filter=self.filter_query,
            sort=self.sort_expressions,
            projection=self.document_class._get_projection(),
            skip=self.skip_number,
            limit=self.limit_number,
        )

    def find(
        self,
        *args,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
    ):
        print("HERE")
        self.find_expressions += args
        self.skip(skip)
        self.limit(limit)
        self.sort(sort)
        return self

    def sort(self, *args):
        for arg in args:
            if arg is None:
                pass
            elif isinstance(arg, list):
                self.sort(*arg)
            elif isinstance(arg, tuple):
                self.sort_expressions.append(arg)
            elif isinstance(arg, str):
                if arg.startswith("+"):
                    self.sort_expressions.append(
                        (arg[1:], SortDirection.ASCENDING)
                    )
                elif arg.startswith("-"):
                    self.sort_expressions.append(
                        (arg[1:], SortDirection.DESCENDING)
                    )
                else:
                    self.sort_expressions.append(
                        (arg, SortDirection.ASCENDING)
                    )
            else:
                raise Exception  # TODO come up with exception
        return self

    def skip(self, n: Optional[int]):
        if n is not None:
            self.skip_number = n
        return self

    def limit(self, n: Optional[int]):
        if n is not None:
            self.limit_number = n
        return self

    def update_many(self, *args):
        return self.update(*args)

    def delete_many(self, *args):
        return self.delete(*args)

    async def count(self):
        return (
            await self.document_class.get_motor_collection().count_documents(
                self.filter_query
            )
        )


class FindOne(FindQuery):
    UpdateQueryType = UpdateOne
    DeleteQueryType = DeleteOne

    def find_one(self, *args):
        self.find_expressions += args
        return self

    def update_one(self, *args):
        return self.update(*args)

    def delete_one(self, *args):
        return self.delete(*args)

    def replace_one(self, document):
        return ReplaceOne(
            document_class=self.document_class, filter_query=self.filter_query
        ).replace_one(document=document)

    def __await__(self):
        document = yield from self.document_class.get_motor_collection().find_one(  # noqa
            # noqa
            filter=self.filter_query,
            projection=self.document_class._get_projection(),
            # session=session,
        )
        if document is None:
            return None
        return self.document_class.parse_obj(document)
