from abc import ABC, abstractmethod
from enum import IntEnum

from ipaddress import IPv4Address

from unlink.url import PartialUrl, StatisticsUrl, Url


class StatusCodes(IntEnum):
    SUCCESS = 0
    NOT_EXIST = 1
    WRONG_OWNER = 2


class ShortcutsDB(ABC):
    @abstractmethod
    def expand_url(self, shortcut: str) -> StatisticsUrl | None:
        raise NotImplemented()

    @abstractmethod
    def create(self, url: Url) -> StatusCodes:
        raise NotImplemented()

    @abstractmethod
    def update(self, url: Url) -> StatusCodes:
        raise NotImplemented()

    @abstractmethod
    def delete(self, url: PartialUrl) -> StatusCodes:
        raise NotImplemented()

    @abstractmethod
    def check_exists(self, shortcut: str) -> bool:
        raise NotImplemented()

    @abstractmethod
    def log_entry(self, shortcut: str, user_ip: IPv4Address) -> None:
        raise NotImplemented()

    @abstractmethod
    def get_url_stats(self, url: PartialUrl) -> StatusCodes | StatisticsUrl:
        raise NotImplemented()
