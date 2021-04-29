from abc import abstractmethod
from typing import Dict, Union, Any, Optional

from pymongo.client_session import ClientSession

from beanie.odm.fields import CollectionField
from beanie.odm.operators.update.general import (
    Set,
    CurrentDate,
    Inc,
)


class UpdateMethods:
    @abstractmethod
    def update(self, *args, session: ClientSession = None):
        ...

    def set(
        self,
        expression: Dict[Union[CollectionField, str], Any],
        session: Optional[ClientSession] = None,
    ):
        return self.update(Set(expression), session=session)

    def current_date(
        self,
        expression: Dict[Union[CollectionField, str], Any],
        session: ClientSession = None,
    ):
        return self.update(CurrentDate(expression), session=session)

    def inc(
        self,
        expression: Dict[Union[CollectionField, str], Any],
        session: ClientSession = None,
    ):
        return self.update(Inc(expression), session=session)
