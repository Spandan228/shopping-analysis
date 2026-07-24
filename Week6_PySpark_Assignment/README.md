# Apache Spark Architecture & Data Processing (Week 6)

A production-grade PySpark project demonstrating Apache Spark core architecture, execution engine mechanics, lazy evaluation, Catalyst optimization, schema handling, file I/O (CSV vs. Parquet), and DataFrame transformations.

---

## Repository Structure

```
Week6_PySpark_Assignment/
├── README.md                           # Master project documentation
├── Week6_Questions_Answers.md          # Comprehensive solutions to Week 6 assignment Q1-Q15
├── data/                               # Input sample datasets
│   ├── source.csv                      # Employee raw dataset (50,000 rows)
│   ├── orders.csv                      # E-commerce orders dataset (100,000 rows with nulls)
│   └── products.csv                    # Product catalog dataset (50,000 rows)
└── src/                                # Modular PySpark scripts
    ├── 01_spark_architecture_demo.py   # Driver/Executors, Lazy Evaluation, DAG Lineage inspection
    ├── 02_schema_and_io_operations.py  # inferSchema vs StructType, CSV & Parquet I/O
    ├── 03_dataframe_transformations.py # Rename, cast, tax calculation, multi-condition filter
    ├── 04_null_handling_and_pipeline.py# Null filtering and complete read -> transform -> write pipeline
    └── 05_performance_and_best_practices.py # .show(5) vs .collect(), Predicate Pushdown, Shuffle analysis
```

---

## Prerequisites & Installation

### Environment Requirements
- **Python**: `3.11+`
- **Java**: `OpenJDK 17` or `Java 11+`
- **PySpark**: `4.2.0`

---

## How to Run the Scripts

Each script under `src/` is self-contained and can be executed independently from the project root:

### 1. Spark Architecture & Lazy Evaluation
Demonstrates `SparkSession` setup, DAG execution plan building, and lineage graph inspection via `.explain()` and `.toDebugString()`.
```bash
python src/01_spark_architecture_demo.py
```

### 2. Schema Handling & File I/O
Demonstrates reading CSV with `inferSchema=True` versus explicit `StructType` definitions, as well as serializing to Parquet columnar format.
```bash
python src/02_schema_and_io_operations.py
```

### 3. DataFrame Transformations
Executes column selection (`product_id`, `price` for Electronics), renaming (`old_name` -> `new_name`), type casting (`String` -> `Double`), calculated column addition (`final_price = base_price * 1.18`), and complex boolean filtering (`AND`, `OR`).
```bash
python src/03_dataframe_transformations.py
```

### 4. Null Handling & Data Pipelines
Executes a complete ETL pipeline (`read Parquet -> filter non-null user_id -> write CSV`), validating data quality at each step.
```bash
python src/04_null_handling_and_pipeline.py
```

### 5. Performance Optimizations & Best Practices
Demonstrates why `.show(5)` is memory-safe compared to `.collect()`, verifies Predicate Pushdown in physical query plans, and analyzes Narrow vs. Wide transformation shuffles.
```bash
python src/05_performance_and_best_practices.py
```

---

## Key Technical Insights & Architecture Concepts

### 1. Spark Architecture Components
- **Driver**: Central orchestrator that converts code into a Directed Acyclic Graph (DAG) of stages and dispatches tasks.
- **Cluster Manager**: Resource allocator (YARN, Kubernetes, or Standalone) managing worker nodes.
- **Executors**: Worker processes executing data processing tasks in parallel and returning metrics to the Driver.

### 2. Lazy Evaluation & Lineage Graph (DAG)
- Transformations (like `filter`, `select`, `withColumn`) are **lazy** and build a logical plan (DAG).
- Execution is triggered only when an **Action** (like `show()`, `count()`, `write`) is called.
- The Lineage Graph enables **fault tolerance**: if a worker fails, Spark recomputes only the lost data partitions using the DAG lineage.

### 3. CSV vs. Parquet Format Comparison
- **CSV**: Text-based, row-oriented. Requires scanning all columns even when querying a single column.
- **Parquet**: Binary, columnar-oriented. Offers high compression (Snappy/GZIP), column projection skipping, and embedded schema metadata.

### 4. Predicate Pushdown
- Filters (e.g. `status = 'Completed'`) are pushed directly to the Parquet storage reader.
- By inspecting Row Group `min`/`max` metadata, Parquet skips non-matching disk blocks entirely, saving I/O and RAM.

### 5. Memory Safety: `.show(5)` vs `.collect()`
- `.show(5)` fetches only 5 preview rows to the Driver process memory.
- `.collect()` pulls **all** dataset partitions into the Driver JVM heap memory, causing `OutOfMemoryError` (Driver OOM) on multi-terabyte datasets.

---
