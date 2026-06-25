-- Section D: Joins & Relationships

USE shopease;

-- Q19: Inner join to display orders with customer names
SELECT 
    o.order_id, 
    o.order_date, 
    c.first_name, 
    c.last_name, 
    o.total_amount 
FROM orders o 
INNER JOIN customers c ON o.customer_id = c.customer_id;

-- Q20: Left join to list all customers and their orders (includes customers without orders)
SELECT 
    c.customer_id, 
    c.first_name, 
    c.last_name, 
    o.order_id, 
    o.order_date, 
    o.total_amount 
FROM customers c 
LEFT JOIN orders o ON c.customer_id = o.customer_id;

-- Q21: Three-table join to show order details (orders -> order_items -> products)
SELECT 
    o.order_id, 
    p.product_name, 
    oi.quantity, 
    oi.unit_price, 
    oi.discount_pct 
FROM orders o
INNER JOIN order_items oi ON o.order_id = oi.order_id
INNER JOIN products p ON oi.product_id = p.product_id;

-- Q22: Explain the difference between LEFT JOIN and RIGHT JOIN, and when to use FULL OUTER JOIN
/*
Differences:
- LEFT JOIN returns all records from the left table and matched records from the right table. 
  Unmatched right columns are returned as NULL. (e.g. all customers, with or without orders).
- RIGHT JOIN returns all records from the right table and matched records from the left table. 
  Unmatched left columns are returned as NULL. (e.g. all orders, with or without matching customers).

FULL OUTER JOIN:
- Returns all records from both tables, matching where possible, and showing NULLs on either side when unmatched.
- Useful for identifying orphaned rows or comparing discrepancies between two tables. 
- MySQL does not support FULL OUTER JOIN natively; we emulate it by UNIONing a LEFT JOIN and a RIGHT JOIN.
*/

-- Q23: Foreign Key relationships and insertion behavior with invalid keys
/*
Foreign Keys:
1. orders.customer_id -> customers.customer_id
2. order_items.order_id -> orders.order_id
3. order_items.product_id -> products.product_id

If we try to insert an order with an invalid customer_id (e.g., 999), the database will prevent it 
and return:
"Error Code: 1452. Cannot add or update a child row: a foreign key constraint fails"
This maintains referential integrity by ensuring we cannot create orphaned records.
*/

-- Verification Query (Uncomment to test - will fail due to invalid customer_id):
-- INSERT INTO orders (order_id, customer_id, order_date, status, total_amount)
-- VALUES (1012, 999, '2024-09-01', 'Pending', 500.00);
