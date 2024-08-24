import re

_escape_fts_re = re.compile(r'\s+|(".*?")')


def set_tokens(q: str):
    """
    This is datasette's [escape_fts()](https://github.com/simonw/datasette/blob/8e18c7943181f228ce5ebcea48deb59ce50bee1f/datasette/utils/__init__.py#L818-L829.)

    For tokens that do not have double quotes, add a double quote.
    """  # noqa: E501
    # If query has unbalanced ", add one at end
    if q.count('"') % 2:
        q += '"'

    # Looks for spaces (1) ' ' and (2) double quoted text
    # within the query `q` passed. Sample of (2): "this is double-quoted"
    bits = _escape_fts_re.split(q)
    tokens = [b for b in bits if b and b != '""']
    return [f'"{t}"' if not t.startswith('"') else t for t in tokens]


FTS_BOOLEAN = re.compile(
    r"""
    ^
    (
        "AND"|
        "OR"|
        "NOT"|
        "\(+"| # handles (((
        "\)+" # handles )))
    )
    $
    """,
    re.X,
)


def fts_query(query: str) -> str:
    """This modifies datasette's generic `escape_fts()` function by
    enabling boolean operators of `fts5`. All tokens containing
    said operators are _not_ unescaped.

    Examples:
        >>> uncap_and = '"eminent domain" and "police power"'
        >>> fts_query(uncap_and)
        '"eminent domain" "and" "police power"'
        >>> cap_AND = '"eminent domain" AND "police power"'
        >>> fts_query(cap_AND)
        '"eminent domain" AND "police power"'
        >>> parenthesis_NOT = '("eminent domain" NOT "taxation" AND "police power")'
        >>> fts_query(parenthesis_NOT)
        '( "eminent domain" NOT "taxation" AND "police power" )'


    Args:
        query (str): A search string that will be used as the right hand operator for an fts `MATCH`

    Returns:
        str: A properly formatted search string where double quotes and parenthesis are incorporated.
    """  # noqa: E501
    tokens = set_tokens(query)
    for idx, qb in enumerate(tokens):
        if FTS_BOOLEAN.fullmatch(qb):
            tokens[idx] = qb.strip('"')  # remove quotes when applicable
    return " ".join(tokens)
