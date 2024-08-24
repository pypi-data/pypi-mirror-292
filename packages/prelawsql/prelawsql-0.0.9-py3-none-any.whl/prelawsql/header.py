import re

from bs4 import BeautifulSoup
from citation_title import cite_title
from citation_utils import Citation

from .clean import is_text_possible


def is_opinion_label(text: str) -> bool:
    if not is_text_possible(text, max_len=50):
        return False

    candidate = text.lower()
    for marker in ("opinion", "dissent", "separate", "concur"):
        if marker in candidate:
            return True
    return False


ENBANC_PATTERN = re.compile(r"banc", re.I)
DIVISION_PATTERN = re.compile(r"division", re.I)


def spaced(z: str):
    return re.compile("\\s*".join(i for i in z), re.I | re.X)


DECISION_PATTERN = spaced("decision")
RESOLUTION_PATTERN = spaced("resolution")


def clean_composition(soup: BeautifulSoup) -> str | None:
    targets = soup("h2")
    if not targets:
        return None

    text = targets[0].text.title()

    if ENBANC_PATTERN.search(text):
        return "En Banc"
    elif DIVISION_PATTERN.search(text):
        return "Division"
    return None


def clean_date(soup: BeautifulSoup) -> str | None:
    targets = soup("h2")
    if not targets:
        return None


def clean_category(soup: BeautifulSoup) -> str | None:
    targets = soup("h3")
    if not targets:
        return None

    candidates = targets[0].find_all(string=True, recursive=False)
    if not candidates:
        return None

    text = candidates[-1].strip()

    if DECISION_PATTERN.search(text):
        return "Decision"

    elif RESOLUTION_PATTERN.search(text):
        return "Resolution"

    # Some cases are improperly formatted / spelled or use different phrases
    # "Ecision", "Kapasyahan" - 29848, "Opinion" - 36567, or lack label entirely - 60046
    return None


def clean_heading_from_title(raw_title: str):
    full_title = (
        raw_title.title()
        .strip()
        .removesuffix("D E C I S I O N")
        .strip()
        .removesuffix("R E S O L U T I O N")
        .strip()
    )
    return {"title": full_title, "short": cite_title(full_title)}


def get_header_citation(soup: BeautifulSoup):
    """Initial text at the header of decisions. Often found before
    the first <br> tag and after the header."""
    breaks = soup("br")
    if not breaks:
        return None

    for counter, el in enumerate(breaks, start=1):
        el["id"] = f"mark-{counter}"

    first_br = breaks[0]
    body = str(soup)
    marker = str(first_br)
    index = body.find(marker) + len(marker)
    candidate = body[:index]
    if not is_text_possible(candidate, max_len=150):
        return None

    soup = BeautifulSoup(candidate, "lxml")
    texts = soup(string=True)
    for text in texts:
        check_text = text.lower().strip()
        if "-library" in check_text:
            continue
        if citation := Citation.extract_citation(check_text):
            return citation
    return None
