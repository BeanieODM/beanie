from beanie.migrations.controllers import IterativeMigration
from tests.models import DocumentTestModel


class Forward:
    @IterativeMigration
    async def f(
        self,
        input_document: DocumentTestModel,
        output_document: DocumentTestModel,
    ):
        output_document.test_str = input_document.test_str + "_SMTH"
