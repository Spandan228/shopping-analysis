"""
Database Loader Module.

Responsibilities:
1. Initializes SQLite database at `db/food_delivery_analytics.db`.
2. Applies DDL schema from `sql/schema.sql`.
3. Ingests cleaned CSV datasets into SQLite tables.
4. Verifies record counts and validates foreign key integrity post-load.
"""

import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "db")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "food_delivery_analytics.db")

CLEANED_DIR = os.path.join(BASE_DIR, "data", "cleaned")
PROVIDED_DIR = os.path.join(BASE_DIR, "DataSets")
SCHEMA_PATH = os.path.join(BASE_DIR, "sql", "schema.sql")

def initialize_db(conn):
    print("Initializing Database Schema...")
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    print("Database schema successfully created.")

def load_tables(conn):
    print("\nLoading cleaned CSV datasets into SQL Database...")
    
    # 1. Load Customers
    cust_path = os.path.join(CLEANED_DIR, "customers_clean.csv")
    if os.path.exists(cust_path):
        df_cust = pd.read_csv(cust_path)
        df_cust.to_sql("customers", conn, if_exists="append", index=False)
        print(f"Loaded {len(df_cust)} records into 'customers' table.")
        
    # 2. Load Products
    prod_path = os.path.join(CLEANED_DIR, "products_clean.csv")
    if os.path.exists(prod_path):
        df_prod = pd.read_csv(prod_path)
        df_prod.to_sql("products", conn, if_exists="append", index=False)
        print(f"Loaded {len(df_prod)} records into 'products' table.")
        
    # 3. Load Orders
    orders_path = os.path.join(CLEANED_DIR, "orders_clean.csv")
    if os.path.exists(orders_path):
        df_orders = pd.read_csv(orders_path)
        df_orders.to_sql("orders", conn, if_exists="append", index=False)
        print(f"Loaded {len(df_orders)} records into 'orders' table.")
        
    # 4. Load Order Items
    items_path = os.path.join(CLEANED_DIR, "order_items_clean.csv")
    if os.path.exists(items_path):
        df_items = pd.read_csv(items_path)
        df_items.to_sql("order_items", conn, if_exists="append", index=False)
        print(f"Loaded {len(df_items)} records into 'order_items' table.")
        
    # 5. Load Users SCD
    users_path = os.path.join(CLEANED_DIR, "users_scd_clean.csv")
    if not os.path.exists(users_path):
        users_path = os.path.join(PROVIDED_DIR, "users_scd.csv")
    if os.path.exists(users_path):
        df_users = pd.read_csv(users_path)
        # Convert boolean is_current to integer 1/0 for SQLite compatibility
        if 'is_current' in df_users.columns:
            df_users['is_current'] = df_users['is_current'].astype(int)
        df_users.to_sql("users_scd", conn, if_exists="append", index=False)
        print(f"Loaded {len(df_users)} records into 'users_scd' table.")

    # 6. Load Restaurants SCD
    rest_path = os.path.join(CLEANED_DIR, "restaurants_scd_clean.csv")
    if not os.path.exists(rest_path):
        rest_path = os.path.join(PROVIDED_DIR, "restaurants_scd.csv")
    if os.path.exists(rest_path):
        df_rest = pd.read_csv(rest_path)
        if 'is_current' in df_rest.columns:
            df_rest['is_current'] = df_rest['is_current'].astype(int)
        df_rest.to_sql("restaurants_scd", conn, if_exists="append", index=False)
        print(f"Loaded {len(df_rest)} records into 'restaurants_scd' table.")

    # 7. Load Orders CDC
    cdc_path = os.path.join(CLEANED_DIR, "orders_cdc_clean.csv")
    if not os.path.exists(cdc_path):
        cdc_path = os.path.join(PROVIDED_DIR, "orders_cdc.csv")
    if os.path.exists(cdc_path):
        df_cdc = pd.read_csv(cdc_path)
        df_cdc.to_sql("orders_cdc", conn, if_exists="append", index=False)
        print(f"Loaded {len(df_cdc)} records into 'orders_cdc' table.")

def verify_data(conn):
    print("\n=== VERIFYING DATABASE TABLES & ROW COUNTS ===")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]
    
    for tbl in sorted(tables):
        cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
        cnt = cursor.fetchone()[0]
        print(f"Table '{tbl}': {cnt} rows")

    # Check foreign key violations
    cursor.execute("PRAGMA foreign_key_check;")
    fk_errors = cursor.fetchall()
    if fk_errors:
        print(f"WARNING: Found {len(fk_errors)} Foreign Key Violations!")
    else:
        print("SUCCESS: Zero Foreign Key Violations. Referential Integrity intact!")

def main():
    print(f"Connecting to database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    try:
        initialize_db(conn)
        load_tables(conn)
        verify_data(conn)
    finally:
        conn.close()
        print("Database loading complete.")

if __name__ == "__main__":
    main()
