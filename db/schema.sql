-- Banking sample schema used to demonstrate database testing.
DROP SCHEMA IF EXISTS bank CASCADE;
CREATE SCHEMA bank;
SET search_path TO bank;

CREATE TABLE customers (
    customer_id  SERIAL PRIMARY KEY,
    full_name    TEXT        NOT NULL CHECK (length(trim(full_name)) > 0),
    email        TEXT        NOT NULL UNIQUE CHECK (email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'),
    country      CHAR(2)     NOT NULL,
    risk_level   TEXT        NOT NULL DEFAULT 'low' CHECK (risk_level IN ('low', 'medium', 'high')),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE accounts (
    account_id   SERIAL PRIMARY KEY,
    customer_id  INT           NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
    currency     CHAR(3)       NOT NULL DEFAULT 'INR',
    balance      NUMERIC(14,2) NOT NULL DEFAULT 0 CHECK (balance >= 0),
    status       TEXT          NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'frozen', 'closed'))
);
CREATE INDEX idx_accounts_customer ON accounts(customer_id);

CREATE TABLE transactions (
    txn_id       BIGSERIAL PRIMARY KEY,
    from_account INT           REFERENCES accounts(account_id),
    to_account   INT           REFERENCES accounts(account_id),
    amount       NUMERIC(14,2) NOT NULL CHECK (amount > 0),
    created_at   TIMESTAMPTZ   NOT NULL DEFAULT now(),
    CHECK (from_account IS DISTINCT FROM to_account)
);
CREATE INDEX idx_txn_from ON transactions(from_account);
CREATE INDEX idx_txn_to ON transactions(to_account);

-- Business rule: transfers are atomic, need an active source with enough money.
CREATE FUNCTION transfer(p_from INT, p_to INT, p_amount NUMERIC) RETURNS BIGINT
LANGUAGE plpgsql AS $$
DECLARE
    v_txn BIGINT;
BEGIN
    IF p_amount <= 0 THEN
        RAISE EXCEPTION 'Amount must be positive';
    END IF;
    PERFORM 1 FROM accounts WHERE account_id = p_from AND status = 'active' FOR UPDATE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Source account % is not active', p_from;
    END IF;
    UPDATE accounts SET balance = balance - p_amount WHERE account_id = p_from;
    UPDATE accounts SET balance = balance + p_amount WHERE account_id = p_to AND status = 'active';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Target account % is not active', p_to;
    END IF;
    INSERT INTO transactions(from_account, to_account, amount)
    VALUES (p_from, p_to, p_amount) RETURNING txn_id INTO v_txn;
    RETURN v_txn;
END $$;

-- Reporting view: money in and out per account.
CREATE VIEW account_activity AS
SELECT a.account_id,
       COALESCE((SELECT sum(amount) FROM transactions t WHERE t.to_account = a.account_id), 0)   AS total_in,
       COALESCE((SELECT sum(amount) FROM transactions t WHERE t.from_account = a.account_id), 0) AS total_out
FROM accounts a;

-- ETL: raw data lands in staging, then loads into customers.
CREATE TABLE staging_customers (
    full_name TEXT,
    email     TEXT,
    country   TEXT
);
