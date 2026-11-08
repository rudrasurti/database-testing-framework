from conftest import scalar


def test_no_duplicate_emails_ignoring_case(db):
    assert scalar(db, "SELECT count(*) - count(DISTINCT lower(email)) FROM customers") == 0


def test_every_account_belongs_to_a_customer(db):
    assert scalar(db, "SELECT count(*) FROM accounts a LEFT JOIN customers c USING (customer_id) "
                      "WHERE c.customer_id IS NULL") == 0


def test_country_codes_are_upper_case_iso_style(db):
    assert scalar(db, "SELECT count(*) FROM customers WHERE country !~ '^[A-Z]{2}$'") == 0


def test_no_future_created_dates(db):
    assert scalar(db, "SELECT count(*) FROM customers WHERE created_at > now()") == 0
