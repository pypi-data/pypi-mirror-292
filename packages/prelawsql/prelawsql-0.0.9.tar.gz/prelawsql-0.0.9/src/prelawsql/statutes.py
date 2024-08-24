import datetime
import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum, auto
from functools import cached_property
from pathlib import Path
from typing import NamedTuple, Self

import yaml
from rich.progress import track
from slugify import slugify
from sqlite_utils.db import Database, Table

from .config import DATA_DIR, DB_FILE, STAT_DIR, STAT_TMP, TREE_GLOB
from .db import add_idx, check_table


class StatuteTitleCategory(StrEnum):
    """
    A Rule in the Philippines involves various denominations.
    It can be referred to by its

    1. `official` title
    2. `serial` title
    3. `short` title
    4. `alias` titles
    4. `searchable` titles

    Consider something like the _Maceda Law_ which can be dissected as follows:

    Category | Mandatory | Nature | Description | Example | Matching Strategy
    --:|:--:|:--:|:--|:--|--:
    `official` | yes | official | full length title | _AN ACT TO PROVIDE PROTECTION TO BUYERS OF REAL ESTATE ON INSTALLMENT PAYMENTS_ | [Statute Details][statutes]
    `serial` | yes | official | `Statute Category` + serial identifier. | _Republic Act No. 6552_ | Serial Pattern regex matching
    `short`  | no | official | may be declared in body of statute | _Realty Installment Buyer Act_ | A helper function, upstream
    `alias`  | no | unofficial | popular, undocumented means of referring to a statute | _Maceda Law_ | Named Pattern regex matching
    `searchables`  | no | unofficial | easy way for users to reference via search | ra 6552 | --
    """  # noqa: E501

    Official = auto()
    Serial = auto()
    Alias = auto()
    Short = auto()
    Searchable = auto()


