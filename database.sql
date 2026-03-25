
DROP DATABASE IF EXISTS supply_chain;
CREATE DATABASE supply_chain;

-- Connect to database
\c supply_chain


DROP TABLE IF EXISTS purchase_orders;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS inventory;


CREATE TABLE inventory (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    stock INT CHECK (stock >= 0),
    reorder_point INT,
    supplier VARCHAR(100)
);

CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,
    product_id INT,
    date DATE NOT NULL,
    quantity INT CHECK (quantity > 0)
);

CREATE TABLE purchase_orders (
    po_id SERIAL PRIMARY KEY,
    product_id INT,
    quantity INT,
    status VARCHAR(50),
    supplier VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO inventory (product_name, stock, reorder_point, supplier)
VALUES 
('Rice', 100, 30, 'Supplier A'),
('Wheat', 80, 25, 'Supplier B');

INSERT INTO sales (product_id, date, quantity)
VALUES 
(1, '2024-03-01', 10),
(1, '2024-03-02', 12),
(2, '2024-03-01', 8);


INSERT INTO sales (product_id, date, quantity)
SELECT 
    (random()*2+1)::int,
    CURRENT_DATE - (random()*30)::int,
    (random()*20+5)::int
FROM generate_series(1,100);


CREATE INDEX idx_sales_date ON sales(date);




CREATE VIEW daily_sales AS
SELECT date, SUM(quantity) AS total_sales
FROM sales
GROUP BY date
ORDER BY date;

-- Connection Name: local_pg
-- Server/Host: localhost
-- Port: 5432
-- Database: supply_chain
-- Username: aditi
-- Password: (leave empty)