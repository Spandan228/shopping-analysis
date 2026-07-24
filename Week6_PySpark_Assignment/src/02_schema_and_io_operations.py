"""
02_schema_and_io_operations.py

Demonstrates data ingestion and serialization patterns in PySpark:
1. Reading CSV with inferSchema=True (Q3).
2. Explicit schema enforcement using StructType and StructField.
3. Reading and Writing Parquet vs CSV formats.
4. Schema inspection and data type verification.

Author: Week 6 PySpark Exploration
"""

import os
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    IntegerType,
    StringType,
    DoubleType,
)


def main():
    print("=" * 70)
    print(" SCHEMA HANDLING AND FILE I/O OPERATIONS (CSV & PARQUET) ")
    print("=" * 70)

    spark = (
        SparkSession.builder.appName("SchemaAndIOOperations")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_csv_path = os.path.join(base_dir, "data", "source.csv")
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    # ----------------------------------------------------
    # Q3: Reading CSV with header=true and inferSchema=true
    # ----------------------------------------------------
    print("\n[1] Executing Q3 Solution: Reading CSV with inferSchema=True")
    print(f"    Source path: {source_csv_path}")

    # Spark command to read CSV with header and inferSchema enabled
    df_inferred = (
        spark.read.option("header", "true")
        .option("inferSchema", "true")
        .csv(source_csv_path)
    )

    print("\n--- Inferred Schema ---")
    df_inferred.printSchema()
    print("--- First 5 Records ---")
    df_inferred.show(5, truncate=False)

    # ----------------------------------------------------
    # Best Practice: Reading CSV with Explicit StructType Schema
    # ----------------------------------------------------
    print("\n[2] Explicit Schema Definition (Production Best Practice)")
    # InferSchema scans the entire file once extra; defining schema explicitly avoids extra job overhead.
    explicit_schema = StructType(
        [
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True),
            StructField("age", IntegerType(), True),
            StructField("salary", DoubleType(), True),
            StructField("department", StringType(), True),
            StructField("join_date", StringType(), True),
        ]
    )

    df_explicit = (
        spark.read.option("header", "true")
        .schema(explicit_schema)
        .csv(source_csv_path)
    )

    print("\n--- Explicit Schema ---")
    df_explicit.printSchema()

    # ----------------------------------------------------
    # Writing to Parquet Format & Reading Back
    # ----------------------------------------------------
    parquet_output_path = os.path.join(output_dir, "source_data.parquet")
    print(f"\n[3] Saving DataFrame as Parquet at: {parquet_output_path}")

    df_explicit.write.mode("overwrite").parquet(parquet_output_path)
    print("    -> Successfully serialized data into Parquet columnar format.")

    # Read back from Parquet (Parquet preserves exact datatypes without needing inferSchema)
    print("\n[4] Reading back Parquet file...")
    df_from_parquet = spark.read.parquet(parquet_output_path)
    print("--- Parquet Schema (Preserved without scanning raw text) ---")
    df_from_parquet.printSchema()
    df_from_parquet.show(5, truncate=False)

    spark.stop()
    print("\n[+] Session stopped. Schema and I/O demonstration completed.")


if __name__ == "__main__":
    main()
