from datetime import datetime
from ipaddress import IPv4Address

from pymongo import MongoClient

from consts import (
    MONGO_COLLECTION_NAME,
    MONGO_DATABASE_NAME,
    STATISTICS_FIELD_SHORTCUT,
    STATISTICS_FIELD_URL,
    STATISTICS_FIELD_VISITORS,
)
from shortcuts_db import ShortcutsDB, StatusCodes
from url import DeleteUrl, StatisticsUrl, Url


class MongoShortcutsDB(ShortcutsDB):
    def __init__(self, connection: str):
        self.client = MongoClient(connection)
        self.collection = self.client[MONGO_DATABASE_NAME][
            MONGO_COLLECTION_NAME
        ]

    def expand_url(
        self, shortcut: str, user_ip: IPv4Address
    ) -> StatisticsUrl | None:
        item = self.collection.find_one({STATISTICS_FIELD_SHORTCUT: shortcut})

        url_item = None
        if item:
            item[STATISTICS_FIELD_VISITORS] = [
                (IPv4Address(ip), time)
                for ip, time in item[STATISTICS_FIELD_VISITORS]
            ]
            url_item = StatisticsUrl(**item)
            self._log_visit(url_item, user_ip)

        return url_item

    def create(self, item: Url) -> StatusCodes:
        if self.check_exists(item.shortcut):
            return StatusCodes.NOT_EXIST

        stats_url = StatisticsUrl(
            shortcut=item.shortcut,
            url=item.url,
            visitors=[],
            owner=item.owner,
        )

        self.collection.insert_one(stats_url.model_dump())
        return StatusCodes.SUCCESS

    def update(self, url: Url) -> StatusCodes:
        if not self.check_exists(url.shortcut):
            return StatusCodes.NOT_EXIST

        expanded_url = self.expand_url(url.shortcut)

        if not expanded_url.owner == url.owner:
            return StatusCodes.WRONG_OWNER

        self.collection.update_one(
            {STATISTICS_FIELD_SHORTCUT: url.shortcut},
            {
                "$set": {
                    STATISTICS_FIELD_SHORTCUT: url.shortcut,
                    STATISTICS_FIELD_URL: url.url,
                }
            },
        )
        return StatusCodes.SUCCESS

    def delete(self, url: DeleteUrl) -> StatusCodes:
        if not self.check_exists(url.shortcut):
            return StatusCodes.NOT_EXIST

        expanded_url = self.expand_url(url.shortcut)

        if not expanded_url.owner == url.owner:
            return StatusCodes.WRONG_OWNER

        self.collection.delete_one(
            {STATISTICS_FIELD_SHORTCUT: url.shortcut},
        )
        return StatusCodes.SUCCESS

    def check_exists(self, shortcut: str) -> bool:
        item = self.collection.find_one({STATISTICS_FIELD_SHORTCUT: shortcut})

        return item is not None

    def _log_visit(self, url: StatisticsUrl, user_ip: IPv4Address) -> None:
        item = self.collection.find_one(
            {STATISTICS_FIELD_SHORTCUT: url.shortcut}
        )

        self.collection.update_one(
            {STATISTICS_FIELD_SHORTCUT: url.shortcut},
            {
                "$push": {
                    STATISTICS_FIELD_VISITORS: [str(user_ip), datetime.now()]
                }
            },
        )
