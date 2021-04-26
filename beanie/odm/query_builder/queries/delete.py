from typing import Type


class DeleteQuery:
    def __init__(self, document_class: Type["Document"], filter_query=None):
        self.document_class = document_class
        self.filter_query = filter_query


class DeleteMany(DeleteQuery):
    def __await__(self):
        yield from self.document_class.get_motor_collection().delete_many(
            self.filter_query
        )


class DeleteOne(DeleteQuery):
    def __await__(self):
        yield from self.document_class.get_motor_collection().delete_one(
            self.filter_query,
        )
