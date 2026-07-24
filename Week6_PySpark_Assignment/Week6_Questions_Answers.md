# Week 6 PySpark & Spark Architecture - Solutions

This file contains solutions for all 15 questions from the Week 6 assignment PDF.

---

### Q1: Explain the roles of the Driver, Cluster Manager, and Executor in a Spark application.

**Answer:**

Apache Spark operates on a master-worker architecture where tasks are distributed across multiple nodes. The three core components are:

1. **Driver**:
   - The Driver is the main process that runs the user's `main()` function and initializes the `SparkSession` or `SparkContext`.
   - It converts the user's PySpark/Scala code into a logical plan, optimizes it using the Catalyst Optimizer, and converts it into a Directed Acyclic Graph (DAG) of physical execution stages and tasks.
   - It schedules tasks and coordinates with worker nodes to track execution progress.

2. **Cluster Manager**:
   - The resource manager responsible for allocating physical resources (CPU cores and RAM memory) across the cluster.
   - Spark supports various cluster managers like **YARN**, **Kubernetes**, **Mesos**, or Spark's built-in **Standalone** cluster manager.
   - The Driver requests worker containers/executors from the Cluster Manager.

3. **Executor**:
   - Worker processes running on individual worker nodes in the cluster.
   - Executors receive tasks from the Driver, execute data processing in parallel threads, and store computed data in memory or disk.
   - Once work is complete, executors return task results and status back to the Driver.

---

### Q2: How does Spark's Lazy Evaluation strategy improve performance when chain-processing large datasets?

**Answer:**

In Spark, **Lazy Evaluation** means that transformations (like `map()`, `filter()`, `select()`, `withColumn()`) are not executed immediately when you write them. Instead, Spark simply records them in a logical execution plan called the DAG (Lineage Graph).

Physical execution is only triggered when an **Action** (such as `.show()`, `.count()`, `.collect()`, or `.write`) is called.

#### How it improves performance:
1. **Catalyst Optimization**: Because Spark sees the entire chain of transformations before running anything, the Catalyst Optimizer can optimize the logical plan. For example, it can combine multiple filters into a single condition or drop unused columns (Projection Pushdown).
2. **Avoiding Redundant Computation**: If you chain 10 complex transformations on a 1 Terabyte dataset but only call `.show(5)`, Spark optimizes the read operation so it processes only enough rows to display 5 records, saving massive disk I/O and memory.
3. **Pushed Down Filters**: Spark can push filter conditions directly down to the file storage format (like Parquet), skipping unneeded files/blocks altogether.

---

### Q3: Write a Spark command to read a CSV file located at "data/source.csv", ensuring the first row is treated as a header and inferSchema is enabled.

**Answer:**

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("ReadCSVExample").getOrCreate()

# Reading CSV file with header and inferSchema enabled
df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv("data/source.csv")
)

df.show(5)
```

---

### Q4: What is the difference between CSV and Parquet in terms of storage (row-based vs. columnar) and why does it matter for performance?

**Answer:**

#### CSV (Row-Based Format)
- **Structure**: Data is stored row by row as plain uncompressed or compressed text.
- **Reading Data**: If a query only needs 2 columns out of 50, Spark still has to read and parse the entire file line by line across all 50 columns.
- **Schema**: CSV files do not store schema or data types natively; everything is plain text.

#### Parquet (Columnar Format)
- **Structure**: Data is stored column by column in binary format.
- **Reading Data**: If a query only needs 2 columns, Spark reads *only* the specific byte streams for those 2 columns and completely skips the remaining 48 columns (Column Projection).
- **Compression & Schema**: Similar data types stored sequentially in a single column allow for much higher compression ratios (Snappy/GZIP). Schema metadata and data types are embedded directly inside the file header/footer.

#### Performance Impact:
Parquet drastically reduces disk I/O, network bandwidth, and memory consumption compared to CSV when querying large datasets.

---

### Q5: Given a DataFrame df, write a query to select the columns product_id and price where the category is 'Electronics'.

**Answer:**

```python
from pyspark.sql import functions as F

# Filtering category and selecting columns
electronics_df = (
    df
    .filter(F.col("category") == "Electronics")
    .select("product_id", "price")
)

electronics_df.show()
```

---

### Q6: Write the code to "revise" a DataFrame by renaming the column old_name to new_name and casting the price column from a String to a Double.

**Answer:**

```python
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType

# Renaming column and casting price from String to Double
revised_df = (
    df
    .withColumnRenamed("old_name", "new_name")
    .withColumn("price", F.col("price").cast(DoubleType()))
)

revised_df.printSchema()
```

---

### Q7: How does Spark use the Lineage Graph (DAG) to provide fault tolerance if a worker node fails?

**Answer:**

Instead of writing intermediate data partitions to disk after every transformation (which was a major bottleneck in older frameworks like MapReduce), Spark uses the **Lineage Graph (DAG)**:

1. Every DataFrame/RDD maintains a graph of dependencies that records the exact sequence of transformations used to create it from the raw source file.
2. If a worker node crashes mid-job and loses a partition of data stored in its memory, Spark does **not** restart the whole application.
3. Instead, the Driver inspects the Lineage Graph for that specific lost partition and re-executes only the required parent transformations on another healthy worker node to rebuild just the missing partition.

---

### Q8: Write a query to filter a DataFrame df_orders for rows where the status is 'Completed' AND the amount is greater than 1000.

**Answer:**

```python
from pyspark.sql import functions as F

