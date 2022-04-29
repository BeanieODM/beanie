from datetime import timedelta
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, Field


class ModelSettings(BaseModel):
    projection: Optional[Dict[str, Any]] = None
    use_state_management: bool = False
    state_management_replace_objects: bool = False
    validate_on_save: bool = False
    use_revision: bool = False
    use_cache: bool = False
    cache_capacity: int = 32
    cache_expiration_time: timedelta = timedelta(minutes=10)
    bson_encoders: Dict[Any, Any] = Field(default_factory=dict)
    multi_model: bool = False

    @classmethod
    def init(
        cls,
        document_model: Type,
    ) -> "ModelSettings":
        settings_class = getattr(document_model, "Settings", None)
        if settings_class is not None:
            return cls.parse_obj(vars(settings_class))
        else:
            return ModelSettings()
