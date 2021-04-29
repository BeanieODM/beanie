from typing import Type

from beanie.odm.queries.parameters import FindParameters


class DeleteQuery:
    def __init__(
        self, document_model: Type["Document"], find_parameters: FindParameters
    ):
        self.document_model = document_model
        self.find_parameters = find_parameters


class DeleteMany(DeleteQuery):
    def __await__(self):
        yield from self.document_model.get_motor_collection().delete_many(
            self.find_parameters.get_filter_query()
        )


class DeleteOne(DeleteQuery):
    def __await__(self):
        yield from self.document_model.get_motor_collection().delete_one(
            self.find_parameters.get_filter_query(),
        )
