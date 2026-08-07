-- STEP 6 & STEP 7: COHORT ANALYSIS, RETENTION & CUSTOMER SEGMENTATION (RFM)

-- STEP 6: COHORT & RETENTION ANALYSIS

-- 1. Customer First Purchase Cohorts
WITH FirstPurchase AS (
    SELECT 
        customer_id,
        MIN(STRFTIME('%Y-%m', order_timestamp)) AS cohort_month
    FROM orders
    WHERE status != 'Cancelled'
    GROUP BY customer_id
),
CustomerActivity AS (
    SELECT DISTINCT
        o.customer_id,
        fp.cohort_month,
        STRFTIME('%Y-%m', o.order_timestamp) AS activity_month,
        (
            (CAST(STRFTIME('%Y', o.order_timestamp) AS INTEGER) - CAST(SUBSTR(fp.cohort_month, 1, 4) AS INTEGER)) * 12 +
            (CAST(STRFTIME('%m', o.order_timestamp) AS INTEGER) - CAST(SUBSTR(fp.cohort_month, 6, 2) AS INTEGER))
        ) AS month_number
    FROM orders o
    INNER JOIN FirstPurchase fp ON o.customer_id = fp.customer_id
    WHERE o.status != 'Cancelled'
)
SELECT 
    cohort_month,
    COUNT(DISTINCT CASE WHEN month_number = 0 THEN customer_id END) AS cohort_size,
    COUNT(DISTINCT CASE WHEN month_number = 1 THEN customer_id END) AS month_1_users,
    COUNT(DISTINCT CASE WHEN month_number = 2 THEN customer_id END) AS month_2_users,
    COUNT(DISTINCT CASE WHEN month_number = 3 THEN customer_id END) AS month_3_users,
    COUNT(DISTINCT CASE WHEN month_number = 6 THEN customer_id END) AS month_6_users,
    COUNT(DISTINCT CASE WHEN month_number = 12 THEN customer_id END) AS month_12_users
FROM CustomerActivity
GROUP BY cohort_month
ORDER BY cohort_month ASC;


-- 2. Monthly Retention Rate Matrix Percentage
WITH FirstPurchase AS (
    SELECT 
        customer_id,
        MIN(STRFTIME('%Y-%m', order_timestamp)) AS cohort_month
    FROM orders
    WHERE status != 'Cancelled'
    GROUP BY customer_id
),
CohortSizes AS (
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_id) AS cohort_size
    FROM FirstPurchase
    GROUP BY cohort_month
),
CustomerActivity AS (
    SELECT DISTINCT
        o.customer_id,
        fp.cohort_month,
        (
            (CAST(STRFTIME('%Y', o.order_timestamp) AS INTEGER) - CAST(SUBSTR(fp.cohort_month, 1, 4) AS INTEGER)) * 12 +
            (CAST(STRFTIME('%m', o.order_timestamp) AS INTEGER) - CAST(SUBSTR(fp.cohort_month, 6, 2) AS INTEGER))
        ) AS month_number
    FROM orders o
    INNER JOIN FirstPurchase fp ON o.customer_id = fp.customer_id
    WHERE o.status != 'Cancelled'
)
SELECT 
    ca.cohort_month,
    cs.cohort_size,
    ROUND(COUNT(DISTINCT CASE WHEN month_number = 0 THEN ca.customer_id END) * 100.0 / cs.cohort_size, 1) AS month_0_retention_pct,
    ROUND(COUNT(DISTINCT CASE WHEN month_number = 1 THEN ca.customer_id END) * 100.0 / cs.cohort_size, 1) AS month_1_retention_pct,
    ROUND(COUNT(DISTINCT CASE WHEN month_number = 2 THEN ca.customer_id END) * 100.0 / cs.cohort_size, 1) AS month_2_retention_pct,
    ROUND(COUNT(DISTINCT CASE WHEN month_number = 3 THEN ca.customer_id END) * 100.0 / cs.cohort_size, 1) AS month_3_retention_pct
FROM CustomerActivity ca
INNER JOIN CohortSizes cs ON ca.cohort_month = cs.cohort_month
GROUP BY ca.cohort_month, cs.cohort_size
ORDER BY ca.cohort_month ASC;


