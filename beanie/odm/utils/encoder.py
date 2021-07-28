from collections import defaultdict
from datetime import datetime
from enum import Enum
from pathlib import PurePath
from types import GeneratorType
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from uuid import UUID

from pydantic import BaseModel

from bson import ObjectId

from .bson import ENCODERS_BY_TYPE

SetIntStr = Set[Union[int, str]]
DictIntStrAny = Dict[Union[int, str], Any]


def generate_encoders_by_class_tuples(
    type_encoder_map: Dict[Any, Callable[[Any], Any]]
) -> Dict[Callable[[Any], Any], Tuple[Any, ...]]:
    encoders_by_class_tuples: Dict[
        Callable[[Any], Any], Tuple[Any, ...]
    ] = defaultdict(tuple)
    for type_, encoder in type_encoder_map.items():
        encoders_by_class_tuples[encoder] += (type_,)
    return encoders_by_class_tuples


encoders_by_class_tuples = generate_encoders_by_class_tuples(ENCODERS_BY_TYPE)


def bsonable_encoder(
    obj: Any,
    exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    by_alias: bool = True,
    custom_encoder: Dict[Any, Callable[[Any], Any]] = {},
) -> Any:
    if exclude is not None and not isinstance(exclude, (set, dict)):
        exclude = set(exclude)
    if isinstance(obj, BaseModel):
        encoder = getattr(obj.__config__, "bson_encoders", {})
        if custom_encoder:
            encoder.update(custom_encoder)
        obj_dict = obj.dict(
            exclude=exclude,  # type: ignore # in Pydantic
            by_alias=by_alias,
        )
        return bsonable_encoder(
            obj_dict,
            custom_encoder=encoder,
        )
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, PurePath):
        return str(obj)
    if isinstance(
        obj, (str, int, float, ObjectId, UUID, datetime, type(None))
    ):
        return obj
    if isinstance(obj, dict):
        encoded_dict = {}
        for key, value in obj.items():
            encoded_value = bsonable_encoder(
                value,
                by_alias=by_alias,
                custom_encoder=custom_encoder,
            )
            encoded_dict[key] = encoded_value
        return encoded_dict
    if isinstance(obj, (list, set, frozenset, GeneratorType, tuple)):
        return [
            bsonable_encoder(
                item,
                exclude=exclude,
                by_alias=by_alias,
                custom_encoder=custom_encoder,
            )
            for item in obj
        ]
    if custom_encoder:
        if type(obj) in custom_encoder:
            return custom_encoder[type(obj)](obj)
        for encoder_type, encoder in custom_encoder.items():
            if isinstance(obj, encoder_type):
                return encoder(obj)
    if type(obj) in ENCODERS_BY_TYPE:
        return ENCODERS_BY_TYPE[type(obj)](obj)
    for encoder, classes_tuple in encoders_by_class_tuples.items():
        if isinstance(obj, classes_tuple):
            return encoder(obj)

    errors: List[Exception] = []
    try:
        data = dict(obj)
    except Exception as e:
        errors.append(e)
        try:
            data = vars(obj)
        except Exception as e:
            errors.append(e)
            raise ValueError(errors)
    return bsonable_encoder(
        data,
        by_alias=by_alias,
        custom_encoder=custom_encoder,
    )
