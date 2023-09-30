import datetime
from ipaddress import IPv4Address
from typing import List, Tuple

from pydantic import BaseModel


class Url(BaseModel):
    shortcut: str
    url: str
    owner: str


class PartialUrl(BaseModel):
    shortcut: str
    owner: str


class StatisticsUrl(BaseModel):
    shortcut: str
    url: str
    visitors: List[Tuple[IPv4Address, datetime.datetime]]
    owner: str
