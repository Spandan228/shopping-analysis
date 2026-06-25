-- Section C: Aggregation (GROUP BY, SUM, COUNT, AVG, MIN, MAX)

USE shopease;

-- Q13: Count the total number of orders in the orders table
SELECT COUNT(order_id) AS total_orders 
FROM orders;

-- Q14: Find the total revenue from all 'Delivered' orders
SELECT SUM(total_amount) AS total_revenue_delivered 
FROM orders 
WHERE status = 'Delivered';

-- Q15: Calculate the average unit_price of products in each category
SELECT 
    category, 
    ROUND(AVG(unit_price), 2) AS average_unit_price 
FROM products 
GROUP BY category;

-- Q16: For each order status, find the count of orders and the total revenue. Sort by revenue descending.
SELECT 
    status, 
    COUNT(order_id) AS order_count, 
    SUM(total_amount) AS total_revenue 
FROM orders 
GROUP BY status 
ORDER BY total_revenue DESC;

-- Q17: Find the most expensive (MAX) and cheapest (MIN) product in each category
SELECT 
    category, 
    MAX(unit_price) AS max_unit_price, 
    MIN(unit_price) AS min_unit_price 
FROM products 
GROUP BY category;

-- Q18: List all product categories where the average unit_price is greater than ₹2000
-- Note: WHERE filters rows before grouping; HAVING filters rows after grouping.
SELECT 
    category, 
    ROUND(AVG(unit_price), 2) AS average_unit_price 
FROM products 
GROUP BY category 
HAVING AVG(unit_price) > 2000.00;
