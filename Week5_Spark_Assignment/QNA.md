# Week 5 Spark Assignment: Questions and Answers

### Q1: What are the key limitations of traditional MapReduce that make Spark a preferred choice for modern big data processing?
**Answer:**
Traditional MapReduce has several limitations that make Spark a preferred choice:
1. **Disk I/O Bottlenecks:** MapReduce writes intermediate state results to physical disks after each map and reduce step. This makes iterative tasks (like machine learning or multi-stage pipelines) very slow due to excessive disk reads and writes.
2. **High Latency:** Creating new MapReduce tasks and JVMs for every step introduces high orchestration latency.
3. **Complexity & Verbose Code:** MapReduce requires boilerplate Java code even for simple tasks like word counts. Spark provides clean, high-level APIs in Python, Scala, Java, and SQL.
4. **Lack of In-Memory Support:** Spark works primarily in-memory, retaining cached data across transformation stages, which makes it up to 100x faster than MapReduce for iterative workloads.

---

### Q2: Explain how Spark uses In-Memory Computing to speed up iterative machine learning algorithms compared to disk-based systems.
**Answer:**
Iterative machine learning algorithms (e.g., K-means, Logistic Regression, PageRank) apply the same functions repeatedly to the same dataset until convergence. 
* In **disk-based systems** like MapReduce, each iteration is treated as a separate job. The data is loaded from disk, processed, written back to disk, and then re-read in the next iteration.
* In **Spark**, developers can persist or cache intermediate DataFrames or RDDs in the memory (RAM) of execution nodes using `.cache()` or `.persist()`. Subsequent iterations pull the dataset directly from RAM, bypassing expensive serialization and disk I/O, resulting in substantial speedups.

---

### Q3: Write a code snippet to remove all duplicate rows from a DataFrame based on a specific set of columns: `user_id` and `transaction_date`.
**Answer:**
```python
# Drop duplicates based on a subset of columns in PySpark
df_cleaned = df.dropDuplicates(subset=["user_id", "transaction_date"])
```

---

### Q4: Given a DataFrame `df_sales`, write a query to filter for rows where the region is 'West' and then group by `product_category` to find the average `sale_amount`.
**Answer:**
```python
from pyspark.sql.functions import avg, col

df_result = (df_sales
             .filter(col("region") == "West")
             .groupBy("product_category")
             .agg(avg("sale_amount").alias("avg_sale_amount")))
```

---

### Q5: What is the difference between `.na.drop()` and `.na.fill()`? Provide a code example of filling null values in a status column with the string 'Unknown'.
**Answer:**
* **`df.na.drop()`**: Used to remove rows from the DataFrame if they contain null values. You can configure it to drop rows containing any nulls, all nulls, or nulls in specific subset columns.
* **`df.na.fill()`** (or `.fillna()`): Used to replace null values with a specified default value (e.g., a default string, integer, or dictionary mappings).

**Example of filling status column nulls with 'Unknown':**
```python
df_filled = df.na.fill(value="Unknown", subset=["status"])
# Or using dictionary mapping:
# df_filled = df.na.fill({"status": "Unknown"})
```

---

### Q6: Write a query to find the total count of records for each city in a DataFrame, but only for cities where the count is greater than 100.
**Answer:**
```python
from pyspark.sql.functions import col

df_city_counts = (df.groupBy("city")
                  .count()
                  .filter(col("count") > 100))
```

---

### Q7: How does the immutability of Spark DataFrames affect how you perform "data cleaning" steps like dropping columns or renaming them?
**Answer:**
DataFrames in Spark are **immutable**—once created, their schema and contents cannot be modified in-place. 
* When performing cleaning actions (e.g., `df.drop()`, `df.withColumnRenamed()`), Spark does not alter the underlying data.
* Instead, it creates and returns a **new DataFrame** representing the transformed state.
* Under the hood, Spark logs these operations in a **DAG (Directed Acyclic Graph)**. The physical execution is postponed (lazy evaluation) until an action (like `.show()` or `.write`) is called, allowing Spark's Catalyst Optimizer to simplify and optimize the execution plan.

---

