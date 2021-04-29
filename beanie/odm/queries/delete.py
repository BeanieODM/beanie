from typing import Type


class DeleteQuery:
    def __init__(self, document_model: Type["Document"], find_query: dict):
        self.document_model = document_model
        self.find_query = find_query


class DeleteMany(DeleteQuery):
    def __await__(self):
        yield from self.document_model.get_motor_collection().delete_many(
            self.find_query
        )


class DeleteOne(DeleteQuery):
    def __await__(self):
        yield from self.document_model.get_motor_collection().delete_one(
            self.find_query,
        )
