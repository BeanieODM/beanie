from typing import Any, Dict, Optional, Type

from pydantic import BaseModel


class ModelSettings(BaseModel):
    projection: Optional[Dict[str, Any]]
    use_state_management: bool = False
    validate_on_save: bool = False

    @classmethod
    def parse_settings(cls, settings_class: Optional[Type]) -> "ModelSettings":
        if settings_class is not None:
            return cls.parse_obj(vars(settings_class))
        else:
            return ModelSettings()
