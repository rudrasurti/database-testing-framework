from conftest import scalar


def test_expected_tables_exist(db):
    rows = db.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'bank' AND table_type = 'BASE TABLE'"
    ).fetchall()
    assert {r[0] for r in rows} >= {"customers", "accounts", "transactions", "staging_customers"}


def test_balance_column_is_exact_numeric(db):
    dtype, scale = db.execute(
        "SELECT data_type, numeric_scale FROM information_schema.columns "
        "WHERE table_schema = 'bank' AND table_name = 'accounts' AND column_name = 'balance'"
    ).fetchone()
    assert (dtype, scale) == ("numeric", 2)  # money must never be a float


def test_foreign_keys_are_defined(db):
    fks = scalar(db, "SELECT count(*) FROM information_schema.table_constraints "
                     "WHERE table_schema = 'bank' AND constraint_type = 'FOREIGN KEY'")
    assert fks == 3


def test_foreign_key_columns_are_indexed(db):
    idx = {r[0] for r in db.execute("SELECT indexname FROM pg_indexes WHERE schemaname = 'bank'").fetchall()}
    assert {"idx_accounts_customer", "idx_txn_from", "idx_txn_to"} <= idx
