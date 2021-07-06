from beanie.odm.documents import DocType as DocType
from beanie.odm.interfaces.session import SessionMethods as SessionMethods
from beanie.odm.queries.cursor import BaseCursorQuery as BaseCursorQuery
from beanie.odm.utils.projection import get_projection as get_projection
from pydantic import BaseModel as BaseModel
from typing import Any, List, Mapping, Optional, Type, TypeVar

AggregationProjectionType = TypeVar('AggregationProjectionType')

class AggregationQuery(BaseCursorQuery[AggregationProjectionType], SessionMethods):
    aggregation_pipeline: Any
    document_model: Any
    projection_model: Any
    find_query: Any
    session: Any
    def __init__(self, document_model: Type[DocType], aggregation_pipeline: List[Mapping[str, Any]], find_query: Mapping[str, Any], projection_model: Optional[Type[BaseModel]] = ...) -> None: ...
    def get_aggregation_pipeline(self) -> List[Mapping[str, Any]]: ...
    @property
    def motor_cursor(self): ...
    def get_projection_model(self) -> Optional[Type[BaseModel]]: ...
