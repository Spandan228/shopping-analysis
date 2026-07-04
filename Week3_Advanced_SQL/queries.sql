-- SQL Advanced Analytics & Customer Sales Insights (Superstore Dataset)

-- STEP 1: Database Schema Setup

-- Raw staging table (populated from CSV import)
-- Table structure should match the fields of the Sample Superstore CSV.

CREATE TABLE IF NOT EXISTS superstore_raw (
    row_id INTEGER PRIMARY KEY,
    order_id TEXT,
    order_date TEXT,
    ship_date TEXT,
    ship_mode TEXT,
    customer_id TEXT,
    customer_name TEXT,
    segment TEXT,
    country TEXT,
    city TEXT,
    state TEXT,
    postal_code TEXT,
    region TEXT,
    product_id TEXT,
    category TEXT,
    sub_category TEXT,
    product_name TEXT,
    sales REAL,
    quantity INTEGER,
    discount REAL,
    profit REAL
);

-- customers reference table
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    segment TEXT
);

-- products reference table
CREATE TABLE IF NOT EXISTS products (
    product_id TEXT,
    product_name TEXT,
    category TEXT,
    sub_category TEXT,
    PRIMARY KEY (product_id, product_name)
);

-- normalized orders transactional table
CREATE TABLE IF NOT EXISTS orders (
    row_id INTEGER PRIMARY KEY,
    order_id TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    order_date TEXT NOT NULL,
    ship_date TEXT,
    ship_mode TEXT,
    sales REAL NOT NULL,
    quantity INTEGER NOT NULL,
    discount REAL NOT NULL,
    profit REAL NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
);

-- Data Population via SELECT DISTINCT

INSERT INTO customers (customer_id, customer_name, segment)
SELECT DISTINCT customer_id, customer_name, segment
FROM superstore_raw;

INSERT INTO products (product_id, product_name, category, sub_category)
SELECT DISTINCT product_id, product_name, category, sub_category
FROM superstore_raw;

INSERT INTO orders (row_id, order_id, customer_id, product_id, order_date, ship_date, ship_mode, sales, quantity, discount, profit)
SELECT DISTINCT row_id, order_id, customer_id, product_id, order_date, ship_date, ship_mode, sales, quantity, discount, profit
FROM superstore_raw;


-- STEP 2: Analytical Queries

-- 1. Find all orders where sales are greater than the average sales (Subquery)
-- This returns line-item transactions exceeding the average line-item transaction value.
SELECT order_id, sales
FROM orders
WHERE sales > (SELECT AVG(sales) FROM orders)
ORDER BY sales DESC;


-- 2. Find the highest sales order (line-item value) for each customer (Subquery)
SELECT o.customer_id, c.customer_name, o.order_id, o.sales
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.sales = (
    SELECT MAX(sales)
    FROM orders sub
    WHERE sub.customer_id = o.customer_id
)
ORDER BY o.sales DESC;


-- 3. Calculate total sales for each customer (CTE)
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_name, ROUND(cs.total_sales, 2) AS total_sales
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id
ORDER BY total_sales DESC;


-- 4. Find customers whose total sales are above average (CTE + Subquery)
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_name, ROUND(cs.total_sales, 2) AS total_sales
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id
WHERE cs.total_sales > (
    SELECT AVG(total_sales)
    FROM customer_sales
)
ORDER BY total_sales DESC;


-- 5. Rank all customers based on total sales (Window Function)
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_name, ROUND(cs.total_sales, 2) AS total_sales,
       RANK() OVER (ORDER BY cs.total_sales DESC) AS sales_rank,
       DENSE_RANK() OVER (ORDER BY cs.total_sales DESC) AS sales_dense_rank
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id;


-- 6. Assign row numbers to each order within a customer (Window Function + PARTITION BY)
-- Sorts customer purchases chronologically by date.
SELECT c.customer_name, o.order_id, o.order_date, ROUND(o.sales, 2) AS sales,
       ROW_NUMBER() OVER (
           PARTITION BY o.customer_id 
           ORDER BY o.order_date DESC, o.row_id
       ) AS order_seq
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id;


-- 7. Display top 3 customers based on total sales (Window Function)
WITH customer_ranks AS (
    SELECT customer_id, SUM(sales) AS total_sales,
           RANK() OVER (ORDER BY SUM(sales) DESC) AS rnk
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_name, ROUND(cr.total_sales, 2) AS total_sales, cr.rnk
FROM customer_ranks cr
JOIN customers c ON cr.customer_id = c.customer_id
WHERE cr.rnk <= 3;


-- STEP 3: Final Combined Query

-- Shows Customer Name, Total Sales, and Rank together (JOIN + CTE + Window Function)
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_name, ROUND(cs.total_sales, 2) AS total_sales,
       RANK() OVER (ORDER BY cs.total_sales DESC) AS sales_rank,
       DENSE_RANK() OVER (ORDER BY cs.total_sales DESC) AS sales_dense_rank
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id;


-- Mini Project: Customer Sales Insights

-- M1. Who are the top 5 customers?
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_name, ROUND(cs.total_sales, 2) AS total_sales
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id
ORDER BY total_sales DESC
LIMIT 5;


-- M2. Who are the bottom 5 customers?
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_name, ROUND(cs.total_sales, 2) AS total_sales
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id
ORDER BY total_sales ASC
LIMIT 5;


-- M3. Which customers made only one order?
SELECT c.customer_name, COUNT(DISTINCT o.order_id) AS total_orders
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY o.customer_id, c.customer_name
HAVING COUNT(DISTINCT o.order_id) = 1
ORDER BY customer_name;


-- M4. Which customers have above-average sales?
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_name, ROUND(cs.total_sales, 2) AS total_sales
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id
WHERE cs.total_sales > (
    SELECT AVG(total_sales)
    FROM customer_sales
)
ORDER BY total_sales DESC;


-- M5. What is the highest order value per customer?

-- Interpretation A: Highest single line item value per customer
SELECT c.customer_name, ROUND(MAX(o.sales), 2) AS max_line_item_value
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY o.customer_id, c.customer_name
ORDER BY max_line_item_value DESC;

-- Interpretation B: Highest aggregated order total (sum of line items with the same Order ID) per customer
WITH order_totals AS (
    SELECT customer_id, order_id, SUM(sales) AS total_order_sales
    FROM orders
    GROUP BY customer_id, order_id
)
SELECT c.customer_name, ROUND(MAX(ot.total_order_sales), 2) AS max_order_value
FROM order_totals ot
JOIN customers c ON ot.customer_id = c.customer_id
GROUP BY ot.customer_id, c.customer_name
ORDER BY max_order_value DESC;
