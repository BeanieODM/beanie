from pymongo.client_session import ClientSession
from beanie.odm.interfaces.session import SessionMethods as SessionMethods
from pymongo.results import DeleteResult as DeleteResult
from typing import Any, Mapping, Optional, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from beanie.odm.documents import Document, DocType as DocType

class DeleteQuery(SessionMethods):
    document_model: Document
    find_query: Mapping[str, Any]
    session: Optional[ClientSession]

    def __init__(
        self,
        document_model: Type[DocType],
        find_query: Mapping[str, Any]
    ) -> None: 
        ...

class DeleteMany(DeleteQuery):
    def __await__(self) -> DeleteResult: 
        ...

class DeleteOne(DeleteQuery):
    def __await__(self) -> DeleteResult: 
        ...
