from collections import deque
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from pathlib import PurePath
from types import GeneratorType
from typing import (
    AbstractSet,
    List,
    Mapping,
    Union,
    Optional,
)
from typing import Any, Callable, Dict, Type
from uuid import UUID

import bson
from bson import ObjectId, DBRef, Binary, Decimal128
from pydantic import BaseModel
from pydantic import SecretBytes, SecretStr
from pydantic.color import Color

from beanie.odm.fields import Link, LinkTypes
from beanie.odm import documents

ENCODERS_BY_TYPE: Dict[Type[Any], Callable[[Any], Any]] = {
    Color: str,
    timedelta: lambda td: td.total_seconds(),
    Decimal: Decimal128,
    deque: list,
    IPv4Address: str,
    IPv4Interface: str,
    IPv4Network: str,
    IPv6Address: str,
    IPv6Interface: str,
    IPv6Network: str,
    SecretBytes: SecretBytes.get_secret_value,
    SecretStr: SecretStr.get_secret_value,
    Enum: lambda o: o.value,
    PurePath: str,
    Link: lambda l: l.ref,  # noqa: E741
    bytes: lambda b: b if isinstance(b, Binary) else Binary(b),
    UUID: lambda u: bson.Binary.from_uuid(u),
}


class Encoder:
    """
    BSON encoding class
    """

    def __init__(
        self,
        exclude: Union[
            AbstractSet[Union[str, int]], Mapping[Union[str, int], Any], None
        ] = None,
        custom_encoders: Optional[Dict[Type, Callable]] = None,
        by_alias: bool = True,
        to_db: bool = False,
    ):
        self.exclude = exclude or {}
        self.by_alias = by_alias
        self.custom_encoders = custom_encoders or {}
        self.to_db = to_db

    def encode(self, obj: Any):
        """
        Run the encoder
        """
        return self._encode(obj=obj)

    def encode_document(self, obj):
        """
        Beanie Document class case
        """
        obj.parse_store()

        encoder = Encoder(
            custom_encoders=obj.get_settings().bson_encoders,
            by_alias=self.by_alias,
            to_db=self.to_db,
        )

        link_fields = obj.get_link_fields()
        obj_dict: Dict[str, Any] = {}
        if obj.get_settings().union_doc is not None:
            obj_dict["_class_id"] = obj.__class__.__name__
        if obj._inheritance_inited:
            obj_dict["_class_id"] = obj._class_id

        for k, o in obj._iter(to_dict=False, by_alias=self.by_alias):
            if k not in self.exclude:
                if link_fields and k in link_fields:
                    if link_fields[k].link_type == LinkTypes.LIST:
                        obj_dict[k] = [link.to_ref() for link in o]
                    if link_fields[k].link_type == LinkTypes.DIRECT:
                        obj_dict[k] = o.to_ref()
                    if link_fields[k].link_type == LinkTypes.OPTIONAL_DIRECT:
                        if o is not None:
                            obj_dict[k] = o.to_ref()
                        else:
                            obj_dict[k] = o
                    if link_fields[k].link_type == LinkTypes.OPTIONAL_LIST:
                        if o is not None:
                            obj_dict[k] = [link.to_ref() for link in o]
                        else:
                            obj_dict[k] = o
                else:
                    obj_dict[k] = o
                obj_dict[k] = encoder.encode(obj_dict[k])
        return obj_dict

    def encode_base_model(self, obj):
        """
        BaseModel case
        """
        obj_dict = {}
        for k, o in obj._iter(to_dict=False, by_alias=self.by_alias):
            if k not in self.exclude:
                obj_dict[k] = self._encode(o)

        return obj_dict

    def encode_dict(self, obj):
        """
        Dictionary case
        """
        return {key: self._encode(value) for key, value in obj.items()}

    def encode_iterable(self, obj):
        """
        Iterable case
        """
        return [self._encode(item) for item in obj]

    def _encode(
        self,
        obj,
    ) -> Any:
        """"""
        if self.custom_encoders:
            if type(obj) in self.custom_encoders:
                return self.custom_encoders[type(obj)](obj)
            for encoder_type, encoder in self.custom_encoders.items():
                if isinstance(obj, encoder_type):
                    return encoder(obj)
        if type(obj) in ENCODERS_BY_TYPE:
            return ENCODERS_BY_TYPE[type(obj)](obj)
        for cls, encoder in ENCODERS_BY_TYPE.items():
            if isinstance(obj, cls):
                return encoder(obj)

        if isinstance(obj, documents.Document):
            return self.encode_document(obj)
        if isinstance(obj, BaseModel):
            return self.encode_base_model(obj)
        if isinstance(obj, dict):
            return self.encode_dict(obj)
        if isinstance(obj, (list, set, frozenset, GeneratorType, tuple)):
            return self.encode_iterable(obj)

        if isinstance(
            obj, (str, int, float, ObjectId, datetime, type(None), DBRef)
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
        return self._encode(data)
