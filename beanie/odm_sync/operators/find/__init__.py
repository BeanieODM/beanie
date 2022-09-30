from abc import ABC

from beanie.odm_sync.operators import BaseOperator


class BaseFindOperator(BaseOperator, ABC):
    ...
