-- Section A: SQL Basics (SELECT, Constraints, Primary Keys)

USE shopease;

-- Q1: Display all customers
SELECT * FROM customers;

-- Q2: Get name and city of all customers
SELECT first_name, last_name, city FROM customers;

-- Q3: Get list of unique product categories
SELECT DISTINCT category FROM products;

-- Q4: Identify primary key of each table and explain properties
/*
Primary Keys:
- customers: customer_id
- products: product_id
- orders: order_id
- order_items: item_id

A Primary Key must be UNIQUE and NOT NULL to ensure that every record in a table has a 
valid, unique identifier. If a PK could be duplicated or null, we would lose referential 
integrity and have no reliable way to reference or distinguish individual rows.
*/

-- Q5: Explain constraints on customer email column and duplicate insert behavior
/*
Constraints: UNIQUE, NOT NULL.
If we attempt to insert a duplicate email, the transaction will fail and return:
"Error Code: 1062. Duplicate entry '...' for key 'email'"
because the UNIQUE constraint prevents duplicate entries for this field.
*/

-- Verification Query (Uncomment to test - will fail due to duplicate email):
-- INSERT INTO customers (customer_id, first_name, last_name, email, city, state, join_date)
-- VALUES (109, 'Duplicate', 'Test', 'aarav.s@email.com', 'Mumbai', 'Maharashtra', '2024-09-01');

-- Q6: Try inserting a product with unit_price = -50
/*
Attempting to insert a negative unit price will fail and return:
"Error Code: 3819. Check constraint 'products_chk_1' is violated."
The failure is caused by the CHECK (unit_price > 0) constraint defined on the products table.
*/

-- Failed Insert Query (Uncomment to test):
-- INSERT INTO products (product_id, product_name, category, brand, unit_price, stock_qty)
-- VALUES (209, 'Negative Price Item', 'Electronics', 'FailBrand', -50.00, 100);