class StatuteSerialCategory(StrEnum):
    """
    It would be difficult to identify rules if they were arbitrarily named
    without a fixed point of reference. For instance the _Civil Code of the
    Philippines_,  an arbitrary collection of letters, would be hard to find
    if laws were organized alphabetically.

    Fortunately, each Philippine `serial`-title rule belongs to an
    assignable `StatuteSerialCategory`:

    Serial Category `name` | Shorthand `value`
    --:|:--
    Republic Act | ra
    Commonwealth Act | ca
    Act | act
    Constitution | const
    Spain | spain
    Batas Pambansa | bp
    Presidential Decree | pd
    Executive Order | eo
    Letter of Instruction | loi
    Veto Message | veto
    Rules of Court | roc
    Bar Matter | rule_bm
    Administrative Matter | rule_am
    Resolution en Banc | rule_reso
    Circular OCA | oca_cir
    Circular SC | sc_cir

    This is not an official reference but
    rather a non-exhaustive taxonomy of Philippine legal rules mapped to
    a `enum.Enum` object.

    Enum | Purpose
    --:|:--
    `name` | for _most_ members, can "uncamel"-ized to produce serial title
    `value` | (a) folder for discovering path / (b) category usable in the database table

    Using this model simplifies the ability to navigate rules. Going back to
    the _Civil Code_ described above, we're able to describe it as follows:

    Aspect | Description
    --:|:--
    serial title | _Republic Act No. 386_
    assumed folder path |`/ra/386`
    category | ra
    id | 386

    Mapped to its `Rule` counterpart we get:

    Field | Value | Description
    :--:|:--:|:--
    `cat`| ra | Serial statute category
    `id` | 386 | Serial identifier of the category

    ## Purpose

    Knowing the path to a `Rule`, we can later [extract its contents][statutes].

    Examples:
        >>> StatuteSerialCategory
        <enum 'StatuteSerialCategory'>
        >>> StatuteSerialCategory._member_map_
        {'RepublicAct': 'ra', 'CommonwealthAct': 'ca', 'Act': 'act', 'Constitution': 'const', 'Spain': 'spain', 'BatasPambansa': 'bp', 'PresidentialDecree': 'pd', 'ExecutiveOrder': 'eo', 'LetterOfInstruction': 'loi', 'VetoMessage': 'veto', 'RulesOfCourt': 'roc', 'BarMatter': 'rule_bm', 'AdministrativeMatter': 'rule_am', 'ResolutionEnBanc': 'rule_reso', 'CircularOCA': 'oca_cir', 'CircularSC': 'sc_cir'}
    """  # noqa: E501

    RepublicAct = "ra"
    CommonwealthAct = "ca"
    Act = "act"
    Constitution = "const"
    Spain = "spain"
    BatasPambansa = "bp"
    PresidentialDecree = "pd"
    ExecutiveOrder = "eo"
    LetterOfInstruction = "loi"
    VetoMessage = "veto"
    RulesOfCourt = "roc"
    BarMatter = "rule_bm"
    AdministrativeMatter = "rule_am"
    ResolutionEnBanc = "rule_reso"
    CircularOCA = "oca_cir"
    CircularSC = "sc_cir"

    def __repr__(self) -> str:
        """Uses value of member `ra` instead of Enum default
        `<StatuteSerialCategory.RepublicAct: 'ra'>`. It becomes to
        use the following conventions:

        Examples:
            >>> StatuteSerialCategory('ra')
            'ra'
            >>> StatuteSerialCategory.RepublicAct
            'ra'

        Returns:
            str: The value of the Enum member
        """
        return str.__repr__(self.value)

    def serialize(self, idx: str) -> str | None:
        """Given a member item and a valid serialized identifier, create a serial title.

        Note that the identifier must be upper-cased to make this consistent
        with the textual convention, e.g.

        Examples:
            >>> StatuteSerialCategory.PresidentialDecree.serialize('570-a')
            'Presidential Decree No. 570-A'
            >>> StatuteSerialCategory.AdministrativeMatter.serialize('03-06-13-sc')
            'Administrative Matter No. 03-06-13-SC'

        Args:
            idx (str): The number to match with the category

        Returns:
            str | None: The serialized text, e.g. `category` + `idx`
        """

        def uncamel(cat: StatuteSerialCategory):
            """See [Stack Overflow](https://stackoverflow.com/a/9283563)"""
            x = r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))"
            return re.sub(x, r" \1", cat.name)

        match self:  # noqa: E999 ; ruff complains but this is valid Python
            case StatuteSerialCategory.Spain:
                small_idx = idx.lower()
                if small_idx in ["civil", "penal"]:
                    return f"Spanish {idx.title()} Code"
                elif small_idx == "commerce":
                    return "Code of Commerce"
                raise SyntaxWarning(f"{idx=} invalid serial of {self}")

            case StatuteSerialCategory.Constitution:
                if idx.isdigit() and int(idx) in [1935, 1973, 1987]:
                    return f"{idx} Constitution"
                raise SyntaxWarning(f"{idx=} invalid serial of {self}")

            case StatuteSerialCategory.RulesOfCourt:
                if idx in ["1918", "1940", "1964"]:
                    return f"{idx} Rules of Court"
                elif idx in ["cpr"]:
                    return "Code of Professional Responsibility"
                raise SyntaxWarning(f"{idx=} invalid serial of {self}")

            case StatuteSerialCategory.VetoMessage:
                """No need to specify No.; understood to mean a Republic Act"""
                return f"Veto Message - {idx}"

            case StatuteSerialCategory.ResolutionEnBanc:
                """The `idx` needs to be a specific itemized date."""
                return f"Resolution of the Court En Banc dated {idx}"

            case StatuteSerialCategory.CircularSC:
                return f"SC Circular No. {idx}"

            case StatuteSerialCategory.CircularOCA:
                return f"OCA Circular No. {idx}"

            case StatuteSerialCategory.AdministrativeMatter:
                """Handle special rule with variants: e.g.`rule_am 00-5-03-sc-1`
                and `rule_am 00-5-03-sc-2`
                """
                am = uncamel(self)
                small_idx = idx.lower()
                if "sc" in small_idx:
                    if small_idx.endswith("sc"):
                        return f"{am} No. {small_idx.upper()}"
                    elif sans_var := re.search(r"^.*-sc(?=-\d+)", small_idx):
                        return f"{am} No. {sans_var.group().upper()}"
                return f"{am} No. {small_idx.upper()}"

            case StatuteSerialCategory.BatasPambansa:
                if idx.isdigit():
                    return (  # there are no -A -B suffixes in BPs
                        f"{uncamel(self)} Blg. {idx}"
                    )

            case _:
                # no need to uppercase pure digits
                target_digit = idx if idx.isdigit() else idx.upper()
                return f"{uncamel(self)} No. {target_digit}"

    def searchable(self, num: str) -> list[str]:
        """Given the value `<v>` of a category (lowercased, as saved in the database),
        use `StatuteSerialCategory(<v>)`. This will get the proper category. Use the
        category alongside the passed `num`.

        Examples:
            >>> civ = StatuteSerialCategory('ra')
            >>> civ.searchable('386')
            ['ra 386', 'rep act no. 386', 'r.a. no. 386', 'r.a. 386']
            >>> civ = StatuteSerialCategory('rule_am')
            >>> civ.searchable('00-2-03-sc')
            ['am 00-2-03-sc', 'a.m. no. 00-2-03-sc', 'a.m. 00-2-03-sc', 'admin matter no. 00-2-03-sc']
        """  # noqa: E501
        match self:
            case StatuteSerialCategory.RepublicAct:
                return [
                    f"ra {num}",
                    f"rep act no. {num}",
                    f"r.a. no. {num}",
                    f"r.a. {num}",
                ]
            case StatuteSerialCategory.CommonwealthAct:
                return [
                    f"ca {num}",
                    f"commonwealth act no. {num}",
                    f"c.a. no. {num}",
                    f"c.a. {num}",
                ]
            case StatuteSerialCategory.Act:
                return [
                    f"act of congress {num}",
                ]
            case StatuteSerialCategory.BatasPambansa:
                return [
                    f"bp {num}",
                    f"b.p. no. {num}",
                    f"b.p. blg. {num}",
                    f"batas pambansa {num}",
                    f"batas pambansa blg. {num}",
                ]
            case StatuteSerialCategory.ExecutiveOrder:
                return [
                    f"eo {num}",
                    f"e.o. no. {num}",
                    f"exec order {num}",
                    f"exec. order no. {num}",
                ]
            case StatuteSerialCategory.PresidentialDecree:
                return [
                    f"pd {num}",
                    f"p.d. no. {num}",
                    f"pres decree {num}",
                    f"pres. dec. {num}",
                    f"pres. decree {num}",
                ]
            case StatuteSerialCategory.LetterOfInstruction:
                return [
                    f"loi {num}",
                    f"l.o.i. {num}",
                    f"l.o.i. no. {num}",
                ]
            case StatuteSerialCategory.Spain:
                return [
                    f"spanish {num}",
                    f"old {num}",
                ]
            case StatuteSerialCategory.RulesOfCourt:
                return [
                    f"{num} roc",
                ]
            case StatuteSerialCategory.Constitution:
                return [
                    f"{num} const",
                ]
            case StatuteSerialCategory.AdministrativeMatter:
                return [
                    f"am {num}",
                    f"a.m. no. {num}",
                    f"a.m. {num}",
                    f"admin matter no. {num}",
                ]
            case StatuteSerialCategory.BarMatter:
                return [
                    f"bm {num}",
                    f"b.m. no. {num}",
                    f"b.m. {num}",
                    f"bar matter no. {num}",
                ]
            case StatuteSerialCategory.CircularOCA:
                return [
                    f"oca {num}",
                    f"oca ipi {num}",
                    f"oca ipi no. {num}",
                ]
            case StatuteSerialCategory.CircularSC:
                return [
                    f"sc cir {num}",
                    f"sc cir. no. {num}",
                    f"sc cir. no. {num}",
                ]
            case _:
                return [f"{self.value} {num}"]

    def cite(self, num: str) -> str | None:
        """Given the value `<v>` of a category (lowercased, as saved in the database),
        use `StatuteSerialCategory(<v>)`. This will get the proper category. Use the
        category alongside the passed `num`.

        Examples:
            >>> civ = StatuteSerialCategory('ra')
            >>> civ.cite('386')
            'R.A. No. 386'
            >>> spain = StatuteSerialCategory('spain')
            >>> spain.cite('penal')
            'Spanish Penal Code'
            >>> roc = StatuteSerialCategory('roc')
            >>> roc.cite('1964')
            '1964 Rules of Court'

        Args:
            num (str): The serialized instance of the category

        Returns:
            str | None: A representation of the category for use in citations.
        """
        match self:
            case StatuteSerialCategory.Spain:
                if num == "civil":
                    return "Spanish Civil Code"
                elif num == "penal":
                    return "Spanish Penal Code"
                elif num == "commerce":
                    return "Code of Commerce"
                return None
            case StatuteSerialCategory.Act:
                return f"Act No. {num.upper()}"
            case StatuteSerialCategory.BatasPambansa:
                return f"B.P. Blg. {num.upper()}"
            case StatuteSerialCategory.VetoMessage:
                return f"Veto Message - R.A. No. {num.upper()}"
            case StatuteSerialCategory.Constitution:
                return f"{num} Constitution"
            case StatuteSerialCategory.RulesOfCourt:
                return f"{num} Rules of Court"
            case StatuteSerialCategory.AdministrativeMatter:
                return f"A.M. No. {num.upper()}"
            case StatuteSerialCategory.BarMatter:
                return f"B.M. No. {num.upper()}"
            case StatuteSerialCategory.ResolutionEnBanc:
                return f"Resolution of the Court En Banc dated {num}"
            case StatuteSerialCategory.CircularOCA:
                return f"OCA Circular No. {num.upper()}"
            case StatuteSerialCategory.CircularSC:
                return f"SC Circular No. {num.upper()}"
            case _:
                ...
                base = ".".join([i for i in self.value]).upper()
                return f"{base}. No. {num.upper()}"


