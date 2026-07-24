"""
01_spark_architecture_demo.py

Demonstrates core Apache Spark architecture concepts:
1. SparkSession initialization (Driver process setup).
2. Lazy Evaluation mechanism (Transformations vs. Execution trigger).
3. DAG (Directed Acyclic Graph) Lineage Graph inspection via explain() and RDD debug strings.

Author: Week 6 PySpark Exploration
"""

import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def main():
    print("=" * 70)
    print(" SPARK ARCHITECTURE & LAZY EVALUATION DEMONSTRATION ")
    print("=" * 70)

    # 1. Initialize SparkSession (Driver Process)
    # The SparkSession is the primary entry point to Spark functionality.
    # It communicates with the Cluster Manager (standalone/YARN/Mesos/K8s) to allocate Executors.
    spark = (
        SparkSession.builder.appName("SparkArchitectureDemo")
        .master("local[*]")  # Uses all available logical CPU cores on local machine
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    print(f"\n[+] Spark Application ID : {spark.sparkContext.applicationId}")
    print(f"[+] Spark Version        : {spark.version}")
    print(f"[+] Master Node          : {spark.sparkContext.master}\n")

    # Path to sample orders dataset
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "orders.csv")

    # 2. Demonstrating Lazy Evaluation & Lineage Graph (DAG)
    print("[1] Building Transformation Pipeline (No physical execution occurs yet)...")
    
    # Transformation 1: Read CSV (Lazy schema evaluation if no action is triggered)
    raw_df = spark.read.option("header", "true").option("inferSchema", "true").csv(data_path)
    
    # Transformation 2: Filtering completed orders
    completed_orders = raw_df.filter(F.col("status") == "Completed")
    
    # Transformation 3: Filtering high value orders (> 1000)
    high_val_orders = completed_orders.filter(F.col("amount") > 1000)
    
    # Transformation 4: Adding calculated tax column
    tax_df = high_val_orders.withColumn("tax_amount", F.round(F.col("amount") * 0.18, 2))

    print("    -> Transformations chained successfully. DataFrame schema defined.")
    print("    -> Spark has built the Execution Plan (DAG) but zero disk/memory reads occurred so far!\n")

    # 3. Inspecting the Physical and Logical Query Plans (Catalyst Optimizer DAG)
    print("[2] Catalyst Optimizer Execution Plan (.explain()):")
    print("-" * 50)
    tax_df.explain(True)
    print("-" * 50)

    # 4. RDD Lineage Graph Inspection
    print("\n[3] RDD Lineage Graph (.toDebugString()):")
    print("-" * 50)
    rdd_lineage = tax_df.rdd.toDebugString().decode("utf-8")
    print(rdd_lineage)
    print("-" * 50)

    # 5. Triggering Action (Forces execution across Executors)
    print("\n[4] Triggering Action (.show()): Execution begins NOW!")
    tax_df.show(5, truncate=False)

    total_count = tax_df.count()
    print(f"[+] Action complete! Filtered dataset count: {total_count} rows.\n")

    spark.stop()
    print("[+] SparkSession terminated gracefully.")


if __name__ == "__main__":
    main()
