"""
Dataset Generator for Food Delivery & E-Commerce Order Analytics System.

Generates synthetic relational datasets with intentional real-world inconsistencies:
- Missing / Null values (null customer names, null emails, null order amounts)
- Duplicate records (duplicate order rows, duplicate user rows)
- Mismatched / Orphan foreign keys (order_items pointing to non-existent orders/products)
- Invalid dates (future timestamps, out-of-sequence order updates)
- Negative / Zero amounts

Uses standard Python libraries for zero external dependency friction.
Saves raw CSV outputs to `data/raw/` directory.
"""

import os
import random
import csv
from datetime import datetime, timedelta
import pandas as pd

# Set seed for reproducibility
random.seed(42)

RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

FIRST_NAMES = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
               "Ananya", "Diya", "Saanvi", "Aadhya", "Pari", "Anika", "Navya", "Angel", "Myra", "Riya"]
LAST_NAMES = ["Sharma", "Verma", "Gupta", "Mehta", "Joshi", "Nair", "Patel", "Reddy", "Rao", "Singh",
              "Kulkarni", "Deshmukh", "Iyer", "Chawla", "Bhat", "Kapoor", "Saxena", "Choudhury", "Das", "Sen"]
DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "techcorp.com", "foodie.io"]

def generate_customers(num_records=1000):
    print(f"Generating {num_records} raw customer records...")
    cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Ahmedabad", "Chennai", "Kolkata", "Pune", "Jaipur"]
    segments = ["Consumer", "Corporate", "Home Office"]
    
    customers = []
    for i in range(1, num_records + 1):
        cust_id = f"CUST{i:04d}"
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        name = f"{fn} {ln}"
        email = f"{fn.lower()}.{ln.lower()}{random.randint(10, 999)}@{random.choice(DOMAINS)}"
        city = random.choice(cities)
        
        days_ago = random.randint(10, 700)
        signup_dt = datetime.now() - timedelta(days=days_ago)
        signup_date = signup_dt.strftime("%Y-%m-%d")
        segment = random.choice(segments)
        
        # Inject nulls
        if random.random() < 0.05:
            name = None
        if random.random() < 0.04:
            email = None
        if random.random() < 0.03:
            city = None
            
        customers.append({
            "customer_id": cust_id,
            "name": name,
            "email": email,
            "city": city,
            "signup_date": signup_date,
            "segment": segment
        })
        
    df = pd.DataFrame(customers)
    
    # Inject exact duplicate rows (2%)
    duplicates = df.sample(frac=0.02, random_state=42)
    df = pd.concat([df, duplicates], ignore_index=True)
    
    # Inject invalid email formats
    invalid_mask = df.sample(frac=0.03, random_state=42).index
    df.loc[invalid_mask, 'email'] = "invalid_email_format_no_at"
    
    return df

def generate_products(num_records=150):
    print(f"Generating {num_records} raw product / restaurant item records...")
    categories = ["North Indian", "South Indian", "Chinese", "Italian", "Fast Food", "Beverages", "Desserts", "Biryani"]
    dish_prefixes = ["Paneer", "Chicken", "Veg", "Butter", "Masala", "Crispy", "Tandoori", "Special", "Royal", "Garlic"]
    dish_suffixes = ["Tikka", "Biryani", "Curry", "Platter", "Roll", "Burger", "Pizza", "Noodles", "Pasta", "Delight"]

    products = []
    for i in range(1, num_records + 1):
        prod_id = f"PROD{i:03d}"
        name = f"{random.choice(dish_prefixes)} {random.choice(dish_suffixes)}"
        category = random.choice(categories)
        unit_price = round(random.uniform(50, 800), 2)
        stock_qty = random.randint(10, 500)
        
        # Inject invalid negative price anomaly
        if random.random() < 0.02:
            unit_price = -round(random.uniform(10, 100), 2)
            
        # Inject null category
        if random.random() < 0.04:
            category = None
            
        products.append({
            "product_id": prod_id,
            "product_name": name,
            "category": category,
            "unit_price": unit_price,
            "stock_quantity": stock_qty
        })
        
    df = pd.DataFrame(products)
    return df

