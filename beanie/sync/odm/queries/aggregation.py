from typing import (
    Type,
    List,
    Mapping,
    Optional,
    TYPE_CHECKING,
    Any,
    Generic,
    TypeVar,
)

from pydantic import BaseModel

from motor.core import AgnosticCommandCursor

from beanie.sync.odm.cache import LRUCache
from beanie.sync.odm.interfaces.session import SessionMethods
from beanie.sync.odm.queries.cursor import BaseCursorQuery
from beanie.sync.odm.utils.projection import get_projection

if TYPE_CHECKING:
    from beanie.sync.odm.documents import DocType

AggregationProjectionType = TypeVar("AggregationProjectionType")


class AggregationQuery(
    Generic[AggregationProjectionType],
    BaseCursorQuery[AggregationProjectionType],
    SessionMethods,
):
    """
    Aggregation Query

    Inherited from:

    - [SessionMethods](https://roman-right.github.io/beanie/api/interfaces/#sessionmethods) - session methods
    - [BaseCursorQuery](https://roman-right.github.io/beanie/api/queries/#basecursorquery) - generator
    """

    def __init__(
        self,
        document_model: Type["DocType"],
        aggregation_pipeline: List[Mapping[str, Any]],
        find_query: Mapping[str, Any],
        projection_model: Optional[Type[BaseModel]] = None,
        ignore_cache: bool = False,
        **pymongo_kwargs
    ):
        self.aggregation_pipeline: List[
            Mapping[str, Any]
        ] = aggregation_pipeline
        self.document_model = document_model
        self.projection_model = projection_model
        self.find_query = find_query
        self.session = None
        self.ignore_cache = ignore_cache
        self.pymongo_kwargs = pymongo_kwargs

    @property
    def _cache_key(self) -> str:
        return LRUCache.create_key(
            {
                "type": "Aggregation",
                "filter": self.find_query,
                "pipeline": self.aggregation_pipeline,
                "projection": get_projection(self.projection_model)
                if self.projection_model
                else None,
            }
        )

    def _get_cache(self):
        if (
            self.document_model.get_settings().use_cache
            and self.ignore_cache is False
        ):
            return self.document_model._cache.get(self._cache_key)  # type: ignore
        else:
            return None

    def _set_cache(self, data):
        if (
            self.document_model.get_settings().use_cache
            and self.ignore_cache is False
        ):
            return self.document_model._cache.set(self._cache_key, data)  # type: ignore

    def get_aggregation_pipeline(
        self,
    ) -> List[Mapping[str, Any]]:
        match_pipeline: List[Mapping[str, Any]] = (
            [{"$match": self.find_query}] if self.find_query else []
        )
        projection_pipeline: List[Mapping[str, Any]] = []
        if self.projection_model:
            projection = get_projection(self.projection_model)
            if projection is not None:
                projection_pipeline = [{"$project": projection}]
        return match_pipeline + self.aggregation_pipeline + projection_pipeline

    @property
    def motor_cursor(self) -> AgnosticCommandCursor:
        aggregation_pipeline = self.get_aggregation_pipeline()
        return self.document_model.get_motor_collection().aggregate(
            aggregation_pipeline, session=self.session, **self.pymongo_kwargs
        )

    def get_projection_model(self) -> Optional[Type[BaseModel]]:
        return self.projection_model
