"""
03_dataframe_transformations.py

Demonstrates essential PySpark DataFrame transformations:
1. Q5: Selecting product_id and price where category == 'Electronics'.
2. Q6: Renaming column (old_name -> new_name) & casting price (String -> Double).
3. Q8: Filtering orders (status == 'Completed' AND amount > 1000).
4. Q10: Adding calculated column final_price (base_price * 1.18).
5. Q14: Logical OR filtering (region == 'North' OR priority == 'High').

Author: Week 6 PySpark Exploration
"""

import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType


def main():
    print("=" * 70)
    print(" PYSPARK DATAFRAME TRANSFORMATIONS & QUERY DEMO ")
    print("=" * 70)

    spark = (
        SparkSession.builder.appName("DataFrameTransformations")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    products_path = os.path.join(base_dir, "data", "products.csv")
    orders_path = os.path.join(base_dir, "data", "orders.csv")

    # Load initial DataFrames
    df_products = spark.read.option("header", "true").csv(products_path)
    df_orders = spark.read.option("header", "true").option("inferSchema", "true").csv(orders_path)

    # ----------------------------------------------------
    # Q5: Select product_id and price where category is 'Electronics'
    # ----------------------------------------------------
    print("\n[1] Q5 Solution: Select product_id & price where category = 'Electronics'")
    q5_df = df_products.filter(F.col("category") == "Electronics").select("product_id", "price")
    q5_df.show(truncate=False)

    # ----------------------------------------------------
    # Q6: Rename column 'old_name' -> 'new_name' and cast 'price' String -> Double
    # ----------------------------------------------------
    print("\n[2] Q6 Solution: Rename old_name -> new_name & Cast price String -> Double")
    print("--- Original Schema (price as String) ---")
    df_products.printSchema()

    q6_df = (
        df_products
        .withColumnRenamed("old_name", "new_name")
        .withColumn("price", F.col("price").cast(DoubleType()))
    )

    print("--- Revised Schema (price as Double) ---")
    q6_df.printSchema()
    q6_df.show(truncate=False)

    # ----------------------------------------------------
    # Q8: Filter df_orders where status == 'Completed' AND amount > 1000
    # ----------------------------------------------------
    print("\n[3] Q8 Solution: Filter orders (status = 'Completed' AND amount > 1000)")
    q8_df = df_orders.filter(
        (F.col("status") == "Completed") & (F.col("amount") > 1000)
    )
    q8_df.show(truncate=False)

    # ----------------------------------------------------
    # Q10: Add column final_price = base_price * 1.18 (18% tax)
    # ----------------------------------------------------
    print("\n[4] Q10 Solution: Add final_price column (base_price * 1.18)")
    # Ensure base_price is Double for arithmetic
    df_products_base = df_products.withColumn("base_price", F.col("base_price").cast("double"))
    q10_df = df_products_base.withColumn(
        "final_price", F.round(F.col("base_price") * 1.18, 2)
    )
    q10_df.select("product_id", "old_name", "base_price", "final_price").show(truncate=False)

    # ----------------------------------------------------
    # Q14: Filter for region == 'North' OR priority == 'High'
    # ----------------------------------------------------
    print("\n[5] Q14 Solution: Filter dataset for region = 'North' OR priority = 'High'")
    q14_df = df_orders.filter(
        (F.col("region") == "North") | (F.col("priority") == "High")
    )
    q14_df.show(truncate=False)

    spark.stop()
    print("\n[+] SparkSession stopped. All transformations executed successfully.")


if __name__ == "__main__":
    main()
