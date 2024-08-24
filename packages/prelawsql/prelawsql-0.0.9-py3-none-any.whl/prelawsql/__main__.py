from pathlib import Path

import click
from sqlite_utils import Database

from .authors import Author
from .citations import CitationPath, CitationTag
from .config import CASE_TMP, DATA_DIR, DB_FILE, STAT_DIR, STAT_TMP
from .listing import Listing, Source
from .statutes import BaseTreePath


@click.group()
def cli():
    """Extensible wrapper of commands."""
    pass


@cli.command()
@click.option("--db-name", type=str, default=DB_FILE, help="Filename of db")
def source(db_name: str) -> Database:
    """Prepare existing statute db path by first deleting it creating
    a new one in WAL-mode.

    Args:
        db_name (str): e.g. "x.db", or "data/main.db"

    Returns:
        Database: The configured database object.
    """
    Path("data").mkdir(exist_ok=True)

    if not db_name.endswith((".sqlite", ".db")):
        raise ValueError("Expects either an *.sqlite, *.db suffix")

    _db_file = Path(db_name)
    _db_file.unlink(missing_ok=True)

    db = Database(filename_or_conn=_db_file, use_counts_table=True)
    db.enable_wal()
    return db


@cli.command()
@click.option(
    "--folder",
    type=Path,
    default=STAT_DIR,
    required=True,
    help="Location of raw files to create database",
)
@click.option(
    "--target",
    type=str,
    default=STAT_TMP,
    required=True,
    help="Location of raw files to create database",
)
def interim_statute_db(folder: Path, target: str):
    """Fast-creation of interim statute files db based on `STAT_DIR`

    Args:
        folder (Path): Origin of statute files
        target (Path): Where to save db.
            Defaults to STAT_TMP.
    """
    Path(DATA_DIR).mkdir(exist_ok=True)
    Path(target).unlink(missing_ok=True)
    BaseTreePath.create_path_table(base_path=folder, db_name=target)


@cli.command()
@click.option(
    "--tablename",
    required=True,
    type=str,
    help="Name of table to host decisions",
)
def interim_decision_db(tablename: str) -> Database:
    """Temporary table to host fetched decision rows

    ```sh
    pre interim-decision-db --tablename src
    ```

    Create 2 tables:

    1. populated `justices`,
    2. empty `src`.
    """
    Path(DATA_DIR).mkdir(exist_ok=True)
    Path(CASE_TMP).unlink(missing_ok=True)
    db = Database(filename_or_conn=CASE_TMP, use_counts_table=True)
    db.enable_wal()
    Author.add_justices(db)
    CitationPath.create_interim_decision_table(db, tablename)
    db.index_foreign_keys()
    return db


@cli.command()
@click.option(
    "--start",
    required=True,
    type=int,
    help="Start year to include.",
)
@click.option(
    "--end",
    type=int,
    required=True,
    help="End year, terminal part of the date range, will not be included",
)
def list_decision_urls(start: int, end: int):
    """Populate `CASE_TMP` with decisions representing urls and assignable paths.

    ```sh
    pre list-decision-urls --start 1996 --end 2024
    ```

    This enables searching the library for decisions within the years indicated.

    The collection of entries in the database serves as a directory.

    This allows us to add markdown files to the local directory (skipping pre-existing files), e.g.: `/corpus-decisions`
    that is represented by `CASE_DIR`.

    Args:
        start (int): When to start.
        end (int): Excluded from the years list.
    """  # noqa: E501
    db = Database(filename_or_conn=CASE_TMP, use_counts_table=True)
    for year in range(start, end):  # takes about 3 minutes for all decisions
        for month in Listing:
            for tag in Source.Decision.fetch_tags(year=year, month=month):
                CitationTag.to_db(tag=tag, db=db)


if __name__ == "__main__":
    cli()  # search @cli.command
