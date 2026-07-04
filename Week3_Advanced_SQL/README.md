# SQL Advanced Analytics - Superstore Dataset

This repository contains SQL schemas, normalized tables, and advanced analytical queries using Subqueries, Common Table Expressions (CTEs), and Window Functions on the Sample Superstore retail sales dataset.

## Project Structure

```
Week3_Advanced_SQL/
├── Dataset/
│   └── Sample - Superstore.csv  # Raw sales transactions data
├── queries.sql                   # Standalone, well-formatted SQL script containing all queries
├── results.txt                   # Raw execution output text of all SQL queries
├── insights.md                   # Full analysis report, schemas, and answers to the mini-project
└── README.md                     # Repository documentation (this file)
```

## Setup & Execution Instructions

The database setup and analytical queries can be executed in any standard relational database environment (such as SQLite, PostgreSQL, or MySQL):

1. **Load Raw Data**: Import the transactional records from `Dataset/Sample - Superstore.csv` into a staging table named `superstore_raw`.
2. **Schema Creation & Normalization**: Run the queries in the DDL section of `queries.sql` to initialize the `customers`, `products`, and `orders` tables and populate them using `SELECT DISTINCT`.
3. **Execution**: Execute the remaining analytical queries in `queries.sql` to generate sales insights. Output matches the reports saved in `results.txt`.

## Summary of Analytical Concepts Implemented

1. **Staging & Relational Normalization**: Standardized raw headers to snake_case and converted MM/DD/YYYY date formats to ISO format. Normalized the staging table using distinct queries into:
   - `customers` (customer ID, name, segment)
   - `products` (product ID, name, category, sub-category)
   - `orders` (transaction logs linked to customer IDs)
2. **Subqueries**: Used to extract line items exceeding average value, and for correlated queries to find the max order per customer.
3. **Common Table Expressions (CTEs)**: Used to aggregate customer metrics (total sales, averages) to simplify main query logic.
4. **Window Functions**: Applied `RANK()` and `ROW_NUMBER() OVER (PARTITION BY ...)` for customer ranking and chronological sequencing of orders.
