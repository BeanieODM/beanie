from typing import Union, List, Tuple, Mapping

from pydantic import BaseModel

from beanie.odm.models import SortDirection
from beanie.odm.operators.find.logical import And


class FindParameters(BaseModel):  # TODO think if this is needed
    find_expressions: List[Union[dict, Mapping]] = []
    sort_expressions: List[Tuple[str, SortDirection]] = []
    skip_number: int = 0
    limit_number: int = 0

    def get_filter_query(self):
        return And(*self.find_expressions)
