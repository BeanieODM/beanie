from typing import Type, List, Union, Mapping

from pydantic import BaseModel

from beanie.odm.queries.cursor import BaseCursorQuery
from beanie.odm.queries.parameters import FindParameters


class AggregationPipeline(BaseCursorQuery):
    def __init__(
        self,
        document_model: Type["Document"],
        aggregation_pipeline: List[Union[dict, Mapping]],
        find_parameters: FindParameters,
        aggregation_model: Type[BaseModel],  # TODO naming
    ):
        self.aggregation_pipeline = aggregation_pipeline
        self.document_model = document_model
        self.aggregation_model = aggregation_model
        self.find_parameters = find_parameters
        self.init_cursor(return_model=aggregation_model)

    @property
    def motor_cursor(self):
        match_pipeline = (
            [{"$match": self.find_parameters.get_filter_query()}]
            if self.find_parameters.find_expressions
            else []
        )
        aggregation_pipeline = match_pipeline + self.aggregation_pipeline
        return self.document_model.get_motor_collection().aggregate(
            aggregation_pipeline
        )
