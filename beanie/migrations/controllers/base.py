from abc import ABC, abstractmethod
from typing import List, Type

from beanie import Document


class BaseMigrationController(ABC):
    @abstractmethod
    async def run(self, session):
        pass

    @property
    @abstractmethod
    def models(self) -> List[Type[Document]]:
        pass
