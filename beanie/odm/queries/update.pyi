import abc
from beanie.odm.documents import Document, DocType as DocType
from beanie.odm.interfaces.session import SessionMethods as SessionMethods
from beanie.odm.interfaces.update import UpdateMethods as UpdateMethods
from beanie.odm.operators.update import (
    BaseUpdateOperator as BaseUpdateOperator,
)
from pymongo.client_session import ClientSession as ClientSession
from pymongo.results import (
    InsertOneResult as InsertOneResult,
    UpdateResult as UpdateResult,
)
from typing import Any, Dict, List, Mapping, Optional, Type, Union

class UpdateQuery(UpdateMethods, SessionMethods, metaclass=abc.ABCMeta):
    document_model: Document
    find_query: Mapping[str, Any]
    update_expressions: List[Mapping[str, Any]]
    session: Optional[ClientSession]
    is_upsert: bool
    upsert_insert_doc: Optional[Document]

    def __init__(
        self, 
        document_model: Type[DocType], 
        find_query: Mapping[str, Any]
    ) -> None:
        ...

    @property
    def update_query(self) -> Dict[str, Any]: 
        ...

    def update(
        self,
        *args: Mapping[str, Any],
        session: Optional[ClientSession] = None
    ) -> UpdateQuery: 
        ...

    def upsert(
        self,
        *args: Mapping[str, Any],
        on_insert: DocType,
        session: Optional[ClientSession] = None
    ) -> UpdateQuery: 
        ...

    def __await__(self) -> Union[UpdateResult, InsertOneResult]: 
        ...

class UpdateMany(UpdateQuery):
    def update_many(
        self,
        *args: Mapping[str, Any],
        session: Optional[ClientSession] = None
    ): ...

class UpdateOne(UpdateQuery):
    def update_one(
        self, 
        *args: Mapping[str, Any],
        session: Optional[ClientSession] = None
    ): ...
