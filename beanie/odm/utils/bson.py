import datetime
import re
import sys
from collections import deque
from decimal import Decimal
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from typing import Any, Callable, Dict, Type
from uuid import UUID

if sys.version_info >= (3, 7):
    Pattern = re.Pattern
else:
    # python 3.6
    Pattern = re.compile("a").__class__

from pydantic import SecretBytes, SecretStr
from pydantic.color import Color
from pydantic.json import decimal_encoder, isoformat

ENCODERS_BY_TYPE: Dict[Type[Any], Callable[[Any], Any]] = {
    Color: str,
    datetime.date: isoformat,
    datetime.time: isoformat,
    datetime.timedelta: lambda td: td.total_seconds(),
    Decimal: decimal_encoder,
    deque: list,
    IPv4Address: str,
    IPv4Interface: str,
    IPv4Network: str,
    IPv6Address: str,
    IPv6Interface: str,
    IPv6Network: str,
    # Pattern: lambda o: o.pattern, # bson.regex.Regex?
    SecretBytes: str,
    SecretStr: str,
    UUID: str,
}
