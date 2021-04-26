from typing import Type, List, Union, Mapping

from pydantic import BaseModel

from beanie.odm.query_builder.queries.cursor import BaseCursorQuery


class AggregationQuery(BaseCursorQuery):
    def __init__(
        self,
        aggregation_query: List[Union[dict, Mapping]],
        document_class: Type["Document"],
        aggregation_model: Type[BaseModel],  # TODO naming
    ):
        self.aggregation_query = aggregation_query
        self.document_class = document_class
        self.aggregation_model = aggregation_model
        self.init_cursor(return_model=aggregation_model)

    @property
    def motor_cursor(self):
        return self.document_class.get_motor_collection().aggregate(
            self.aggregation_query
        )