def generate_orders(customers_df, products_df, num_records=5000):
    print(f"Generating {num_records} raw order records...")
    cust_ids = customers_df["customer_id"].dropna().unique().tolist()
    
    orders = []
    statuses = ["Placed", "Preparing", "Out for Delivery", "Delivered", "Cancelled"]
    start_date = datetime(2025, 1, 1)
    
    for i in range(1, num_records + 1):
        order_id = f"ORD{i:05d}"
        # 3% chance of orphaned customer ID
        cust_id = random.choice(cust_ids) if random.random() > 0.03 else "CUST99999"
        
        days_offset = random.randint(0, 500)
        hours_offset = random.randint(0, 23)
        mins_offset = random.randint(0, 59)
        order_dt = start_date + timedelta(days=days_offset, hours=hours_offset, minutes=mins_offset)
        
        # 1% chance of future date error
        if random.random() < 0.01:
            order_dt = datetime.now() + timedelta(days=100)
            
        total_amt = round(random.uniform(100, 2500), 2)
        status = random.choice(statuses)
        
        # Inject missing total amount
        if random.random() < 0.04:
            total_amt = None
            
        orders.append({
            "order_id": order_id,
            "customer_id": cust_id,
            "order_timestamp": order_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "total_amount": total_amt,
            "status": status
        })
        
    df = pd.DataFrame(orders)
    
    # Inject exact duplicates
    duplicates = df.sample(frac=0.03, random_state=42)
    df = pd.concat([df, duplicates], ignore_index=True)
    
    return df

def generate_order_items(orders_df, products_df, num_records=12000):
    print(f"Generating {num_records} raw order item records...")
    order_ids = orders_df["order_id"].dropna().unique().tolist()
    product_ids = products_df["product_id"].dropna().unique().tolist()
    
    items = []
    for i in range(1, num_records + 1):
        item_id = f"ITEM{i:06d}"
        # 2% chance of orphaned order_id
        o_id = random.choice(order_ids) if random.random() > 0.02 else "ORD999999"
        # 2% chance of orphaned product_id
        p_id = random.choice(product_ids) if random.random() > 0.02 else "PROD9999"
        
        quantity = random.randint(1, 6)
        unit_price = round(random.uniform(50, 800), 2)
        subtotal = round(quantity * unit_price, 2)
        
        # Inject zero/negative quantity anomaly
        if random.random() < 0.01:
            quantity = 0
            
        items.append({
            "item_id": item_id,
            "order_id": o_id,
            "product_id": p_id,
            "quantity": quantity,
            "unit_price": unit_price,
            "subtotal": subtotal
        })
        
    df = pd.DataFrame(items)
    return df

def main():
    print("=== STARTING SYNTHETIC DATASET GENERATION ===")
    customers_df = generate_customers(1000)
    products_df = generate_products(150)
    orders_df = generate_orders(customers_df, products_df, 5000)
    order_items_df = generate_order_items(orders_df, products_df, 12000)
    
    customers_path = os.path.join(RAW_DATA_DIR, "customers.csv")
    products_path = os.path.join(RAW_DATA_DIR, "products.csv")
    orders_path = os.path.join(RAW_DATA_DIR, "orders.csv")
    order_items_path = os.path.join(RAW_DATA_DIR, "order_items.csv")
    
    customers_df.to_csv(customers_path, index=False)
    products_df.to_csv(products_path, index=False)
    orders_df.to_csv(orders_path, index=False)
    order_items_df.to_csv(order_items_path, index=False)
    
    print(f"Saved raw datasets to {RAW_DATA_DIR}:")
    print(f"  - customers.csv ({len(customers_df)} rows)")
    print(f"  - products.csv ({len(products_df)} rows)")
    print(f"  - orders.csv ({len(orders_df)} rows)")
    print(f"  - order_items.csv ({len(order_items_df)} rows)")
    print("=== DATASET GENERATION COMPLETE ===")

if __name__ == "__main__":
    main()
