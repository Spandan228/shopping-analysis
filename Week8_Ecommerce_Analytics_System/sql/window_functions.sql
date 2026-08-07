-- STEP 5: SQL ANALYTICS - WINDOW FUNCTIONS & CTEs

-- 1. Rank Customers by Lifetime Value (LTV) using RANK() and DENSE_RANK()
WITH CustomerLTV AS (
    SELECT 
        c.customer_id,
        c.name AS customer_name,
        c.city,
        c.segment,
        COUNT(o.order_id) AS total_orders,
        ROUND(SUM(o.total_amount), 2) AS total_lifetime_spend
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.status != 'Cancelled'
    GROUP BY c.customer_id, c.name, c.city, c.segment
)
SELECT 
    customer_id,
    customer_name,
    city,
    segment,
    total_orders,
    total_lifetime_spend,
    RANK() OVER (ORDER BY total_lifetime_spend DESC) AS ltv_rank,
    DENSE_RANK() OVER (ORDER BY total_lifetime_spend DESC) AS ltv_dense_rank,
    DENSE_RANK() OVER (PARTITION BY city ORDER BY total_lifetime_spend DESC) AS city_ltv_rank
FROM CustomerLTV
ORDER BY total_lifetime_spend DESC
LIMIT 20;


-- 2. Cumulative Running Totals & 3-Month Moving Averages for Revenue
WITH DailyMonthlyRevenue AS (
    SELECT 
        DATE(o.order_timestamp) AS order_date,
        ROUND(SUM(o.total_amount), 2) AS daily_revenue,
        COUNT(o.order_id) AS daily_orders
    FROM orders o
    WHERE o.status != 'Cancelled'
    GROUP BY DATE(o.order_timestamp)
)
SELECT 
    order_date,
    daily_revenue,
    daily_orders,
    ROUND(SUM(daily_revenue) OVER (ORDER BY order_date ASC), 2) AS cumulative_running_total,
    ROUND(AVG(daily_revenue) OVER (ORDER BY order_date ASC ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS 7_day_moving_avg_revenue
FROM DailyMonthlyRevenue
ORDER BY order_date ASC;


-- 3. Monthly Revenue Growth Rate CTE Analysis
WITH MonthlyMetrics AS (
    SELECT 
        STRFTIME('%Y-%m', o.order_timestamp) AS order_month,
        ROUND(SUM(o.total_amount), 2) AS current_month_revenue,
        COUNT(o.order_id) AS current_month_orders
    FROM orders o
    WHERE o.status != 'Cancelled'
    GROUP BY STRFTIME('%Y-%m', o.order_timestamp)
),
MonthlyGrowth AS (
    SELECT 
        order_month,
        current_month_revenue,
        current_month_orders,
        LAG(current_month_revenue, 1) OVER (ORDER BY order_month ASC) AS previous_month_revenue,
        LAG(current_month_orders, 1) OVER (ORDER BY order_month ASC) AS previous_month_orders
    FROM MonthlyMetrics
)
SELECT 
    order_month,
    current_month_revenue,
    previous_month_revenue,
    ROUND(current_month_revenue - COALESCE(previous_month_revenue, 0), 2) AS absolute_growth,
    ROUND(
        CASE 
            WHEN previous_month_revenue IS NULL OR previous_month_revenue = 0 THEN 0.0
            ELSE ((current_month_revenue - previous_month_revenue) * 100.0 / previous_month_revenue)
        END, 2
    ) AS mom_growth_percentage
FROM MonthlyGrowth
ORDER BY order_month ASC;


-- 4. Customer Recency & Subsequent Order Gap Analysis
WITH CustomerOrderSequence AS (
    SELECT 
        o.customer_id,
        o.order_id,
        o.order_timestamp,
        o.total_amount,
        ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_timestamp ASC) AS order_number,
        LAG(o.order_timestamp, 1) OVER (PARTITION BY o.customer_id ORDER BY o.order_timestamp ASC) AS previous_order_timestamp
    FROM orders o
    WHERE o.status != 'Cancelled'
)
SELECT 
    customer_id,
    order_id,
    order_number,
    order_timestamp,
    previous_order_timestamp,
    ROUND((JULIANDAY(order_timestamp) - JULIANDAY(previous_order_timestamp)), 1) AS days_since_previous_order
FROM CustomerOrderSequence
WHERE previous_order_timestamp IS NOT NULL
ORDER BY customer_id, order_number
LIMIT 20;
