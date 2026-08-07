# E-Commerce Order Analytics System

A production-ready data engineering and analytics platform combining **Python, Pandas, and SQL (SQLite)** — from synthetic dataset generation with anomaly injection to data cleaning, relational schema creation, cohort retention analysis, RFM segmentation, and CLI reporting.

---

## ⚡ Quick Start Guide (How Anyone Can Run This Repo)

If you have just cloned this repository from GitHub, follow these simple steps to run the entire pipeline from scratch:

```bash
# 1. Clone the repository and navigate into the project directory
git clone https://github.com/YourUsername/ecommerce-analytics-system.git
cd ecommerce-analytics-system

# 2. Install dependencies (Pandas, Faker, Tabulate)
pip install -r requirements.txt

# 3. Run the 3 core commands in sequence:

# Step A: Generate raw datasets with real-world anomalies
python scripts/generate_data.py

# Step B: Clean datasets and validate referential integrity
python scripts/clean_data.py

# Step C: Run dynamic CLI reporting queries (auto-initializes SQL DB)
python scripts/report_cli.py --report revenue
```

---

## 📁 Repository Directory Layout

```
ecommerce-analytics-system/
│── data/
│   ├── raw/                          <-- Step 1: Raw CSV Datasets
│   │   ├── customers.csv
│   │   ├── products.csv
│   │   ├── orders.csv
│   │   └── order_items.csv
│   └── cleaned/                      <-- Step 2: Cleaned CSV Datasets
│       ├── customers_clean.csv
│       ├── products_clean.csv
│       ├── orders_clean.csv
│       └── order_items_clean.csv
│── scripts/
│   ├── generate_data.py              <-- Step 1: Data Generator with Anomalies
│   ├── clean_data.py                 <-- Step 2: Pandas Cleaner & Referential Integrity
│   └── report_cli.py                 <-- Step 8 & 9: Production CLI Reporting Tool
│── sql/
│   ├── schema.sql                    <-- Step 3: DDL Constraints & Indexes
│   ├── aggregations.sql              <-- Step 4: Revenue, AOV, Top Products
│   ├── window_functions.sql          <-- Step 5: LTV Ranks, Running Totals, CTEs
│   └── cohort_analysis.sql           <-- Step 6 & 7: Cohort Retention & RFM Segmentation
│── output/
│   └── sample_reports/               <-- Step 10: Generated CSV Reports & Screenshots
│       ├── 01_generate_data.png
│       ├── 02_clean_data.png
│       ├── 03_revenue_report.png
│       ├── 04_top_customers.png
│       ├── 05_cohort_retention.png
│       └── 06_rfm_segmentation.png
│── requirements.txt                  <-- Python Dependencies
└── README.md                         <-- Project Documentation & Quick Start
```

---

## 💻 Interactive CLI Reporting Commands

Anyone inspecting your project can run dynamic reports using `scripts/report_cli.py`:

```bash
# Monthly Revenue & Average Order Value (AOV)
python scripts/report_cli.py --report revenue --limit 10

# Top Customers by Lifetime Value (LTV Rank)
python scripts/report_cli.py --report top_customers --limit 10

# Cohort Retention Matrix (Months 0 - 12)
python scripts/report_cli.py --report retention

# RFM Customer Segmentation (Recency, Frequency, Monetary)
python scripts/report_cli.py --report rfm --limit 10

# Secure Parameterized Filter by City (e.g. Mumbai)
python scripts/report_cli.py --report top_customers --city "Mumbai" --limit 5

# Export ALL reports to CSV files in output/sample_reports/
python scripts/report_cli.py --report all --export
```

---

## 📷 Visual Deliverables & Output Screenshots

All execution screenshots are saved inside [`output/sample_reports/`](file:///c:/Users/Spandan%20Swarup%20Nanda/Desktop/week%208%20celebal/Food%20Delivery%20Analytics/ecommerce-analytics-system/output/sample_reports/):

1. **`01_generate_data.png`**: Raw dataset generation output (1000 customers, 5000 orders, 12000 order items).
2. **`02_clean_data.png`**: Data cleaning and referential integrity validation output.
3. **`03_revenue_report.png`**: Monthly revenue, total orders, and Average Order Value (AOV) CLI table.
4. **`04_top_customers.png`**: Top customers ranked by Lifetime Value (LTV) using `RANK()`.
5. **`05_cohort_retention.png`**: First purchase cohort retention matrix (Months 0–12).
6. **`06_rfm_segmentation.png`**: RFM Customer Segmentation (Champions, Loyal, At Risk).

---

## 📊 SQL Analytics Suite

1. **`sql/schema.sql`**: Relational DDL enforcing PKs, FKs (`ON DELETE CASCADE`), `NOT NULL`, `CHECK` bounds, and B-Tree performance indexes.
2. **`sql/aggregations.sql`**: Revenue per customer, category revenue, monthly revenue trends, Top 10 products, Average Order Value (AOV).
3. **`sql/window_functions.sql`**: LTV ranking using `RANK()` and `DENSE_RANK()`, 7-day moving averages (`AVG() OVER`), running totals (`SUM() OVER`), and MoM growth CTEs.
4. **`sql/cohort_analysis.sql`**: First purchase cohort grouping, monthly retention rates matrix (Months 0–12), churned vs repeat identification (>90 days inactive), and **RFM Customer Segmentation** (`NTILE(4)` scoring).

---

## 🛡️ Edge Case & Security Architecture

- **SQL Injection Prevention**: 100% prepared statements with parameterized tuple bindings (`cursor.execute(query, params)`).
- **Auto Database Loading**: Automatically initializes SQLite database schema and imports cleaned CSVs on first run.
- **Terminal Formatting**: Custom tight ASCII layout prevents text wrapping across narrow terminal windows.
