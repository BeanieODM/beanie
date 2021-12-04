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

from bson import ObjectId, DBRef
from pydantic import BaseModel

from .bson import ENCODERS_BY_TYPE
from ..fields import LinkTypes


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
        to_db: bool = False,
    ) -> Any:
        from beanie.odm.documents import Document

        if custom_encoder is None:
            custom_encoder = {}
        if exclude is None:
            exclude = {}
        if not isinstance(exclude, (set, dict)):
            exclude = set(exclude)
        if isinstance(obj, Document):
            encoders = obj.get_settings().model_settings.bson_encoders
            if custom_encoder:
                encoders.update(custom_encoder)

            link_fields = obj.get_link_fields()
            obj_dict = {}
            for k, o in obj._iter(to_dict=False, by_alias=by_alias):
                if k not in exclude:  # TODO get exclude from the class
                    if link_fields and k in link_fields:
                        if link_fields[k].link_type == LinkTypes.LIST:
                            obj_dict[k] = [link.to_ref() for link in o]
                        if link_fields[k].link_type == LinkTypes.DIRECT:
                            obj_dict[k] = o.to_ref()
                    else:
                        obj_dict[k] = o
            return self.encode(obj_dict, custom_encoder=encoders, to_db=to_db)
        if isinstance(obj, BaseModel):
            encoders = {}
            if custom_encoder:
                encoders.update(custom_encoder)
            obj_dict = {}
            for k, o in obj._iter(to_dict=False, by_alias=by_alias):
                if k not in exclude:  # TODO get exclude from the class
                    obj_dict[k] = o

            return self.encode(obj_dict, custom_encoder=encoders, to_db=to_db)
        if isinstance(obj, dict):
            encoded_dict = {}
            for key, value in obj.items():
                encoded_value = self.encode(
                    value,
                    by_alias=by_alias,
                    custom_encoder=custom_encoder,
                    to_db=to_db,
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
                    to_db=to_db,
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
        if isinstance(
            obj, (str, int, float, ObjectId, UUID, datetime, type(None), DBRef)
        ):
            return obj

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
            data, by_alias=by_alias, custom_encoder=custom_encoder, to_db=to_db
        )


bson_encoder = Encoder()
