"""
CLI Reporting Tool for Food Delivery & E-Commerce Analytics System.

Usage:
    python scripts/report_cli.py --report revenue
    python scripts/report_cli.py --report top_customers --limit 5
    python scripts/report_cli.py --report retention
    python scripts/report_cli.py --report rfm
    python scripts/report_cli.py --report all --export

Features:
- Dynamically queries SQLite database tables.
- Automatically initializes schema & loads data if missing.
- Formats output with clean, non-wrapping ASCII tables.
- 100% Parameterized queries with zero SQL injection risk.
- Graceful edge-case handling (empty sets, DB errors, invalid parameters).
"""

import sys
import os
import argparse
import sqlite3
import pandas as pd

# Prevent terminal line wrapping
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "db")
DB_PATH = os.path.join(DB_DIR, "food_delivery_analytics.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "sample_reports")
CLEANED_DIR = os.path.join(BASE_DIR, "data", "cleaned")
SCHEMA_PATH = os.path.join(BASE_DIR, "sql", "schema.sql")

BASE_QUERIES = {
    "revenue": """
        SELECT 
            STRFTIME('%Y-%m', order_timestamp) AS month,
            COUNT(order_id) AS orders,
            COUNT(DISTINCT customer_id) AS customers,
            ROUND(SUM(total_amount), 2) AS revenue,
            ROUND(AVG(total_amount), 2) AS aov
        FROM orders
        WHERE status != 'Cancelled'
        GROUP BY STRFTIME('%Y-%m', order_timestamp)
        ORDER BY month DESC
    """,
    "top_customers": """
        SELECT 
            c.customer_id AS cust_id,
            c.name AS customer_name,
            c.city,
            c.segment,
            COUNT(o.order_id) AS orders,
            ROUND(SUM(o.total_amount), 2) AS spend,
            RANK() OVER (ORDER BY SUM(o.total_amount) DESC) AS ltv_rank
        FROM customers c
        INNER JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.status != 'Cancelled'
        {WHERE_CLAUSE}
        GROUP BY c.customer_id, c.name, c.city, c.segment
        ORDER BY spend DESC
    """,
    "top_products": """
        SELECT 
            p.product_id AS prod_id,
            p.product_name,
            p.category,
            SUM(oi.quantity) AS units_sold,
            ROUND(SUM(oi.subtotal), 2) AS total_revenue
        FROM order_items oi
        INNER JOIN products p ON oi.product_id = p.product_id
        INNER JOIN orders o ON oi.order_id = o.order_id
        WHERE o.status != 'Cancelled'
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY total_revenue DESC
    """,
    "retention": """
        WITH FirstPurchase AS (
            SELECT customer_id, MIN(STRFTIME('%Y-%m', order_timestamp)) AS cohort_month
            FROM orders WHERE status != 'Cancelled' GROUP BY customer_id
        ),
        CohortSizes AS (
            SELECT cohort_month, COUNT(DISTINCT customer_id) AS cohort_size
            FROM FirstPurchase GROUP BY cohort_month
        ),
        Activity AS (
            SELECT DISTINCT o.customer_id, fp.cohort_month,
                ((CAST(STRFTIME('%Y', o.order_timestamp) AS INT) - CAST(SUBSTR(fp.cohort_month, 1, 4) AS INT)) * 12 +
                 (CAST(STRFTIME('%m', o.order_timestamp) AS INT) - CAST(SUBSTR(fp.cohort_month, 6, 2) AS INT))) AS month_num
            FROM orders o
            JOIN FirstPurchase fp ON o.customer_id = fp.customer_id
            WHERE o.status != 'Cancelled'
        )
        SELECT 
            a.cohort_month AS cohort,
            cs.cohort_size AS total_users,
            ROUND(COUNT(DISTINCT CASE WHEN month_num = 0 THEN a.customer_id END) * 100.0 / cs.cohort_size, 1) AS m0_ret_pct,
            ROUND(COUNT(DISTINCT CASE WHEN month_num = 1 THEN a.customer_id END) * 100.0 / cs.cohort_size, 1) AS m1_ret_pct,
            ROUND(COUNT(DISTINCT CASE WHEN month_num = 2 THEN a.customer_id END) * 100.0 / cs.cohort_size, 1) AS m2_ret_pct
        FROM Activity a
        JOIN CohortSizes cs ON a.cohort_month = cs.cohort_month
        GROUP BY a.cohort_month, cs.cohort_size
        ORDER BY a.cohort_month ASC
    """,
    "rfm": """
        WITH MaxDate AS (SELECT MAX(order_timestamp) AS max_ts FROM orders),
        RFM AS (
            SELECT 
                c.customer_id, c.name, c.city,
                CAST(JULIANDAY((SELECT max_ts FROM MaxDate)) - JULIANDAY(MAX(o.order_timestamp)) AS INT) AS recency,
                COUNT(o.order_id) AS frequency,
                ROUND(SUM(o.total_amount), 2) AS monetary
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.status != 'Cancelled'
            {WHERE_CLAUSE}
            GROUP BY c.customer_id, c.name, c.city
        ),
        Scores AS (
            SELECT *,
                NTILE(4) OVER (ORDER BY recency DESC) AS r_score,
                NTILE(4) OVER (ORDER BY frequency ASC) AS f_score,
                NTILE(4) OVER (ORDER BY monetary ASC) AS m_score
            FROM RFM
        )
        SELECT customer_id AS cust_id, name, city, recency AS rec_days, frequency AS freq, monetary AS spend,
            (r_score || f_score || m_score) AS rfm_score,
            CASE 
                WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Champions / VIP'
                WHEN r_score >= 3 AND f_score >= 2 THEN 'Loyal Customers'
                WHEN r_score >= 3 AND f_score = 1 THEN 'New Customers'
                WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
                ELSE 'Needs Attention'
            END AS rfm_segment
        FROM Scores
        ORDER BY spend DESC
    """
}

def auto_initialize_db(conn):
    """Auto initializes database schema and loads cleaned datasets if not loaded."""
    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
        
    tables_map = {
        "customers": "customers_clean.csv",
        "products": "products_clean.csv",
        "orders": "orders_clean.csv",
        "order_items": "order_items_clean.csv"
    }
    for tbl, fname in tables_map.items():
        fpath = os.path.join(CLEANED_DIR, fname)
        if os.path.exists(fpath):
            df = pd.read_csv(fpath)
            df.to_sql(tbl, conn, if_exists="append", index=False)

def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    needs_init = not os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    if needs_init:
        auto_initialize_db(conn)
    return conn

def execute_report(report_name, limit=None, city=None):
    if report_name not in BASE_QUERIES:
        print(f"[ERROR] Invalid report name: '{report_name}'. Valid choices: {list(BASE_QUERIES.keys())}")
        sys.exit(1)
        
    raw_query = BASE_QUERIES[report_name]
    params = []
    
    if city:
        if "{WHERE_CLAUSE}" in raw_query:
            raw_query = raw_query.format(WHERE_CLAUSE="AND c.city = ?")
            params.append(city)
        else:
            raw_query = f"SELECT * FROM ({raw_query}) WHERE city = ?"
            params.append(city)
    else:
        if "{WHERE_CLAUSE}" in raw_query:
            raw_query = raw_query.format(WHERE_CLAUSE="")
            
    if limit is not None:
        raw_query += " LIMIT ?"
        params.append(int(limit))
        
    conn = get_connection()
    try:
        df = pd.read_sql_query(raw_query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        print(f"[ERROR] Query Execution Failed for '{report_name}': {e}")
        conn.close()
        return pd.DataFrame()

def format_clean_ascii_table(df):
    try:
        from tabulate import tabulate
        return tabulate(df, headers="keys", tablefmt="simple", showindex=False)
    except ImportError:
        col_widths = {col: max(len(str(col)), df[col].astype(str).str.len().max() if not df.empty else 0) for col in df.columns}
        header_row = "  ".join(str(col).ljust(col_widths[col]) for col in df.columns)
        separator = "  ".join("-" * col_widths[col] for col in df.columns)
        rows = [
            "  ".join(str(val).ljust(col_widths[col]) for col, val in zip(df.columns, row))
            for row in df.itertuples(index=False)
        ]
        return "\n".join([header_row, separator] + rows)

def render_output(df, report_name, fmt="table", export=False):
    if df.empty:
        print(f"\n[INFO] Report '{report_name}' returned NO RESULTS (Empty Set).")
        return

    print(f"\n===========================================================")
    print(f" REPORT: {report_name.upper()} (Total Records: {len(df)})")
    print(f"===========================================================")
    
    if fmt == "json":
        print(df.to_json(orient="records", indent=2))
    elif fmt == "csv":
        print(df.to_csv(index=False))
    else:
        print(format_clean_ascii_table(df))
        
    if export:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        file_path = os.path.join(OUTPUT_DIR, f"{report_name}_report.csv")
        df.to_csv(file_path, index=False)
        print(f"\n[SUCCESS] Exported report to: {file_path}")

def main():
    parser = argparse.ArgumentParser(description="Food Delivery & E-Commerce Order Analytics CLI Tool")
    parser.add_argument("--report", type=str, required=True, 
                        choices=["revenue", "top_customers", "top_products", "retention", "rfm", "all"],
                        help="Specify report type to generate")
    parser.add_argument("--format", type=str, default="table", choices=["table", "json", "csv"],
                        help="Output format (table, json, csv)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of rows returned")
    parser.add_argument("--city", type=str, default=None, help="Filter report by city securely")
    parser.add_argument("--export", action="store_true", help="Export report output to CSV in output/sample_reports/")

    args = parser.parse_args()

    if args.report == "all":
        for r_name in ["revenue", "top_customers", "top_products", "retention", "rfm"]:
            df = execute_report(r_name, limit=args.limit, city=args.city)
            render_output(df, r_name, fmt=args.format, export=args.export)
    else:
        df = execute_report(args.report, limit=args.limit, city=args.city)
        render_output(df, args.report, fmt=args.format, export=args.export)

if __name__ == "__main__":
    main()
