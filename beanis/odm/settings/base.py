from typing import Optional

from pydantic import BaseModel
from redis import Redis
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, Type


class ItemSettings(BaseModel):
    name: Optional[str] = None

    motor_db: Optional[Redis] = None
    class_id: str = "_class_id"
    keep_nulls: bool = False
    use_revision: bool = False
    is_root: bool = False
    use_state_management: bool = False
    bson_encoders: Dict[Any, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True