### Q8: Write a Spark command to filter a dataset for rows where the age is between 18 and 30 (inclusive) and the subscription is 'Premium'.
**Answer:**
```python
from pyspark.sql.functions import col

df_filtered = df.filter(
    (col("age") >= 18) & 
    (col("age") <= 30) & 
    (col("subscription") == "Premium")
)
# Alternative using between():
# df_filtered = df.filter(col("age").between(18, 30) & (col("subscription") == "Premium"))
```

---

### Q9: When cleaning a dataset, why is it often better to handle null values before performing mathematical aggregations like `sum()` or `avg()`?
**Answer:**
1. **Preventing Skewed Averages:** Spark's aggregate functions automatically ignore null values. For `avg()`, the sum is divided only by the count of non-null entries. If many nulls exist, it might skew the result away from the actual business population average.
2. **Explicit Business Logic:** Null values can represent zeros, defaults, or missing logs. Imputing them (e.g., filling price with `0`) ensures that the statistics reflect true business metrics (like dividing total revenue by *all* transactions, not just the non-null ones).
3. **Avoiding Execution Side-Effects:** Mathematical operations involving nulls can return unexpected outputs or propagate nulls in subsequent join/transformation operations.

---

### Q10: Write the code to revise a column named `raw_timestamp` by casting it to a `TimestampType` and renaming it to `event_time`.
**Answer:**
```python
from pyspark.sql.functions import col
from pyspark.sql.types import TimestampType

df_updated = (df
              .withColumn("raw_timestamp", col("raw_timestamp").cast(TimestampType()))
              .withColumnRenamed("raw_timestamp", "event_time"))
```

---

### Q11: Explain the "Shuffle" process that occurs during a grouping operation. Why is it considered a wide transformation?
**Answer:**
* **The Shuffle Process:** In Spark, data is distributed across multiple partitions on different worker nodes. When grouping data (e.g., `groupBy("city")`), rows with the same key (e.g., `"New York"`) might be scattered across different partitions. Spark must redistribute, copy, and group these records across executors so that all records of the same key end up on the same partition. This network redistribution is the shuffle process.
* **Wide Transformation:** Grouping is a wide transformation because it has a **many-to-many** partition dependency (each output partition depends on data from multiple input partitions). Shuffles require disk writing, network transit, and CPU serialization, making them expensive operations that should be minimized.

---

### Q12: Write a code snippet that identifies and removes rows where the `email` column contains null values OR the `username` is an empty string.
**Answer:**
```python
from pyspark.sql.functions import col

df_cleaned = df.filter(col("email").isNotNull() & (col("username") != ""))
```

---

### Q13: How do you use the `.agg()` function to calculate multiple statistics at once, such as the min, max, and mean of the `price` column?
**Answer:**
```python
from pyspark.sql.functions import min, max, mean

df_stats = df.agg(
    min("price").alias("min_price"),
    max("price").alias("max_price"),
    mean("price").alias("mean_price")
)
```

---

### Q14: In the context of cleaning a dataset, what is the risk of using `inferSchema=true` when your source data contains messy or inconsistent date formats?
**Answer:**
Using `inferSchema=true` on messy date formats presents several risks:
1. **Fallback to String:** If formats are inconsistent (e.g., some are `2026-07-18`, others are `18/07/2026` or contain `"N/A"` text), Spark will fail to detect a uniform date pattern and infer the column as `StringType`, preventing date-based functions from working.
2. **Incorrect Parse Rules:** Spark might misinterpret values (e.g., parsing `02/03/2026` as Feb 3rd under US locale instead of March 2nd under UK locale).
3. **Silent Null Conversions:** Spark might parse some matches but silently convert non-conforming rows to `null`, leading to data loss without throwing errors.
*Best practice is to load columns as strings and parse them explicitly using `to_timestamp()` or `to_date()` with exact formats.*

---

### Q15: Write a final processing pipeline that: 
1. Filters out duplicates. 
2. Fills null prices with 0. 
3. Groups by `store_id` to calculate total revenue.
**Answer:**
```python
from pyspark.sql.functions import col, sum

df_pipeline = (df
               .dropDuplicates()                   # 1. Filter out duplicates
               .fillna({"price": 0})               # 2. Fill null prices with 0
               .groupBy("store_id")                # 3. Group by store_id
               .agg(sum("price").alias("total_revenue"))) # Calculate revenue
```
