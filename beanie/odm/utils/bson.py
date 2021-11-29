import datetime
from collections import deque
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
from typing import Any, Callable, Dict, Type

from pydantic import SecretBytes, SecretStr
from pydantic.color import Color
from pydantic.json import isoformat

from beanie.odm.fields import Link

ENCODERS_BY_TYPE: Dict[Type[Any], Callable[[Any], Any]] = {
    Color: str,
    datetime.date: isoformat,
    datetime.time: isoformat,
    datetime.timedelta: lambda td: td.total_seconds(),
    Decimal: float,
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
    Link: lambda l: l.ref,
}
