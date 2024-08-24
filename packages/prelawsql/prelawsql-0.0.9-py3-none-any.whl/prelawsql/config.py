import logging
from collections.abc import Iterator
from pathlib import Path
from urllib.parse import ParseResult

from environs import Env
from rich.progress import track
from sqlite_utils.db import Database, Table

from .db import add_idx, check_table

env = Env()
env.read_env()

### MAIN

DATA_DIR: str = env("DATA_DIR", "data")
""" Where to store main / temp databases. """

DB_FILE: str = env("DB_FILE", "data/main.db")
""" Where to store the main database """

SOURCE: ParseResult = env.url("SOURCE", "https://lawsql.com")
""" Where to source the tree files"""

### TREES


TREE_GLOB: str = env("TREE_GLOB", "**/*/*.yml")
""" Pattern to use to detect both codification and statute *.yml files
within `CODE_DIR` and `STAT_DIR`, respectively"""

CODE_DIR: Path = env.path("CODE_DIR", "../corpus-codifications")
""" Where to store and source codification *.yml files locally """

CODE_FILES: Iterator[Path] = CODE_DIR.glob(TREE_GLOB)
"""Combines `CODE_DIR` with `TREE_GLOB` to generate all codification files."""

STAT_DIR: Path = env.path("STAT_DIR", "../corpus-statutes")
""" Where to store and source statute *.yml files locally """

STAT_TMP: str = f"{DATA_DIR}/stats.db"
""" Interim statutes database for fast querying."""

STAT_FILES: Iterator[Path] = STAT_DIR.glob(TREE_GLOB)
"""Combines `STAT_DIR` with `TREE_GLOB` to generate all statute files."""

### DECISIONS

CASE_DIR: Path = env.path("CASE_DIR", "../corpus-decisions")
""" Where to store and source decision / opinion *.md files locally """

CASE_GLOB: str = env("CASE_GLOB", "*/*/*/*.md")
""" Pattern to use to detect the ponencia *.md file within `CASE_DIR`."""

CASE_TMP: str = f"{DATA_DIR}/cases.db"
""" Interim decisions database for fast querying."""

CASE_FILES: Iterator[Path] = CASE_DIR.glob(CASE_GLOB)
""" Combines `CASE_DIR` with `CASE_GLOB` to generate all statute files."""
