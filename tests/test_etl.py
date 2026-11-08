import pathlib

from conftest import scalar

ETL = (pathlib.Path(__file__).resolve().parents[1] / "db" / "etl.sql").read_text()


def test_etl_loads_only_clean_unique_rows(db):
    before = scalar(db, "SELECT count(*) FROM customers")
    db.execute(ETL)
    # staging has 4 rows: 1 duplicate and 1 invalid -> 2 new customers
    assert scalar(db, "SELECT count(*) FROM customers") == before + 2


def test_etl_reconciles_with_staging(db):
    db.execute(ETL)
    expected = scalar(db, "SELECT count(DISTINCT lower(email)) FROM staging_customers "
                          "WHERE length(trim(full_name)) > 0 AND email ~* '^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$'")
    loaded = scalar(db, "SELECT count(*) FROM customers c JOIN staging_customers s ON lower(s.email) = c.email")
    assert scalar(db, "SELECT count(DISTINCT c.email) FROM customers c JOIN staging_customers s ON lower(s.email) = c.email") == expected
    assert loaded >= expected


def test_etl_is_idempotent(db):
    db.execute(ETL)
    once = scalar(db, "SELECT count(*) FROM customers")
    db.execute(ETL)
    assert scalar(db, "SELECT count(*) FROM customers") == once