class StatuteTitle(NamedTuple):
    """Will be used to populate the database; assumes a fixed `statute_id` from
    a downstream source that can be correlated to the differen title variants."""

    category: StatuteTitleCategory
    text: str

    @classmethod
    def generate(
        cls,
        official: str | None = None,
        serial: str | None = None,
        short: str | list[str] | None = None,
        aliases: list[str] | None = None,
        searchables: list[str] | None = None,
    ):
        if official:
            yield cls(category=StatuteTitleCategory.Official, text=official)

        if serial:
            yield cls(category=StatuteTitleCategory.Serial, text=serial)

        if aliases:
            for title in aliases:
                if title and title != "":
                    yield cls(category=StatuteTitleCategory.Alias, text=title)

        if searchables:
            for title in searchables:
                if title and title != "":
                    yield cls(category=StatuteTitleCategory.Searchable, text=title)

        if short:
            if isinstance(short, list):
                for bit in short:
                    yield cls(category=StatuteTitleCategory.Short, text=bit)
            elif isinstance(short, str):
                yield cls(category=StatuteTitleCategory.Short, text=short)

    @classmethod
    def set_title_table_name(cls) -> str:
        return "statute_titles"

    @classmethod
    def create_titles_table(
        cls, db: Database, fk: str = "statute_id", fk_tbl: str = "statutes"
    ) -> Table:
        tbl_name = cls.set_title_table_name()
        db[tbl_name].create(  # type: ignore
            columns={"id": str, fk: str, "cat": str, "text": str},
            pk="id",
            foreign_keys=[(fk, fk_tbl, "id")],
            not_null={"cat", "text"},
            if_not_exists=True,
        )

        for idx in (
            {fk, "cat"},  # e.g. statute_id and cat=serial to detect serial title
            {fk},
            {"cat", "id"},
            {"cat"},
        ):
            add_idx(db[tbl_name], idx)

        return check_table(db[tbl_name])

    @classmethod
    def make_title_rows(
        cls, statute_id: str, titles: Iterable[Self]
    ) -> Iterable[dict[str, str]]:
        """Create title rows having uniform columns and a predefined id."""
        for counter, title in enumerate(titles, start=1):
            text = title.text.strip(". ")
            yield {
                "id": f"{statute_id}-{counter}",
                "statute_id": statute_id,
                "cat": title.category.name.lower(),
                "text": text,
            }

    @classmethod
    def add_title_rows(cls, db: Database, title_variants: Iterable[dict[str, str]]):
        """Sourced from [make_title_rows()][prelawsql.statutes.StatuteTitle.make_title_rows]."""  # noqa: E501
        tbl_name = cls.set_title_table_name()
        try:
            db[tbl_name].insert_all(records=title_variants, ignore=True)  # type: ignore
        except Exception as e:
            raise ValueError(f"Bad {tbl_name}; {e=}")


