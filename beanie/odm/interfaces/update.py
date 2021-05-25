from abc import abstractmethod
from typing import Dict, Mapping, Union, Any, Optional

from pymongo.client_session import ClientSession

from beanie.odm.fields import ExpressionField
from beanie.odm.operators.update.general import (
    Set,
    CurrentDate,
    Inc,
)


class UpdateMethods:
    """
    Update methods
    """

    @abstractmethod
    def update(
        self,
        *args: Union[Dict[str, Any], Mapping[str, Any]],
        session: Optional[ClientSession] = None
    ):
        return self

    def set(
        self,
        expression: Dict[Union[ExpressionField, str], Any],
        session: Optional[ClientSession] = None,
    ):
        """
        Set values

        Example:

        ```python

        class Sample(Document):
            one: int

        await Document.find(Sample.one == 1).set({Sample.one: 100})

        ```

        Uses [Set operator](https://roman-right.github.io/beanie/api/operators/update/#set)

        :param expression: Dict[Union[ExpressionField, str], Any] - keys and
        values to set
        :param session: Optional[ClientSession] - pymongo session
        :return: self
        """
        return self.update(Set(expression), session=session)

    def current_date(
        self,
        expression: Dict[Union[ExpressionField, str], Any],
        session: Optional[ClientSession] = None,
    ):
        """
        Set current date

        Uses [CurrentDate operator](https://roman-right.github.io/beanie/api/operators/update/#currentdate)

        :param expression: Dict[Union[ExpressionField, str], Any]
        :param session: Optional[ClientSession] - pymongo session
        :return: self
        """
        return self.update(CurrentDate(expression), session=session)

    def inc(
        self,
        expression: Dict[Union[ExpressionField, str], Any],
        session: Optional[ClientSession] = None,
    ):
        """
        Increment

        Example:

        ```python

        class Sample(Document):
            one: int

        await Document.find(Sample.one == 1).inc({Sample.one: 100})

        ```

        Uses [Inc operator](https://roman-right.github.io/beanie/api/operators/update/#inc)

        :param expression: Dict[Union[ExpressionField, str], Any]
        :param session: Optional[ClientSession] - pymongo session
        :return: self
        """
        return self.update(Inc(expression), session=session)
