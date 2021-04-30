from typing import Type, TYPE_CHECKING

from aiohttp import ClientSession

from beanie.odm.interfaces.session import SessionMethods
from beanie.odm.interfaces.update import (
    UpdateMethods,
)
from beanie.odm.operators.update import BaseUpdateOperator

if TYPE_CHECKING:
    from beanie.odm.documents import Document


class UpdateQuery(UpdateMethods, SessionMethods):
    def __init__(self, document_model: Type[Document], find_query: dict):
        self.document_model = document_model
        self.find_query = find_query
        self.update_expressions = []
        self.session = None

    @property
    def update_query(self):
        query = {}
        for expression in self.update_expressions:
            if isinstance(expression, BaseUpdateOperator):
                query.update(expression.query)
            elif isinstance(expression, dict):
                query.update(expression)
            else:
                raise TypeError("Wrong expression type")
        return query

    def update(self, *args, session: ClientSession = None):
        self.set_session(session=session)
        self.update_expressions += args
        return self


class UpdateMany(UpdateQuery):
    def update_many(self, *args, session: ClientSession = None):
        return self.update(*args, session=session)

    def __await__(self):
        yield from self.document_model.get_motor_collection().update_many(
            self.find_query, self.update_query, session=self.session
        )


class UpdateOne(UpdateQuery):
    def update_one(self, *args, session: ClientSession = None):
        return self.update(*args, session=session)

    def __await__(self):
        yield from self.document_model.get_motor_collection().update_one(
            self.find_query, self.update_query, session=self.session
        )
