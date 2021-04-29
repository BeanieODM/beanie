from typing import Type, List, Union, Mapping, Optional

from aiohttp import ClientSession
from pydantic import BaseModel

from beanie.odm.queries.cursor import BaseCursorQuery
from beanie.odm.utils.projection import get_projection


class AggregationPipeline(BaseCursorQuery):
    def __init__(
        self,
        document_model: Type["Document"],
        aggregation_pipeline: List[Union[dict, Mapping]],
        find_query: dict,
        projection_model: Optional[Type[BaseModel]] = None,  # TODO naming
    ):
        self.aggregation_pipeline = aggregation_pipeline
        self.document_model = document_model
        self.projection_model = projection_model
        self.find_query = find_query
        self.session = None

    def set_session(self, session: ClientSession = None):
        if session is not None:
            self.session = session
        return self

    def get_aggregation_pipeline(self):
        match_pipeline = (
            [{"$match": self.find_query}] if self.find_query else []
        )
        projection_pipeline = (
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