class BaseTreePath(NamedTuple):
    """An interim structure that contains common utilities to unpack a
    given tree-based path from a corpus- repository containing
    *.yml files.

    Assumes strict path routing structure: `cat` / `num` / `date` / `variant`.yml,
    e.g. `ra/386/1946-06-18/1.yml` where each file contains the following metadata, the
    mandatory ones being "title" and "units". See example:

    ```yaml
    title: An Act to Ordain and Institute the Civil Code of the Philippines
    units:
    - item: Container 1
        caption: Preliminary Title
        units:
        - item: Chapter 1
            caption: Effect and Application of Laws
            units:
            - item: Article 1
                content: >-
                This Act shall be known as the "Civil Code of the Philippines."
                (n)
            - item: Article 2
                content: >-
                Laws shall take effect after fifteen days following the
                completion of their publication either in the Official
                Gazette or in a newspaper of general circulation in the
                Philippines, unless it is otherwise provided. (1a)
    ```
    """  # noqa: E501

    category: StatuteSerialCategory
    num: str
    date: datetime.date
    slug: str

    @property
    def serial_title(self) -> str:
        serial = self.category.serialize(self.num)
        if not serial:
            raise ValueError(f"Unserialized {self.num}= from {self.category=}")
        return serial

    @property
    def searchable_serial_titles(self) -> list[str]:
        searchables = self.category.searchable(self.num)
        if not searchables:
            raise ValueError(f"No searchables of {self.num}= from {self.category=}")
        return searchables

    @classmethod
    def load(cls, path: Path) -> dict:
        """Convert flat file text into nested JSON object"""
        content = path.read_bytes()
        result = yaml.safe_load(content)
        if not isinstance(result, dict):
            raise ValueError(
                f"JSON conversion of {path=} must result in an initial dict."
            )

        title = result.get("title")
        if not title:
            raise KeyError(f"No title in {path=}")

        units = result.get("units")
        if not units:
            raise KeyError(f"No units in {path=}")

        return result

    @classmethod
    def unpack(cls, path: Path):
        """Convert flat yml file into interim TreePath instance."""
        cat, num, date, slug = path.parts[-4:]
        category = StatuteSerialCategory(cat)
        if not category:
            raise ValueError(f"No category from {cat=}")
        return cls(
            category=category,
            num=num,
            date=datetime.date.fromisoformat(date),
            slug=slug.removesuffix(".yml"),
        )

    @classmethod
    def create_path_table(
        cls,
        base_path: Path = STAT_DIR,
        base_pattern: str = TREE_GLOB,
        db_name: str = STAT_TMP,
    ) -> Table:
        """Quickly lists statutes found in directory without populating content."""
        db = Database(db_name, use_counts_table=True)
        if not db["statutes"].exists():
            rows = []
            items = list(base_path.glob(base_pattern))
            for item in track(items, description="create rows from statute paths"):
                cat, num, date, variant = item.parts[-4:]
                v = variant.split(".")[0]
                rows.append(
                    {
                        "id": "-".join([cat, num, date, v]),
                        "cat": cat,
                        "num": num,
                        "date": date,
                        "variant": v,
                        "size": item.stat().st_size,
                    }
                )

            logging.info("Adding statute paths to interim table.")
            db["statutes"].insert_all(rows, pk="id", ignore=True)  # type: ignore

            logging.info("Adding indexes to interim table.")
            for idx in (
                {"size"},
                {"date"},
                {"cat", "num"},
                {"cat", "num", "date"},
                {"cat", "num", "date", "variant"},
            ):
                add_idx(db["statutes"], idx)
        return check_table(db["statutes"])


