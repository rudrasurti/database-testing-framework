# Database Testing Framework

![Database Tests](https://github.com/rudrasurti/database-testing-framework/actions/workflows/db-tests.yml/badge.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%20%7C%2016%20%7C%2017-336791)

Most bugs that reach production are data bugs: a negative balance, a duplicate customer, a transfer that half-happened. This framework tests the **database itself** with Python, pytest and PostgreSQL: schema, constraints, business rules in SQL, data quality and ETL.

## What's covered (27 tests)

| Suite | What it proves |
|---|---|
| `test_schema.py` | Tables exist, money is `NUMERIC(14,2)` not float, foreign keys exist and are indexed |
| `test_constraints.py` | The database itself rejects 9 kinds of bad data: negative balance, duplicate or invalid email, blank name, orphan account, zero amount, self-transfer, unknown risk level, deleting a customer who still has accounts |
| `test_business_rules.py` | The `transfer()` function moves money and logs it, total money never changes, and every failed transfer (not enough money, frozen account, negative amount) leaves balances and history untouched |
| `test_data_quality.py` | No duplicate emails (case-insensitive), no orphan accounts, valid country codes, no future dates |
| `test_etl.py` | Staging-to-target load skips duplicates and invalid rows, reconciles with staging, and is safe to run twice |

The sample schema is a small banking model (customers, accounts, transactions) in [`db/schema.sql`](db/schema.sql).

## How tests stay independent

The schema is built once per run. Each test runs inside a transaction that is **rolled back** at the end, so tests can insert, update and delete freely without affecting each other, and they run in any order.

## Run locally

```bash
docker run -d --name pg -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16
pip install -r requirements.txt
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
python -m pytest -q tests
```

## CI

GitHub Actions starts a PostgreSQL service container and runs the suite on **PostgreSQL 15, 16 and 17**. [QA Report Bot](https://github.com/rudrasurti/qa-report-bot) posts the result summary on every run and pull request.

## Testing ideas you can reuse

- Test constraints in the database, not only in the app: the database is the last line of defence
- Check that money uses exact numeric types
- For every failure path, assert that **nothing changed**, not only that an error was raised
- Reconcile counts and sums between source and target after every ETL step
- Run ETL twice: a safe load gives the same result

---

**Rudra Surti** · Senior SDET · [Website](https://rudrasurti.github.io) · [LinkedIn](https://www.linkedin.com/in/rudra-surti/)
