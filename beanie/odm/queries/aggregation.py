from typing import (
    Type,
    List,
    Union,
    Mapping,
    Optional,
    TYPE_CHECKING,
    Dict,
    Any,
)

from pydantic import BaseModel

from beanie.odm.interfaces.session import SessionMethods
from beanie.odm.queries.cursor import BaseCursorQuery
from beanie.odm.utils.projection import get_projection

if TYPE_CHECKING:
    from beanie.odm.documents import DocType


class AggregationQuery(BaseCursorQuery, SessionMethods):
    """
    Aggregation Query

    Inherited from:

    - [SessionMethods](https://roman-right.github.io/beanie/api/interfaces/#sessionmethods) - session methods
    - [BaseCursorQuery](https://roman-right.github.io/beanie/api/queries/#basecursorquery) - async generator
    """

    def __init__(
        self,
        document_model: Type["DocType"],
        aggregation_pipeline: List[Union[Dict[str, Any], Mapping[str, Any]]],
        find_query: Union[Dict[str, Any], Mapping[str, Any]],
        projection_model: Optional[Type[BaseModel]] = None,
    ):
        self.aggregation_pipeline: List[
            Union[Dict[str, Any], Mapping[str, Any]]
        ] = aggregation_pipeline
        self.document_model = document_model
        self.projection_model = projection_model
        self.find_query = find_query
        self.session = None

    def get_aggregation_pipeline(
        self,
    ) -> List[Union[Dict[str, Any], Mapping[str, Any]]]:
        match_pipeline: List[Dict[str, Any]] = (
            [{"$match": self.find_query}] if self.find_query else []
        )
        projection_pipeline: List[Dict[str, Any]] = (
            [{"$project": get_projection(self.projection_model)}]
            if self.projection_model
            else []
        )
        return match_pipeline + self.aggregation_pipeline + projection_pipeline

    @property
    def motor_cursor(self):
        aggregation_pipeline = self.get_aggregation_pipeline()
        return self.document_model.get_motor_collection().aggregate(
            aggregation_pipeline, session=self.session
        )

    def get_projection_model(self) -> Optional[Type[BaseModel]]:
        return self.projection_model
