SET search_path TO bank;
INSERT INTO customers (full_name, email, country, risk_level) VALUES
  ('Asha Patel',  'asha@example.com',  'IN', 'low'),
  ('Dev Shah',    'dev@example.com',   'IN', 'medium'),
  ('Maria Lopez', 'maria@example.com', 'ES', 'high');
INSERT INTO accounts (customer_id, balance, status) VALUES
  (1, 5000.00, 'active'),
  (2, 1200.00, 'active'),
  (3,  800.00, 'frozen');
INSERT INTO staging_customers (full_name, email, country) VALUES
  ('Ravi Kumar',  'ravi@example.com',  'IN'),
  ('Neha Joshi',  'neha@example.com',  'IN'),
  ('Ravi Kumar',  'ravi@example.com',  'IN'),
  ('',            'bad-email',         'IN');
