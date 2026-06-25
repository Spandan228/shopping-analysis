-- Section E: Advanced Concepts (CASE, ACID, Transactions)

USE shopease;

-- Q24: Use CASE to classify products into price tiers
SELECT 
    product_name, 
    unit_price,
    CASE 
        WHEN unit_price < 1000.00 THEN 'Budget'
        WHEN unit_price BETWEEN 1000.00 AND 3000.00 THEN 'Mid-Range'
        ELSE 'Premium'
    END AS price_tier
FROM products
ORDER BY unit_price ASC;

-- Q25: Count orders by status (Delivered vs Not Delivered) in a single row using conditional aggregation
SELECT 
    SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_count,
    SUM(CASE WHEN status != 'Delivered' THEN 1 ELSE 0 END) AS not_delivered_count
FROM orders;

-- Q26: Explain ACID properties using a bank transfer example
/*
Real-World Example: Customer A transfers ₹1000 to Customer B.
Steps: 1. Debit ₹1000 from A. 2. Credit ₹1000 to B.

- Atomicity: Both debit and credit must succeed. If step 2 fails (e.g. power loss), the debit must 
  be rolled back so money doesn't disappear.
- Consistency: Balance rules must be maintained. For example, if A's balance cannot go below zero 
  and A only has ₹400, the database blocks the transaction to prevent invalid state.
- Isolation: Other concurrently running queries shouldn't see A's balance after debit but before 
  credit. They see either the state before the transfer or after it completes.
- Durability: Once the transfer is committed, the new balances are permanently written to disk 
  and will survive server crashes.
*/

-- Q27: Write a SQL transaction to perform order insertion, item additions, and stock updates atomically
-- NOTE: We provide two approaches below.

-- ============================================================================
-- APPROACH 1: Standard SQL Transaction Block
-- ============================================================================

-- Cleanup previous run to allow re-runs
DELETE FROM order_items WHERE order_id = 1011;
DELETE FROM orders WHERE order_id = 1011;

START TRANSACTION;

-- 1. Insert order (customer 102 exists in customers)
INSERT INTO orders (order_id, customer_id, order_date, status, total_amount)
VALUES (1011, 102, CURDATE(), 'Pending', 1598.00);

-- 2. Insert order items
-- Product 207: Laptop Stand (899.00, discount 0%)
INSERT INTO order_items (item_id, order_id, product_id, quantity, unit_price, discount_pct)
VALUES (5016, 1011, 207, 1, 899.00, 0.00);

-- Product 202: Cotton T-Shirt (799.00, discount 12.52% to equal total order amount)
INSERT INTO order_items (item_id, order_id, product_id, quantity, unit_price, discount_pct)
VALUES (5017, 1011, 202, 1, 799.00, 12.52);

-- 3. Update stock quantities
UPDATE products SET stock_qty = stock_qty - 1 WHERE product_id = 207;
UPDATE products SET stock_qty = stock_qty - 1 WHERE product_id = 202;

COMMIT;

-- ============================================================================
-- APPROACH 2: Stored Procedure with Automatic Exception Handling and Rollback
-- ============================================================================
-- Wraps the transaction in a procedure to automatically trigger a rollback on runtime error.

DROP PROCEDURE IF EXISTS PlaceOrder1011;

DELIMITER $$

CREATE PROCEDURE PlaceOrder1011()
BEGIN
    -- Rollback automatically if any SQLEXCEPTION is encountered
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Transaction Failed! Error encountered. Rollback executed.' AS Status;
    END;

    START TRANSACTION;

    -- 1. Insert order
    INSERT INTO orders (order_id, customer_id, order_date, status, total_amount)
    VALUES (1011, 102, CURDATE(), 'Pending', 1598.00);

    -- 2. Insert items
    INSERT INTO order_items (item_id, order_id, product_id, quantity, unit_price, discount_pct)
    VALUES (5016, 1011, 207, 1, 899.00, 0.00);

    INSERT INTO order_items (item_id, order_id, product_id, quantity, unit_price, discount_pct)
    VALUES (5017, 1011, 202, 1, 799.00, 12.52);

    -- 3. Update stock
    UPDATE products SET stock_qty = stock_qty - 1 WHERE product_id = 207;
    UPDATE products SET stock_qty = stock_qty - 1 WHERE product_id = 202;

    COMMIT;
    SELECT 'Transaction Succeeded! Order 1011 created and stock updated.' AS Status;

END$$

DELIMITER ;

-- Call the procedure to execute and demonstrate transaction handling
-- To test the procedure, uncomment the following three lines:
-- DELETE FROM order_items WHERE order_id = 1011;
-- DELETE FROM orders WHERE order_id = 1011;
-- CALL PlaceOrder1011();
