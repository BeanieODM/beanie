from typing import Union, Optional, List, Tuple, Type

from pydantic import BaseModel

from beanie.exceptions import DocumentNotFound
from beanie.odm.models import SortDirection
from beanie.odm.interfaces.aggregate import AggregateMethods
from beanie.odm.interfaces.update import (
    UpdateMethods,
)
from beanie.odm.queries.aggregation import AggregationPipeline
from beanie.odm.queries.cursor import BaseCursorQuery
from beanie.odm.queries.delete import (
    DeleteQuery,
    DeleteMany,
    DeleteOne,
)
from beanie.odm.queries.parameters import FindParameters
from beanie.odm.queries.update import (
    UpdateQuery,
    UpdateMany,
    UpdateOne,
)


class FindQuery(UpdateMethods):
    UpdateQueryType = UpdateQuery
    DeleteQueryType = DeleteQuery

    def __init__(self, document_model):
        self.document_model = document_model
        self.find_parameters = FindParameters()

    def _pass_update_expression(self, expression):
        return self.UpdateQueryType(
            document_model=self.document_model,
            find_parameters=self.find_parameters,
        ).update(expression)

    def update(self, *args):
        return self.UpdateQueryType(
            document_model=self.document_model,
            find_parameters=self.find_parameters,
        ).update(*args)

    def delete(self):
        return self.DeleteQueryType(
            document_model=self.document_model,
            find_parameters=self.find_parameters,
        )


class FindMany(BaseCursorQuery, FindQuery, AggregateMethods):
    UpdateQueryType = UpdateMany
    DeleteQueryType = DeleteMany

    def __init__(self, document_model):
        super(FindMany, self).__init__(document_model=document_model)
        self.init_cursor(return_model=document_model)

    @property
    def motor_cursor(self):
        return self.document_model.get_motor_collection().find(
            filter=self.find_parameters.get_filter_query(),
            sort=self.find_parameters.sort_expressions,
            projection=self.document_model._get_projection(),
            skip=self.find_parameters.skip_number,
            limit=self.find_parameters.limit_number,
        )

    def find_many(
        self,
        *args,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
    ):
        self.find_parameters.find_expressions += args
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
                self.find_parameters.sort_expressions.append(arg)
            elif isinstance(arg, str):
                if arg.startswith("+"):
                    self.find_parameters.sort_expressions.append(
                        (arg[1:], SortDirection.ASCENDING)
                    )
                elif arg.startswith("-"):
                    self.find_parameters.sort_expressions.append(
                        (arg[1:], SortDirection.DESCENDING)
                    )
                else:
                    self.find_parameters.sort_expressions.append(
                        (arg, SortDirection.ASCENDING)
                    )
            else:
                raise Exception  # TODO come up with exception
        return self

    def skip(self, n: Optional[int]):
        if n is not None:
            self.find_parameters.skip_number = n
        return self

    def limit(self, n: Optional[int]):
        if n is not None:
            self.find_parameters.limit_number = n
        return self

    def update_many(self, *args):
        return self.update(*args)

    def delete_many(self, *args):
        return self.delete(*args)

    async def count(self):
        return (
            await self.document_model.get_motor_collection().count_documents(
                self.find_parameters.get_filter_query()
            )
        )

    def aggregate(
        self,
        aggregation_pipeline,
        aggregation_model: Type[BaseModel] = None,
    ) -> AggregationPipeline:
        return AggregationPipeline(
            aggregation_pipeline=aggregation_pipeline,
            document_model=self.document_model,
            aggregation_model=aggregation_model,
            find_parameters=self.find_parameters,
        )


class FindOne(FindQuery):
    UpdateQueryType = UpdateOne
    DeleteQueryType = DeleteOne

    def find_one(self, *args):
        self.find_parameters.find_expressions += args
        return self

    def update_one(self, *args):
        return self.update(*args)

    def delete_one(self):
        return self.delete()

    async def replace_one(self, document):
        result = await self.document_model.get_motor_collection().replace_one(
            self.find_parameters.get_filter_query(),
            document.dict(by_alias=True, exclude={"id"}),
        )

        if not result.raw_result["updatedExisting"]:
            raise DocumentNotFound
        return result

    def __await__(self):
        document = yield from self.document_model.get_motor_collection().find_one(
            filter=self.find_parameters.get_filter_query(),
            projection=self.document_model._get_projection(),
            # session=session,
        )  # noqa
        if document is None:
            return None
        return self.document_model.parse_obj(document)
