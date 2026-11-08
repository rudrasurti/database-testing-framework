-- Load clean, de-duplicated rows from staging into customers.
SET search_path TO bank;
INSERT INTO customers (full_name, email, country)
SELECT DISTINCT ON (lower(email)) trim(full_name), lower(email), upper(country)
FROM staging_customers
WHERE length(trim(full_name)) > 0
  AND email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'
ORDER BY lower(email)
ON CONFLICT (email) DO NOTHING;
