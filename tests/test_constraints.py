import psycopg
import pytest


@pytest.mark.parametrize("sql, error", [
    ("UPDATE accounts SET balance = -1 WHERE account_id = 1", psycopg.errors.CheckViolation),
    ("INSERT INTO customers(full_name, email, country) VALUES ('X', 'asha@example.com', 'IN')", psycopg.errors.UniqueViolation),
    ("INSERT INTO customers(full_name, email, country) VALUES ('X', 'not-an-email', 'IN')", psycopg.errors.CheckViolation),
    ("INSERT INTO customers(full_name, email, country) VALUES ('  ', 'blank@example.com', 'IN')", psycopg.errors.CheckViolation),
    ("INSERT INTO accounts(customer_id, balance) VALUES (999, 10)", psycopg.errors.ForeignKeyViolation),
    ("INSERT INTO transactions(from_account, to_account, amount) VALUES (1, 2, 0)", psycopg.errors.CheckViolation),
    ("INSERT INTO transactions(from_account, to_account, amount) VALUES (1, 1, 10)", psycopg.errors.CheckViolation),
    ("UPDATE customers SET risk_level = 'extreme' WHERE customer_id = 1", psycopg.errors.CheckViolation),
    ("DELETE FROM customers WHERE customer_id = 1", psycopg.errors.ForeignKeyViolation),
], ids=["negative-balance", "duplicate-email", "bad-email", "blank-name", "orphan-account",
        "zero-amount", "self-transfer", "unknown-risk-level", "delete-customer-with-account"])
def test_database_rejects_bad_data(db, sql, error):
    with pytest.raises(error):
        db.execute(sql)
