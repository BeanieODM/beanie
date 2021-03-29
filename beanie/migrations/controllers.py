from abc import abstractmethod, ABC
from inspect import signature
from typing import Type, Optional, Union, List

from beanie import Document


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


class Migration(ABC):
    @abstractmethod
    async def run(self, session):
        pass

    @property
    @abstractmethod
    def structures(self) -> List[Type[Document]]:
        pass


class IterativeMigration(Migration):
    def __init__(self, function):
        self.function = function
        migration_signature = signature(function)

        input_signature = migration_signature.parameters.get(
            "input_document"
        )  # TODO check class
        self.input_document_class: Type[Document] = input_signature.annotation

        output_signature = migration_signature.parameters.get(
            "output_document"
        )
        self.output_document_class: Type[
            Document
        ] = output_signature.annotation

    def __call__(self, *args, **kwargs):
        pass

    @property
    def structures(self) -> List[Type[Document]]:
        return [self.input_document_class, self.output_document_class]

    async def run(self, session):
        output_documents = []
        documents_ids = []
        async for input_document in self.input_document_class.find_all():
            output = DummyOutput()
            await self.function(
                1, input_document, output
            )  # TODO fix `self` things
            output_dict = input_document.dict()
            output_dict.update(output.dict())
            output_document = self.output_document_class.parse_obj(output_dict)
            output_documents.append(output_document)
            documents_ids.append(output_document.id)
        await self.input_document_class.delete_all(session=session)
        # raise Exception
        await self.output_document_class.insert_many(output_documents)
