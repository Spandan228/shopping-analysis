-- DATABASE SCHEMA DDL - Food Delivery & E-Commerce Analytics System
-- Target Engine: SQLite 3.x / PostgreSQL / MySQL Compatible
-- Enables strict foreign keys, indexing, check constraints, and default values.

PRAGMA foreign_keys = ON;

-- 1. Customers Table (E-Commerce Customer Dimension)
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    city VARCHAR(100) NOT NULL,
    signup_date DATE NOT NULL,
    segment VARCHAR(50) DEFAULT 'Consumer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Products Table (E-Commerce Product / Food Item Dimension)
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
    stock_quantity INTEGER NOT NULL CHECK (stock_quantity >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Orders Table (E-Commerce Base Transactions)
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    order_timestamp TIMESTAMP NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL CHECK (total_amount >= 0),
    status VARCHAR(50) NOT NULL CHECK (status IN ('Placed', 'Preparing', 'Out For Delivery', 'Delivered', 'Cancelled')),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- 4. Order Items Table (Transactional Grain)
CREATE TABLE order_items (
    item_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
    subtotal DECIMAL(10, 2) NOT NULL CHECK (subtotal >= 0),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- 5. Users SCD Table (Food Delivery Dimension with History)
DROP TABLE IF EXISTS users_scd;
CREATE TABLE users_scd (
    user_id VARCHAR(50) NOT NULL,
    user_name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    effective_from DATE NOT NULL,
    effective_to DATE,
    is_current BOOLEAN NOT NULL DEFAULT 1,
    PRIMARY KEY (user_id, effective_from)
);

-- 6. Restaurants SCD Table (Food Delivery Dimension with History)
DROP TABLE IF EXISTS restaurants_scd;
CREATE TABLE restaurants_scd (
    restaurant_id VARCHAR(50) NOT NULL,
    restaurant_name VARCHAR(150) NOT NULL,
    cuisine VARCHAR(100) NOT NULL,
    rating DECIMAL(3, 2) CHECK (rating >= 1.0 AND rating <= 5.0),
    effective_from DATE NOT NULL,
    effective_to DATE,
    is_current BOOLEAN NOT NULL DEFAULT 1,
    PRIMARY KEY (restaurant_id, effective_from)
);

-- 7. Orders CDC Table (Change Data Capture Audit Log)
DROP TABLE IF EXISTS orders_cdc;
CREATE TABLE orders_cdc (
    order_id VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    PRIMARY KEY (order_id, updated_at)
);

-- Indexes for performance tuning & fast joins
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_timestamp ON orders(order_timestamp);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_users_scd_user_id ON users_scd(user_id, is_current);
CREATE INDEX IF NOT EXISTS idx_restaurants_scd_rest_id ON restaurants_scd(restaurant_id, is_current);