# Filtering with boolean AND (&) condition
filtered_orders = df_orders.filter(
    (F.col("status") == "Completed") & (F.col("amount") > 1000)
)

filtered_orders.show()
```

---

### Q9: Explain the concept of Predicate Pushdown in Parquet and how it affects the amount of data loaded into memory.

**Answer:**

**Predicate Pushdown** means pushing the filtering evaluation (`WHERE` / `filter` clause) down to the file storage layer so non-matching data is filtered out before it gets loaded into Spark Executor memory.

#### How it works in Parquet:
- Parquet divides files into **Row Groups** (blocks of rows).
- Each Row Group header stores min/max statistics for every column inside that group.
- When Spark executes a query like `.filter(col("amount") > 1000)`, the Parquet reader inspects the min/max statistics of each Row Group:
  - If a Row Group's `max(amount)` is `800`, the reader skips reading that entire Row Group from disk completely.

#### Impact on Memory:
- Disk I/O is reduced significantly.
- RAM usage is minimized because unneeded rows are never converted into Java objects or stored in memory.

---

### Q10: Write a code snippet to add a new column final_price which is the base_price multiplied by 1.18 (18% tax).

**Answer:**

```python
from pyspark.sql import functions as F

# Adding calculated final_price column
updated_df = df.withColumn(
    "final_price",
    F.round(F.col("base_price") * 1.18, 2)
)

updated_df.select("base_price", "final_price").show()
```

---

### Q11: What is the difference between Transformations and Actions? Provide two examples of each.

**Answer:**

| Feature | Transformations | Actions |
| :--- | :--- | :--- |
| **Execution** | Lazy. Does not trigger execution; only builds the logical plan (DAG). | Eager. Triggers physical job execution across executors. |
| **Return Type** | Returns a new `DataFrame` or `RDD`. | Returns a non-DataFrame result (a value, a list, or writes output to storage). |

#### Examples:
- **Transformations**:
  1. `.filter(F.col("status") == "Completed")`
  2. `.withColumn("tax", F.col("amount") * 0.18)`
- **Actions**:
  1. `.count()` (returns integer total rows)
  2. `.write.csv("output/path")` (saves file to disk)

---

### Q12: Write the Spark command to load a Parquet file from "path/to/input", filter out any rows where user_id is null, and save the result as a CSV at "path/to/output".

**Answer:**

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.appName("ETLPipeline").getOrCreate()

# Load Parquet -> Filter null user_id -> Write CSV
(
    spark.read.parquet("path/to/input")
    .filter(F.col("user_id").isNotNull())
    .write.mode("overwrite")
    .option("header", "true")
    .csv("path/to/output")
)
```

---

### Q13: In Spark Architecture, what is the difference between Client Mode and Cluster Mode?

**Answer:**

The difference lies in **where the Driver process runs**:

1. **Client Mode**:
   - The Driver process runs directly on the client machine where `spark-submit` was launched.
   - **Use Case**: Interactive exploration, REPLs, Jupyter notebooks, local development and testing.
   - **Drawback**: High network latency because the Driver must communicate back and forth with Executors in the cluster over the network. If the local machine disconnects, the job dies.

2. **Cluster Mode**:
   - The Driver process runs inside an Executor container on one of the worker nodes inside the cluster managed by YARN/Kubernetes.
   - **Use Case**: Production scheduled batch jobs (e.g. Airflow pipelines).
   - **Advantage**: Low network latency (Driver is co-located on the cluster network). The user can safely log off after submitting the job and it will continue running.

---

### Q14: Write a query to filter a dataset for rows where the region is 'North' OR the priority is 'High'.

**Answer:**

```python
from pyspark.sql import functions as F

# Filtering with logical OR (|) condition
filtered_df = df.filter(
    (F.col("region") == "North") | (F.col("priority") == "High")
)

filtered_df.show()
```

---

### Q15: When exploring a dataset, why is it safer to use .show(5) instead of .collect() on a multi-terabyte dataset?

**Answer:**

#### Why `.collect()` is dangerous:
- `.collect()` retrieves **ALL rows from every partition** across all worker nodes and attempts to load them into the Driver node's single JVM heap memory.
- If you run `.collect()` on a multi-terabyte dataset, the data size will far exceed the Driver's available memory, causing an immediate `java.lang.OutOfMemoryError` (Driver OOM crash) and crashing the application.

#### Why `.show(5)` is safe:
- `.show(5)` implicitly applies a `.limit(5)` transformation.
- Spark's optimizer reads only enough rows from the first partition to return 5 records, transferring just those 5 rows to the Driver process. The Driver memory footprint remains minimal regardless of how large the total dataset is.
