"""
04_null_handling_and_pipeline.py

Demonstrates null value handling and complete end-to-end ETL PySpark pipelines:
1. Q12 Solution: Loading Parquet, filtering non-null user_id, and saving to CSV.
2. Complete pipeline construction (read -> transform -> filter -> write).
3. Null checking & data quality validation in PySpark.

Author: Week 6 PySpark Exploration
"""

import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def run_q12_command(spark: SparkSession, input_parquet_path: str, output_csv_path: str):
    """
    Direct implementation of Q12 requirements:
    "Write the Spark command to load a Parquet file from 'path/to/input', 
     filter out any rows where user_id is null, and save the result as a CSV at 'path/to/output'."
    """
    print(f"\n[+] Executing Q12 Pipeline:")
    print(f"    Reading Parquet from : {input_parquet_path}")
    print(f"    Writing CSV to       : {output_csv_path}")

    (
        spark.read.parquet(input_parquet_path)
        .filter(F.col("user_id").isNotNull())
        .write.mode("overwrite")
        .option("header", "true")
        .csv(output_csv_path)
    )
    print("    -> Q12 Pipeline completed successfully!")


def main():
    print("=" * 70)
    print(" NULL HANDLING & END-TO-END DATA PIPELINE DEMO ")
    print("=" * 70)

    spark = (
        SparkSession.builder.appName("NullHandlingAndPipeline")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    orders_csv_path = os.path.join(base_dir, "data", "orders.csv")
    temp_parquet_dir = os.path.join(base_dir, "output", "temp_orders.parquet")
    output_csv_dir = os.path.join(base_dir, "output", "clean_orders_q12.csv")

    # Step A: Setup test Parquet input file (from orders.csv which contains null user_ids)
    print("\n[1] Preparing initial input Parquet dataset with null user_ids...")
    df_raw = spark.read.option("header", "true").option("inferSchema", "true").csv(orders_csv_path)
    df_raw.write.mode("overwrite").parquet(temp_parquet_dir)

    # Display original records including null user_ids
    print("\n--- Original Orders Data (Notice Nulls in user_id) ---")
    df_raw.select("order_id", "user_id", "status", "amount").show(10, truncate=False)

    # Count null user_ids
    null_count = df_raw.filter(F.col("user_id").isNull()).count()
    print(f"[!] Total rows with NULL user_id: {null_count}")

    # Step B: Run Q12 pipeline execution
    run_q12_command(spark, temp_parquet_dir, output_csv_dir)

    # Step C: Read back written CSV to verify null user_ids were removed
    print("\n[2] Verifying Output CSV Data (Filtered user_id IS NOT NULL)...")
    cleaned_df = spark.read.option("header", "true").csv(output_csv_dir)
    cleaned_df.select("order_id", "user_id", "status", "amount").show(10, truncate=False)

    remaining_nulls = cleaned_df.filter(F.col("user_id").isNull()).count()
    print(f"[+] Verification result: Remaining NULL user_id rows = {remaining_nulls}")

    spark.stop()
    print("\n[+] SparkSession terminated.")


if __name__ == "__main__":
    main()
