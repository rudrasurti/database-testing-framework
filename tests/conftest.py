import os
import pathlib

import psycopg
import pytest

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
DB_DIR = pathlib.Path(__file__).resolve().parents[1] / "db"


@pytest.fixture(scope="session")
def schema():
    """Build the schema and seed data once per test session."""
    with psycopg.connect(DB_URL, autocommit=True) as conn:
        for name in ("schema.sql", "seed.sql"):
            conn.execute((DB_DIR / name).read_text())
    yield


@pytest.fixture
def db(schema):
    """Each test runs in a transaction that is rolled back, so tests never affect each other."""
    with psycopg.connect(DB_URL) as conn:
        conn.execute("SET search_path TO bank")
        yield conn
        conn.rollback()


def scalar(conn, sql, *params):
    return conn.execute(sql, params).fetchone()[0]