@dataclass(frozen=True)
class Rule:
    """A `Rule` is detected if it matches either a named pattern or a serial pattern.
    Each rule maps to a category `cat` and number `num`.
    """  # noqa: E501

    cat: StatuteSerialCategory
    num: str

    def __repr__(self) -> str:
        return f"<Rule: {self.cat.value} {self.num}>"

    def __str__(self) -> str:
        return self.cat.serialize(self.num) or f"{self.cat.value=} {self.num=}"

    @property
    def slug(self) -> str:
        return slugify(
            " ".join([self.cat.value, self.num.lower()]), separator="_", lowercase=True
        )

    @property
    def serial_title(self):
        return StatuteSerialCategory(self.cat.value).serialize(self.num)

    @cached_property
    def date(self) -> datetime.date | None:
        """Get the earliest date corresponding to the instance."""
        db = Database(DB_FILE)
        if db["statutes"].exists():
            return self.extract_rule_date(db)
        else:
            mini = BaseTreePath.create_path_table()
            return self.extract_rule_date(mini.db)

    def extract_rule_date(
        self,
        db: Database,
        table_name: str = "statutes",
    ) -> datetime.date | None:
        """Whether using the main database or the mini variant, the same query can
        be applied in extracting the earliest date in a table of rules."""
        results = db.execute_returning_dicts(
            f"""--sql
            select min(s.date) min_date
            from {table_name} s
            where s.cat = :cat and s.num = :num
            group by s.cat, s.num;
            """,
            params={"cat": self.cat.value.lower(), "num": self.num.lower()},
        )
        if results:
            return datetime.date.fromisoformat(results[0]["min_date"])
        return None
