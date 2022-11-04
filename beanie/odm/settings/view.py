from typing import List, Dict, Any, Union, Type

from beanie.odm.settings.base import ItemSettings


class ViewSettings(ItemSettings):
    source: Union[str, Type]
    pipeline: List[Dict[str, Any]]
