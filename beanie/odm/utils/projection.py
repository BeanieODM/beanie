from typing import Dict, Type

from pydantic import BaseModel


def get_projection(model: Type[BaseModel]) -> Dict[str, int]:
    document_projection: Dict[str, int] = {}
    for name, field in model.__fields__.items():
        document_projection[field.alias] = 1
    return document_projection
