from collections import defaultdict
from datetime import datetime
from types import GeneratorType
from typing import (
    AbstractSet,
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Tuple,
    Union,
)
from uuid import UUID

from bson import ObjectId
from pydantic import BaseModel

from .bson import ENCODERS_BY_TYPE


class Encoder:
    def __init__(self):
        self.encoders_by_class_tuples: Dict[
            Callable[[Any], Any], Tuple[Any, ...]
        ] = defaultdict(tuple)
        for type_, encoder in ENCODERS_BY_TYPE.items():
            self.encoders_by_class_tuples[encoder] += (type_,)

    def encode(
        self,
        obj: Any,
        exclude: Union[
            AbstractSet[Union[str, int]], Mapping[Union[str, int], Any], None
        ] = None,
        by_alias: bool = True,
        custom_encoder: Dict[Any, Callable[[Any], Any]] = None,
    ) -> Any:
        if custom_encoder is None:
            custom_encoder = {}
        if exclude is not None and not isinstance(exclude, (set, dict)):
            exclude = set(exclude)
        if isinstance(obj, BaseModel):
            encoders = {}
            collection_class = getattr(obj, "Collection", None)
            if collection_class:
                encoders = vars(collection_class).get("bson_encoders", {})
            if custom_encoder:
                encoders.update(custom_encoder)
            obj_dict = obj.dict(
                exclude=exclude,  # type: ignore # in Pydantic
                by_alias=by_alias,
            )
            return self.encode(
                obj_dict,
                custom_encoder=encoders,
            )
        if isinstance(
            obj, (str, int, float, ObjectId, UUID, datetime, type(None))
        ):
            return obj
        if isinstance(obj, dict):
            encoded_dict = {}
            for key, value in obj.items():
                encoded_value = self.encode(
                    value,
                    by_alias=by_alias,
                    custom_encoder=custom_encoder,
                )
                encoded_dict[key] = encoded_value
            return encoded_dict
        if isinstance(obj, (list, set, frozenset, GeneratorType, tuple)):
            return [
                self.encode(
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
        for encoder, classes_tuple in self.encoders_by_class_tuples.items():
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
        return self.encode(
            data,
            by_alias=by_alias,
            custom_encoder=custom_encoder,
        )


bson_encoder = Encoder()
