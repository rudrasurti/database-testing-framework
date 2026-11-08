import psycopg
import pytest

from conftest import scalar


def balances(db):
    return dict(db.execute("SELECT account_id, balance FROM accounts ORDER BY account_id").fetchall())


def test_transfer_moves_money_and_logs_it(db):
    before = balances(db)
    txn = scalar(db, "SELECT transfer(1, 2, 250.00)")
    after = balances(db)
    assert after[1] == before[1] - 250 and after[2] == before[2] + 250
    assert scalar(db, "SELECT amount FROM transactions WHERE txn_id = %s", txn) == 250


def test_transfer_keeps_total_money_the_same(db):
    total = scalar(db, "SELECT sum(balance) FROM accounts")
    db.execute("SELECT transfer(1, 2, 100)")
    db.execute("SELECT transfer(2, 1, 40)")
    assert scalar(db, "SELECT sum(balance) FROM accounts") == total


@pytest.mark.parametrize("args, message", [
    ((2, 1, 99999), "check"),               # not enough money -> balance check
    ((3, 1, 10), "not active"),             # frozen source
    ((1, 3, 10), "not active"),             # frozen target
    ((1, 2, -5), "positive"),
])
def test_failed_transfer_changes_nothing(db, args, message):
    before = balances(db)
    txns = scalar(db, "SELECT count(*) FROM transactions")
    with pytest.raises(psycopg.Error) as err:
        with db.transaction():
            db.execute("SELECT transfer(%s, %s, %s)", args)
    assert message in str(err.value).lower()
    assert balances(db) == before
    assert scalar(db, "SELECT count(*) FROM transactions") == txns


def test_activity_view_matches_transactions(db):
    db.execute("SELECT transfer(1, 2, 300)")
    db.execute("SELECT transfer(2, 1, 50)")
    total_in, total_out = db.execute("SELECT total_in, total_out FROM account_activity WHERE account_id = 1").fetchone()
    assert (total_in, total_out) == (50, 300)
