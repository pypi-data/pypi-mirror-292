import logging
from enum import IntEnum, StrEnum, auto

from bs4 import BeautifulSoup, Tag

from .config import SOURCE
from .network import url_to_soup


class Listing(StrEnum):
    """Contains month names which can pe paired with source and year."""

    Jan = auto()
    Feb = auto()
    Mar = auto()
    Apr = auto()
    May = auto()
    Jun = auto()
    Jul = auto()
    Aug = auto()
    Sep = auto()
    Oct = auto()
    Nov = auto()
    Dec = auto()


class Source(IntEnum):
    Decision = 1
    RepublicAct = 2

    def set_url(self, year: int, month: Listing) -> str:
        """
        Examples:
            >>> import os
            >>> from prelawsql import Listing, Source
            >>> source = os.environ['SOURCE']
            >>> url = Source.Decision.set_url(2024, Listing.Feb)
            >>> url.removeprefix(source)
            '/docmonth/feb/2024/1'
        """
        return f"{SOURCE.geturl()}/docmonth/{month}/{year}/{self}"

    def fetch_url(self, year: int, month: Listing) -> BeautifulSoup | None:
        url = self.set_url(year, month)
        result = url_to_soup(url=url)
        return result

    def fetch_tags(self, year: int, month: Listing) -> list[Tag]:
        soup = self.fetch_url(year, month)
        if not soup:
            raise Exception(f"Missing content from {month=} on {year=}")
        items = soup(id="container_title")[0]("li")

        msg = f"Received {len(items)=} from {self.name.lower}s {month}/{year}"
        logging.debug(msg)
        return items