-- 3. Repeat vs Churned Customer Identification (Churn Threshold = 90 days inactivity)
WITH LastOrder AS (
    SELECT 
        c.customer_id,
        c.name AS customer_name,
        COUNT(o.order_id) AS total_orders,
        ROUND(SUM(o.total_amount), 2) AS total_spend,
        MAX(o.order_timestamp) AS last_order_date
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status != 'Cancelled'
    GROUP BY c.customer_id, c.name
)
SELECT 
    customer_id,
    customer_name,
    total_orders,
    total_spend,
    last_order_date,
    CASE 
        WHEN total_orders IS NULL OR total_orders = 0 THEN 'Never Purchased'
        WHEN JULIANDAY('now') - JULIANDAY(last_order_date) > 90 THEN 'Churned (>90 days inactive)'
        WHEN total_orders = 1 THEN 'One-Time Customer'
        ELSE 'Active Repeat Customer'
    END AS customer_lifecycle_status
FROM LastOrder
ORDER BY total_spend DESC
LIMIT 20;


-- ----------------------------------------------------------------------------
-- STEP 7: CUSTOMER SEGMENTATION & RFM ANALYSIS
-- ----------------------------------------------------------------------------

-- 4. Purchase Frequency & Spend Tier Segmentation
WITH CustomerMetrics AS (
    SELECT 
        c.customer_id,
        c.name AS customer_name,
        c.city,
        COUNT(o.order_id) AS total_orders,
        COALESCE(ROUND(SUM(o.total_amount), 2), 0.0) AS total_spend
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status != 'Cancelled'
    GROUP BY c.customer_id, c.name, c.city
)
SELECT 
    customer_id,
    customer_name,
    city,
    total_orders,
    total_spend,
    CASE 
        WHEN total_orders = 0 THEN 'Inactive'
        WHEN total_orders = 1 THEN 'One-Time'
        WHEN total_orders BETWEEN 2 AND 5 THEN 'Occasional'
        ELSE 'Loyal'
    END AS frequency_segment,
    CASE 
        WHEN total_spend < 500 THEN 'Low Spend (< $500)'
        WHEN total_spend BETWEEN 500 AND 2000 THEN 'Medium Spend ($500-$2k)'
        ELSE 'High Spend / VIP (> $2k)'
    END AS spend_tier
FROM CustomerMetrics
ORDER BY total_spend DESC
LIMIT 20;


-- 5. Full RFM (Recency, Frequency, Monetary) Scoring
WITH MaxDate AS (
    SELECT MAX(order_timestamp) AS max_order_ts FROM orders
),
RFM_Raw AS (
    SELECT 
        c.customer_id,
        c.name AS customer_name,
        c.city,
        CAST(JULIANDAY((SELECT max_order_ts FROM MaxDate)) - JULIANDAY(MAX(o.order_timestamp)) AS INTEGER) AS recency_days,
        COUNT(o.order_id) AS frequency,
        ROUND(SUM(o.total_amount), 2) AS monetary
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.status != 'Cancelled'
    GROUP BY c.customer_id, c.name, c.city
),
RFM_Scores AS (
    SELECT 
        customer_id,
        customer_name,
        city,
        recency_days,
        frequency,
        monetary,
        NTILE(4) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(4) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(4) OVER (ORDER BY monetary ASC) AS m_score
    FROM RFM_Raw
)
SELECT 
    customer_id,
    customer_name,
    city,
    recency_days,
    frequency,
    monetary,
    (r_score || f_score || m_score) AS rfm_cell,
    CASE 
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Champions / VIP'
        WHEN r_score >= 3 AND f_score >= 2 THEN 'Loyal Customers'
        WHEN r_score >= 3 AND f_score = 1 THEN 'Recent New Customers'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk / Need Attention'
        WHEN r_score = 1 AND f_score = 1 THEN 'Lost / Churned'
        ELSE 'Potential Loyalist'
    END AS rfm_segment
FROM RFM_Scores
ORDER BY monetary DESC
LIMIT 25;
