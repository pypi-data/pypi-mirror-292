from http import HTTPStatus

import httpx
from bs4 import BeautifulSoup


def url_to_content(url: str) -> bytes | None:
    """Get contents of `url`, e.g. html or PDF."""
    res = httpx.get(url, follow_redirects=True, timeout=90.0)
    if res.status_code == HTTPStatus.OK:
        return res.content
    return None


def url_to_soup(url: str) -> BeautifulSoup | None:
    """Creates a soup object from the response of the `url`."""
    content = url_to_content(url=url)
    if content:
        return BeautifulSoup(content, "lxml")
    return None
