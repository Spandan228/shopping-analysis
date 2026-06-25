-- Section B: Filtering & Optimization (WHERE, Indexes)

USE shopease;

-- Q7: Retrieve all orders with status = 'Delivered'
SELECT * 
FROM orders 
WHERE status = 'Delivered';

-- Q8: Find all products in 'Electronics' category with price > ₹2000
SELECT * 
FROM products 
WHERE category = 'Electronics' 
  AND unit_price > 2000.00;

-- Q9: List customers who joined in 2024 and live in 'Maharashtra'
-- Note: We use a date-range filter for SARGability (index friendliness)
SELECT * 
FROM customers 
WHERE state = 'Maharashtra' 
  AND join_date BETWEEN '2024-01-01' AND '2024-12-31';

-- Q10: Find orders placed between 2024-08-10 and 2024-08-25 that are NOT cancelled
SELECT * 
FROM orders 
WHERE order_date BETWEEN '2024-08-10' AND '2024-08-25' 
  AND status != 'Cancelled';

-- Q11: Explain what the index idx_orders_date does and how it improves query performance
/*
The index `idx_orders_date` is a B-Tree index on the `order_date` column in the `orders` table. 
Instead of doing a full table scan, MySQL uses the B-tree to perform a binary range scan. 
This reduces disk I/O and speeds up search queries significantly, especially on larger datasets.

Example query that benefits from this index:
*/
SELECT * FROM orders WHERE order_date = '2024-08-15';

-- Q12: Explain if YEAR(join_date) = 2024 uses index and provide a SARGable rewrite
/*
No, the index on join_date won't be used. Applying functions like YEAR() to indexed columns 
prevents the optimizer from using the index, since the server has to evaluate the function for 
every row in the table (non-SARGable query).

Index-friendly (SARGable) rewrite:
*/
SELECT * 
FROM customers 
WHERE join_date >= '2024-01-01' AND join_date <= '2024-12-31';
