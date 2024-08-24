import datetime
import logging
import re
from pathlib import Path
from typing import Any, NamedTuple, Self

import frontmatter
import yaml
from corpus_judge import JUSTICE_FILE, CandidateJustice
from rich.progress import Progress
from sqlite_utils.db import Database, Table

from .clean import is_text_possible
from .db import add_idx, check_table
from .dumper import SafeDumper

upper_curiam = r"(\bCURIAM\b)"
title_curiam = r"(\bCuriam\b)"
curiams = [upper_curiam, title_curiam]
CURIAM_PATTERN = re.compile(rf"({'|'.join(curiams)})")

judge = r"(\,?\s*\bJ\b)"
chief = r"(\,?\s*\bC\.?\s*J\b)"
saj = r"(\,?\s*\bSAJ\.?)"
writer_block = [judge, chief, saj] + curiams
WRITER_PATTERN = re.compile(rf"({'|'.join(writer_block)})")


class Author(NamedTuple):
    """Refers to a `Justice` who may pen an opinion.

    Closely related to the CitationPath since this determines the filename to use.

    Anonymous _per curiam_ opinions are marked as such.
    """

    is_main: bool = True
    curiam: bool = False
    value: str | None = None

    @property
    def justice_digit(self) -> int | None:
        if self.value and self.value.isdigit():
            return int(self.value)
        return None

    @property
    def is_anonymous(self):
        if self.value and self.value.startswith("a"):
            return True
        return False

    @classmethod
    def add_justices(cls, db: Database) -> Table:
        with Progress() as progress:
            task = progress.add_task("justices", total=4)
            while not progress.finished:
                origin = JUSTICE_FILE.read_bytes()
                progress.update(task, advance=1)

                records = yaml.safe_load(origin)
                progress.update(task, advance=1)

                tbl = cls.create_justice_table(db)
                progress.update(task, advance=1)

                tbl.insert_all(records, ignore=True)  # type: ignore
                progress.update(task, advance=1)

            return tbl

    @classmethod
    def create_justice_table(cls, db: Database) -> Table:
        db["justices"].create(  # type: ignore
            columns={
                "id": int,
                "gender": str,
                "first_name": str,
                "last_name": str,
                "suffix": str,
                "full_name": str,
                "alias": str,
                "birth_date": datetime.date,
                "start_term": datetime.date,
                "end_term": datetime.date,
                "chief_date": datetime.date,
                "retire_date": datetime.date,
                "inactive_date": datetime.date,
            },
            pk="id",
            not_null={"last_name", "full_name", "start_term"},
            if_not_exists=True,
        )

        for idx in (
            {"start_term", "end_term", "retire_date", "chief_date", "inactive_date"},
            {"start_term", "end_term", "retire_date", "inactive_date"},
            {"start_term", "end_term", "retire_date"},
            {"end_term", "retire_date", "inactive_date"},
            {"end_term", "retire_date"},
            {"start_term", "end_term"},
            {"birth_date"},
            {"start_term"},
            {"end_term"},
            {"chief_date"},
            {"retire_date"},
            {"inactive_date"},
            {"end_term"},
        ):
            add_idx(db["justices"], idx)  # type: ignore

        return check_table(db["justices"])

    @classmethod
    def set_file(
        cls,
        decision_path: str | None,
        decision_date: Any,
        detected_writer: Any,
        opinion_numbering: int,
        db: Database,
        tablename: str = "justices",
    ) -> Path:
        """Create a target file for the opinion based on the opinion writer.

        Args:
            decision_path (str, optional): Each opinion belongs to a parent folder.
            decision_date (Any): Since some names are the same, this helps
                determine which justices should be considered candidates.
            detected_writer (Any): This will be processed by `CandidateJustice` to
                determine the integer representing the `Justice`, if available.
            opinion_numbering (int): The first opinion passed will always be considered
                the ponecia.
            db (Database): Where to source the table for `CandidateJustice` to make a
                selection.
            tablename (str, optional): Which table represents the justice table.
                Defaults to "justices".
        Returns:
            Path: Location of processed opinion writer-based content.
        """
        judge = CandidateJustice(
            db=db, text=detected_writer, date_str=decision_date, tablename=tablename
        )
        ponencia_indicator = "main"
        # the first opinion is the ponencia
        if opinion_numbering == 1:
            if judge.per_curiam:
                return Path(f"{decision_path}/{ponencia_indicator}-pc.md")
            elif judge.id:
                return Path(f"{decision_path}/{ponencia_indicator}-{judge.id}.md")
            return Path(f"{decision_path}/{ponencia_indicator}.md")
        # non-ponencia, separate opinion
        elif judge.id:
            return Path(f"{decision_path}/opinion/{judge.id}.md")
        return Path(f"{decision_path}/opinion/a{opinion_numbering}.md")

    @classmethod
    def to_file(cls, target: Path, text: str, meta: dict[str, Any]):
        """After `cls.to_file()`, insert file to resulting `target` path"""
        if target.exists():
            raise FileExistsError(f"{target=} must not be overriden.")
        target.parent.mkdir(parents=True, exist_ok=True)
        logging.info(f"Creating {target=}.")
        frontmatter.dump(
            post=frontmatter.Post(text, **meta), fd=str(target), Dumper=SafeDumper
        )

    @classmethod
    def from_file(cls, file: Path) -> Self:
        """Requires frontmatter-formatted markdown file where filename is either:

        1. `main.md` - Undetected writer
        2. `main-<digit>.md` - Detected writer
        3. `main-pc.md` - Anonymous writer

        The filename suffix determines the existence of a `justice_id` and the `curiam`
        field.

        It must also be based on a certain path. The path will determine the citation
        row which is calculated from its docket subfields.

        The example file structure using this certain "docket" path:

        ```
        |- `/gr`
            |- `/1234`
                |- `/2023-01-01`
                    |- main-172.md
                |- `/2023-05-05`
                    |- main-172.md
        ```

        If the parent folder of such certain path contains a subdirectory `/opinion`,
        and the markdown files should follow another convention for separate
        opinions:

        1. `<digit>.md` - Identifier of writer
        2. `a-<digit>.md` - Anonymous writer

        The example file structure using the same "docket" path with opinions:

        ```
        |- `/gr`
            |- `/1234`
                |- `/2023-01-01`
                    |- opinion
                        |- 194.md
                        |- 191.md
                    |- main-172.md
                |- `/2023-05-05`
                    |- opinion
                        |- 194.md
                    |- main-172.md
        ```

        Args:
            file (Path): A filename that follows a convention.

        Returns:
            int | str | None: If an integer, implies a justice has been identified; if a string,
        """  # noqa: E501
        if file.suffix != ".md":
            raise Exception(f"{file=}; must be *.md")

        if file.parent.stem == "opinion":
            if file.stem.isdigit():
                return cls(is_main=False, value=file.stem)
            elif not file.stem.startswith("a"):
                raise Exception(f"{file=}; must either be digit or anonymous.")
            return cls(is_main=False, value=file.stem)

        if not file.stem.startswith("main"):
            raise Exception(f"{file=} must either be main, main-1, main-pc")
        elif file.name == "main.md":
            return cls(is_main=True)

        _bits = file.stem.split("-")
        if len(_bits) == 2:
            if _bits[1].isdigit():
                return cls(is_main=True, value=_bits[1])  # ponencia
            elif _bits[1] == "pc":
                return cls(is_main=True, curiam=True)  # per curiam
        raise Exception(f"Improper {file=}, could not determine id based on convention")

    @staticmethod
    def is_curiam(text: str):
        if CURIAM_PATTERN.search(text):
            return True
        return False

    @staticmethod
    def get_writer(raw: str) -> str | None:
        if not is_text_possible(raw):
            return None

        def clean_writer(text: str):
            text = text.removesuffix(", S.A.J.:")
            text = text.removesuffix(", SAJ.:")
            text = text.removesuffix(", J,:")
            text = text.removesuffix(" J.:*")
            text = text.removesuffix("[*]")
            text = text.removesuffix(", J:")
            text = text.removesuffix(", J:")
            text = text.removesuffix(", J.:")
            text = text.removesuffix(", C.J.:")
            text = text.removesuffix(":")
            return text.title()

        return clean_writer(raw) if WRITER_PATTERN.search(raw) else None
