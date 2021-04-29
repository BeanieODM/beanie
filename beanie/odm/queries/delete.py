from typing import Type

from aiohttp import ClientSession


class DeleteQuery:
    def __init__(self, document_model: Type["Document"], find_query: dict):
        self.document_model = document_model
        self.find_query = find_query
        self.session = None

    def set_session(self, session: ClientSession = None):
        if session is not None:
            self.session = session
        return self


class DeleteMany(DeleteQuery):
    def __await__(self):
        yield from self.document_model.get_motor_collection().delete_many(
            self.find_query, session=self.session
        )


class DeleteOne(DeleteQuery):
    def __await__(self):
        yield from self.document_model.get_motor_collection().delete_one(
            self.find_query, session=self.session
        )
