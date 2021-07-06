from beanie.odm.interfaces.session import SessionMethods as SessionMethods
from pymongo.results import DeleteResult as DeleteResult
from typing import Any, Mapping, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from beanie.odm.documents import DocType as DocType

class DeleteQuery(SessionMethods):
    document_model: Any
    find_query: Any
    session: Any
    def __init__(self, document_model: Type[DocType], find_query: Mapping[str, Any]) -> None: ...

class DeleteMany(DeleteQuery):
    def __await__(self) -> DeleteResult: ...

class DeleteOne(DeleteQuery):
    def __await__(self) -> DeleteResult: ...
