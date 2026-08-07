"""
Data Cleaning & Validation Module using Pandas.

Responsibilities:
1. Loads raw CSV datasets from `data/raw/` and `DataSets/`.
2. Handles missing values (imputation or dropping invalid critical keys).
3. Deduplicates records based on primary key constraints.
4. Corrects data types (dates, numeric fields, strings).
5. Standardizes string formatting (IDs strictly uppercase, text Title Case).
6. Enforces referential integrity (eliminating orphaned foreign key records).
7. Exports clean datasets to `data/cleaned/`.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROVIDED_DIR = os.path.join(BASE_DIR, "DataSets")
CLEANED_DIR = os.path.join(BASE_DIR, "data", "cleaned")
os.makedirs(CLEANED_DIR, exist_ok=True)

def standardize_strings(df):
    """Trims whitespace, converts IDs to UPPERCASE, and applies Title Case to text columns."""
    for col in df.select_dtypes(include=['object', 'string']).columns:
        df[col] = df[col].astype(str).str.strip()
        # Replace string literals with NaN
        df[col] = df[col].replace({'None': np.nan, 'nan': np.nan, 'NaN': np.nan, '': np.nan})
        
        if "id" in col.lower():
            # ID fields must be uppercase
            df[col] = df[col].apply(lambda x: str(x).upper() if pd.notnull(x) else x)
        else:
            # Descriptive text fields converted to Title Case
            df[col] = df[col].apply(lambda x: str(x).title() if pd.notnull(x) else x)
    return df

def clean_customers():
    raw_path = os.path.join(RAW_DIR, "customers.csv")
    if not os.path.exists(raw_path):
        print("customers.csv not found in raw, skipping...")
        return None
        
    print("Cleaning customers.csv...")
    df = pd.read_csv(raw_path)
    
    # Standardize strings first so ID casing is consistent
    df = standardize_strings(df)
    
    # 1. Deduplicate by customer_id (keep first)
    df = df.drop_duplicates(subset=["customer_id"], keep="first")
    
    # 2. Handle missing fields
    df["name"] = df["name"].fillna("Unknown Customer")
    df["city"] = df["city"].fillna("Unknown City")
    df["segment"] = df["segment"].fillna("Consumer")
    df["email"] = df["email"].fillna("no_email@example.com")
    
    # 3. Fix invalid email format
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    invalid_email_mask = ~df["email"].str.match(email_regex, na=False)
    df.loc[invalid_email_mask, "email"] = df.loc[invalid_email_mask, "customer_id"].apply(lambda cid: f"{str(cid).lower()}@example.com")
    
    # 4. Format signup_date
    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["signup_date"] = df["signup_date"].fillna(datetime.now().strftime("%Y-%m-%d"))
    
    clean_path = os.path.join(CLEANED_DIR, "customers_clean.csv")
    df.to_csv(clean_path, index=False)
    print(f"Cleaned customers saved to {clean_path} ({len(df)} rows)")
    return df

def clean_products():
    raw_path = os.path.join(RAW_DIR, "products.csv")
    if not os.path.exists(raw_path):
        print("products.csv not found in raw, skipping...")
        return None
        
    print("Cleaning products.csv...")
    df = pd.read_csv(raw_path)
    df = standardize_strings(df)
    
    # 1. Deduplicate
    df = df.drop_duplicates(subset=["product_id"], keep="first")
    
    # 2. Impute missing categories
    df["category"] = df["category"].fillna("General")
    
    # 3. Handle invalid negative prices
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").abs()
    df["unit_price"] = df["unit_price"].fillna(100.0)
    
    # 4. Ensure non-negative stock
    df["stock_quantity"] = pd.to_numeric(df["stock_quantity"], errors="coerce").fillna(0).astype(int)
    df["stock_quantity"] = df["stock_quantity"].clip(lower=0)
    
    clean_path = os.path.join(CLEANED_DIR, "products_clean.csv")
    df.to_csv(clean_path, index=False)
    print(f"Cleaned products saved to {clean_path} ({len(df)} rows)")
    return df

def clean_orders(customers_df=None, products_df=None):
    raw_path = os.path.join(RAW_DIR, "orders.csv")
    if not os.path.exists(raw_path):
        print("orders.csv not found in raw, skipping...")
        return None
        
    print("Cleaning orders.csv...")
    df = pd.read_csv(raw_path)
    df = standardize_strings(df)
    
    # 1. Deduplicate by order_id
    df = df.drop_duplicates(subset=["order_id"], keep="first")
    
    # 2. Referential integrity check against customers if provided
    if customers_df is not None:
        valid_cust_ids = set(customers_df["customer_id"].unique())
        initial_count = len(df)
        df = df[df["customer_id"].isin(valid_cust_ids)]
        print(f"Referential Integrity: Dropped {initial_count - len(df)} orders with invalid/orphaned customer_id.")
        
    # 3. Clean order_timestamp & remove future dates
    df["order_timestamp"] = pd.to_datetime(df["order_timestamp"], errors="coerce")
    now = pd.Timestamp.now()
    df = df[df["order_timestamp"] <= now]
    df["order_timestamp"] = df["order_timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # 4. Handle missing total amount
    df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce").abs()
    df["total_amount"] = df["total_amount"].fillna(df["total_amount"].median())
    
    # 5. Standardize status
    df["status"] = df["status"].fillna("Placed")
    
    clean_path = os.path.join(CLEANED_DIR, "orders_clean.csv")
    df.to_csv(clean_path, index=False)
    print(f"Cleaned orders saved to {clean_path} ({len(df)} rows)")
    return df

def clean_order_items(orders_df=None, products_df=None):
    raw_path = os.path.join(RAW_DIR, "order_items.csv")
    if not os.path.exists(raw_path):
        print("order_items.csv not found in raw, skipping...")
        return None
        
    print("Cleaning order_items.csv...")
    df = pd.read_csv(raw_path)
    df = standardize_strings(df)
    
    # 1. Deduplicate by item_id
    df = df.drop_duplicates(subset=["item_id"], keep="first")
    
    # 2. Referential integrity checks
    if orders_df is not None:
        valid_order_ids = set(orders_df["order_id"].unique())
        df = df[df["order_id"].isin(valid_order_ids)]
    if products_df is not None:
        valid_prod_ids = set(products_df["product_id"].unique())
        df = df[df["product_id"].isin(valid_prod_ids)]
        
    # 3. Fix zero or negative quantities
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(1).astype(int)
    df.loc[df["quantity"] <= 0, "quantity"] = 1
    
    # 4. Recalculate subtotal for consistency
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").abs().fillna(50.0)
    df["subtotal"] = (df["quantity"] * df["unit_price"]).round(2)
    
    clean_path = os.path.join(CLEANED_DIR, "order_items_clean.csv")
    df.to_csv(clean_path, index=False)
    print(f"Cleaned order_items saved to {clean_path} ({len(df)} rows)")
    return df

def clean_provided_datasets():
    """Cleans the provided Food Delivery Datasets (users_scd, restaurants_scd, orders, orders_cdc)."""
    print("\n=== CLEANING PROVIDED FOOD DELIVERY DATASETS ===")
    
    # 1. Users SCD
    users_path = os.path.join(PROVIDED_DIR, "users_scd.csv")
    if os.path.exists(users_path):
        df_users = pd.read_csv(users_path)
        df_users = standardize_strings(df_users)
        df_users = df_users.drop_duplicates()
        df_users["city"] = df_users["city"].fillna("Unknown")
        df_users.to_csv(os.path.join(CLEANED_DIR, "users_scd_clean.csv"), index=False)
        print(f"Cleaned users_scd saved ({len(df_users)} rows)")
        
    # 2. Restaurants SCD
    rest_path = os.path.join(PROVIDED_DIR, "restaurants_scd.csv")
    if os.path.exists(rest_path):
        df_rest = pd.read_csv(rest_path)
        df_rest = standardize_strings(df_rest)
        df_rest = df_rest.drop_duplicates()
        df_rest["cuisine"] = df_rest["cuisine"].fillna("Multi-Cuisine")
        df_rest["rating"] = pd.to_numeric(df_rest["rating"], errors="coerce").fillna(4.0).clip(1.0, 5.0)
        df_rest.to_csv(os.path.join(CLEANED_DIR, "restaurants_scd_clean.csv"), index=False)
        print(f"Cleaned restaurants_scd saved ({len(df_rest)} rows)")
        
    # 3. Orders CDC
    cdc_path = os.path.join(PROVIDED_DIR, "orders_cdc.csv")
    if os.path.exists(cdc_path):
        df_cdc = pd.read_csv(cdc_path)
        df_cdc = standardize_strings(df_cdc)
        df_cdc["updated_at"] = pd.to_datetime(df_cdc["updated_at"], errors="coerce")
        df_cdc = df_cdc.sort_values(by=["order_id", "updated_at"], ascending=[True, True])
        df_cdc.to_csv(os.path.join(CLEANED_DIR, "orders_cdc_clean.csv"), index=False)
        print(f"Cleaned orders_cdc saved ({len(df_cdc)} rows)")

def main():
    print("=== STARTING DATA CLEANING & VALIDATION ===")
    cust_df = clean_customers()
    prod_df = clean_products()
    ord_df = clean_orders(cust_df, prod_df)
    clean_order_items(ord_df, prod_df)
    clean_provided_datasets()
    print("=== DATA CLEANING COMPLETE ===")

if __name__ == "__main__":
    main()
