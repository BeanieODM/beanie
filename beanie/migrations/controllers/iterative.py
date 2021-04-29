from inspect import signature, isclass
from typing import Type, Optional, Union, List

from beanie.utils import update_dict
from beanie.migrations.controllers.base import BaseMigrationController
from beanie.odm.documents import Document


class DummyOutput:
    def __init__(self):
        super(DummyOutput, self).__setattr__("_internal_structure_dict", {})

    def __setattr__(self, key, value):
        self._internal_structure_dict[key] = value

    def __getattr__(self, item):
        try:
            return self._internal_structure_dict[item]
        except KeyError:
            self._internal_structure_dict[item] = DummyOutput()
            return self._internal_structure_dict[item]

    def dict(self, to_parse: Optional[Union[dict, "DummyOutput"]] = None):
        if to_parse is None:
            to_parse = self
        input_dict = (
            to_parse._internal_structure_dict
            if isinstance(to_parse, DummyOutput)
            else to_parse
        )
        result_dict = {}
        for key, value in input_dict.items():
            if isinstance(value, (DummyOutput, dict)):
                result_dict[key] = self.dict(to_parse=value)
            else:
                result_dict[key] = value
        return result_dict


def iterative_migration(
    document_models: Optional[List[Type[Document]]] = None,
    batch_size: int = 10000,
):
    class IterativeMigration(BaseMigrationController):
        def __init__(self, function):
            self.function = function
            self.function_signature = signature(function)
            input_signature = self.function_signature.parameters.get(
                "input_document"
            )
            self.input_document_model: Type[
                Document
            ] = input_signature.annotation
            output_signature = self.function_signature.parameters.get(
                "output_document"
            )
            self.output_document_model: Type[
                Document
            ] = output_signature.annotation

            if (
                not isclass(self.input_document_model)
                or not issubclass(self.input_document_model, Document)
                or not isclass(self.output_document_model)
                or not issubclass(self.output_document_model, Document)
            ):
                raise TypeError(
                    "input_document and output_document "
                    "must have annotation of Document subclass"
                )

            self.batch_size = batch_size

        def __call__(self, *args, **kwargs):
            pass

        @property
        def models(self) -> List[Type[Document]]:
            preset_models = document_models
            if preset_models is None:
                preset_models = []
            return preset_models + [
                self.input_document_model,
                self.output_document_model,
            ]

        async def run(self, session):
            output_documents = []
            async for input_document in self.input_document_model.find_all():
                output = DummyOutput()
                function_kwargs = {
                    "input_document": input_document,
                    "output_document": output,
                }
                if "self" in self.function_signature.parameters:
                    function_kwargs["self"] = None
                await self.function(**function_kwargs)
                output_dict = input_document.dict()
                update_dict(output_dict, output.dict())
                output_document = self.output_document_model.parse_obj(
                    output_dict
                )
                output_documents.append(output_document)

                if len(output_documents) == self.batch_size:
                    await self.output_document_model.replace_many(
                        documents=output_documents
                    )
                    output_documents = []

            if output_documents:
                await self.output_document_model.replace_many(
                    documents=output_documents
                )

    return IterativeMigration
