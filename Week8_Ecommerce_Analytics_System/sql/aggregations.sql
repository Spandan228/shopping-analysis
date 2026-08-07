-- STEP 4: SQL ANALYTICS - JOINS & AGGREGATIONS

-- 1. Total Revenue Per Customer
SELECT 
    c.customer_id,
    c.name AS customer_name,
    c.city,
    c.segment,
    COUNT(o.order_id) AS total_orders,
    ROUND(SUM(o.total_amount), 2) AS total_revenue,
    ROUND(AVG(o.total_amount), 2) AS average_order_value
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status != 'Cancelled'
GROUP BY c.customer_id, c.name, c.city, c.segment
ORDER BY total_revenue DESC;


-- 2. Total Revenue Per Product Category
SELECT 
    p.category,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    SUM(oi.quantity) AS total_units_sold,
    ROUND(SUM(oi.subtotal), 2) AS category_revenue,
    ROUND(AVG(oi.unit_price), 2) AS avg_unit_price
FROM order_items oi
INNER JOIN products p ON oi.product_id = p.product_id
INNER JOIN orders o ON oi.order_id = o.order_id
WHERE o.status != 'Cancelled'
GROUP BY p.category
ORDER BY category_revenue DESC;


-- 3. Monthly Revenue & Order Volume Trends
SELECT 
    STRFTIME('%Y-%m', o.order_timestamp) AS order_month,
    COUNT(o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS unique_customers,
    ROUND(SUM(o.total_amount), 2) AS monthly_revenue,
    ROUND(AVG(o.total_amount), 2) AS monthly_aov
FROM orders o
WHERE o.status != 'Cancelled'
GROUP BY STRFTIME('%Y-%m', o.order_timestamp)
ORDER BY order_month ASC;


-- 4. Top 10 Products by Quantity Sold and Revenue
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    SUM(oi.quantity) AS total_quantity_sold,
    ROUND(SUM(oi.subtotal), 2) AS total_product_revenue
FROM order_items oi
INNER JOIN products p ON oi.product_id = p.product_id
INNER JOIN orders o ON oi.order_id = o.order_id
WHERE o.status != 'Cancelled'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_product_revenue DESC
LIMIT 10;


-- 5. Average Order Value (AOV) by Customer Segment & City
SELECT 
    c.segment,
    c.city,
    COUNT(o.order_id) AS total_orders,
    ROUND(SUM(o.total_amount), 2) AS total_spend,
    ROUND(AVG(o.total_amount), 2) AS segment_city_aov
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status != 'Cancelled'
GROUP BY c.segment, c.city
ORDER BY total_spend DESC;
