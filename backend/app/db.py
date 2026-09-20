"""Builds and opens the SQLite database for the GiveCampus dataset.

Uses the dataset's own `schema.sql` and CSVs. The database file is
generated (gitignored) and rebuilt automatically if missing or stale.
"""

import csv
import sqlite3
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = REPO_ROOT / "20260919_GiveCampus_MIT_Hackathon"
DATA_DIR = DATASET_DIR / "data"
SCHEMA_PATH = DATASET_DIR / "schema.sql"
DB_PATH = DATASET_DIR / "givecampus_hackmit.sqlite"

TABLES = [
    "schools",
    "staff",
    "constituents",
    "affiliations",
    "degrees",
    "activities",
    "funds",
    "campaigns",
    "opportunities",
    "gifts",
    "gift_allocations",
    "interactions",
    "events",
    "event_attendance",
    "career_history",
]


def _sqlite_value(value):
    if value == "":
        return None
    if value == "true":
        return 1
    if value == "false":
        return 0
    return value


def build_database(db_path: Path = DB_PATH, force: bool = False) -> Path:
    """Load the CSV package into a fresh SQLite database at db_path."""
    if db_path.exists():
        if not force:
            return db_path
        db_path.unlink()

    connection = sqlite3.connect(db_path)
    try:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        for table in TABLES:
            csv_path = DATA_DIR / f"{table}.csv"
            with csv_path.open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                columns = reader.fieldnames
                placeholders = ", ".join("?" for _ in columns)
                quoted_columns = ", ".join(f'"{column}"' for column in columns)
                rows = ([_sqlite_value(row[column]) for column in columns] for row in reader)
                connection.executemany(
                    f'INSERT INTO "{table}" ({quoted_columns}) VALUES ({placeholders})',
                    rows,
                )
        foreign_key_errors = connection.execute("PRAGMA foreign_key_check").fetchall()
        if foreign_key_errors:
            raise RuntimeError(f"Foreign-key validation failed: {foreign_key_errors[:5]}")
        connection.commit()
    except Exception:
        connection.close()
        db_path.unlink(missing_ok=True)
        raise
    finally:
        connection.close()

    return db_path


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    build_database(db_path)
    return sqlite3.connect(db_path)


def load_table(name: str, db_path: Path = DB_PATH) -> pd.DataFrame:
    connection = get_connection(db_path)
    try:
        return pd.read_sql_query(f'SELECT * FROM "{name}"', connection)
    finally:
        connection.close()
