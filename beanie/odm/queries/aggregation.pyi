from pymongo.client_session import ClientSession
from beanie.odm.documents import Document, DocType
from beanie.odm.interfaces.session import SessionMethods as SessionMethods
from beanie.odm.queries.cursor import BaseCursorQuery as BaseCursorQuery
from beanie.odm.utils.projection import get_projection as get_projection
from pydantic import BaseModel as BaseModel
from typing import Any, List, Mapping, Optional, Type, TypeVar

AggregationDocumentType = TypeVar("AggregationDocumentType")

class AggregationQuery(
    BaseCursorQuery[AggregationDocumentType],
    SessionMethods
):
    aggregation_pipeline: List[Mapping[str, Any]]
    document_model: AggregationDocumentType
    projection_model: BaseModel
    find_query: Mapping[str, Any]
    session: Optional[ClientSession]

    def __init__(
        self,
        document_model: Type[AggregationDocumentType],
        aggregation_pipeline: List[Mapping[str, Any]],
        find_query: Mapping[str, Any],
        projection_model: Optional[Type[BaseModel]] = None,
    ) -> None: ...

    @property
    def motor_cursor(self): ...

    def get_aggregation_pipeline(self) -> List[Mapping[str, Any]]: ...
    
    def get_projection_model(self) -> Optional[Type[BaseModel]]: ...
