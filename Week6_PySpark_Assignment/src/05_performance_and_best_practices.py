"""
05_performance_and_best_practices.py

Demonstrates performance optimization techniques and Spark best practices:
1. Q15: Why .show(5) is safer than .collect() on large datasets (Driver OOM prevention).
2. Q9: Predicate Pushdown in Parquet (pruning row groups before loading to memory).
3. Wide vs. Narrow Transformations (Narrow = local partition, Wide = Shuffle).
4. Memory optimization guidelines for PySpark workflows.

Author: Week 6 PySpark Exploration
"""

import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def main():
    print("=" * 70)
    print(" PYSPARK PERFORMANCE & BEST PRACTICES DEMONSTRATION ")
    print("=" * 70)

    spark = (
        SparkSession.builder.appName("PerformanceAndBestPractices")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    orders_csv = os.path.join(base_dir, "data", "orders.csv")
    parquet_dir = os.path.join(base_dir, "output", "orders_partitioned.parquet")

    # Load data
    df = spark.read.option("header", "true").option("inferSchema", "true").csv(orders_csv)

    # ----------------------------------------------------
    # Q15: Demonstration of .show(5) vs .collect() Safety
    # ----------------------------------------------------
    print("\n[1] Q15 Demonstration: .show(5) vs .collect()")
    print("    -> .show(5) triggers a Limit scan and brings ONLY 5 rows to the Driver process memory.")
    print("    -> .collect() pulls the ENTIRE dataset from all Executor nodes into the Driver JVM heap memory.")
    print("    -> On multi-terabyte datasets, .collect() causes java.lang.OutOfMemoryError (Driver OOM crash)!\n")

    print("--- Safe inspection with .show(5) ---")
    df.show(5, truncate=False)

    print("--- Driver Memory Footprint Check ---")
    # Take safe preview rows without collecting all partitions
    preview_rows = df.limit(5).collect()
    print(f"    Fetched preview row count: {len(preview_rows)} (Safe bound for Driver memory)")

    # ----------------------------------------------------
    # Q9: Predicate Pushdown Demonstration
    # ----------------------------------------------------
    print("\n[2] Q9 Demonstration: Predicate Pushdown in Parquet")
    
    # Save orders DataFrame as Parquet
    df.write.mode("overwrite").parquet(parquet_dir)

    print("    Reading from Parquet with filter condition (status = 'Completed')...")
    parquet_df = spark.read.parquet(parquet_dir).filter(F.col("status") == "Completed")

    print("\n--- Physical Plan showing PushedFilters ---")
    # In the physical plan below, look for PushedFilters: [IsNotNull(status), EqualTo(status,Completed)]
    parquet_df.explain()

    print("\n    -> Explanation: Spark pushes the filter condition directly down to the Parquet file reader.")
    print("    -> Parquet reader inspects block statistics (min/max metadata per Row Group).")
    print("    -> Row Groups that do not match 'Completed' are SKIPPED at storage level, avoiding disk read & memory allocation.")

    # ----------------------------------------------------
    # Transformations Performance: Narrow vs. Wide
    # ----------------------------------------------------
    print("\n[3] Narrow vs. Wide Transformation Analysis")
    
    # Narrow Transformation (No Shuffle): map, filter, select, withColumn
    print("    a) Narrow Transformation (filter & withColumn):")
    narrow_df = df.filter(F.col("amount") > 1000).withColumn("amount_usd", F.col("amount"))
    print("       Partition count unchanged across workers.")

    # Wide Transformation (Shuffle required): groupBy, join, repartition, distinct
    print("    b) Wide Transformation (groupBy status & calculate sum(amount)):")
    wide_df = df.groupBy("status").agg(F.sum("amount").alias("total_amount"))
    wide_df.show(truncate=False)

    print("--- Physical Plan for Wide Transformation (Notice Exchange / HashAggregate) ---")
    wide_df.explain()

    spark.stop()
    print("\n[+] Performance demonstration finished successfully.")


if __name__ == "__main__":
    main()
