# Delta Lake Incremental Data Processing Assignment

> **PySpark & Delta Lake Implementation**  
> *Demonstrating Scalable ETL, Data Quality Assurance, and Slowly Changing Dimensions (SCD Type 1 & SCD Type 2)*

---

## 📌 Executive Summary

This repository presents an enterprise-ready Data Engineering pipeline built with **PySpark** and **Delta Lake**. Designed to process incremental retail customer datasets, the project implements robust schema governance, programmatic Data Quality (DQ) assertions, and advanced Slowly Changing Dimension (SCD) patterns to maintain both transactional state and full historical audit logs.

### Key Technical Highlights
- **Strict Schema Enforcement:** Replaces fragile auto-inference (`inferSchema=True`) with explicit PySpark `StructType` definitions, eliminating schema drift risks.
- **Cross-Platform Compatibility:** Features dynamic, relative path resolution and OS platform guards (`sys.platform`), allowing seamless execution across **Windows, macOS, and Linux** environments without hardcoded path dependencies.
- **SCD Type 1 (Overwrite/Upsert):** Performs atomical `MERGE` operations to update existing records and insert new incoming customer attributes.
- **SCD Type 2 (Historical Audit):** Implements multi-version record management utilizing `is_active`, `effective_date`, and `end_date` attributes for full historical tracking.
- **Programmatic Quality Assertions:** Replaces manual visual checks with runtime `assert` statements to ensure data cleanlines and zero null key occurrences before downstream consumption.

---

## 🛠️ Technology Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Compute Engine** | PySpark (v3.5.1) | Distributed Data Processing & Spark SQL Engine |
| **Storage Layer** | Delta Lake (v3.1.0) | ACID Transactions, Time Travel & Schema Enforcement |
| **Runtime Environment** | Python 3.11+ | Virtual Environment (`venv`) Managed Pipeline |
| **Orchestration / Notebook**| JupyterLab / VS Code | Interactive Execution & Workflow Visualization |

---

## 📂 Repository Structure

```text
delta-lake-assignment/
├── data/                                 # Datasets & Target Delta Tables
│   ├── customer_master.csv               # Baseline Master Dataset (400 records)
│   ├── customer_incremental.csv          # Incremental Batch (50 new + 20 updates)
│   ├── delta_scd1/                       # ACID Delta Storage (SCD Type 1)
│   └── delta_scd2/                       # ACID Delta Storage (SCD Type 2)
│
├── notebooks/                            # Development & Execution Artifacts
│   └── delta_scd_assignment.ipynb        # Primary Production Jupyter Notebook
│
├── screenshots/                          # Audit Evidence & Submission Screenshots
│   ├── data_loading/                     # 01_data_loading.png
│   ├── data_cleaning/                    # 02_data_cleaning.png
│   ├── scd1/                             # 03_scd1_merge.png
│   ├── scd2/                             # 04_scd2_merge.png
│   ├── validation/                       # 05_validation_assertions.png
│   └── final_output/                     # 06_final_output_tables.png
│
├── report/                               # Summary Artifacts & Technical Reports
├── requirements.txt                      # Pinned Dependencies for Reproducibility
└── README.md                             # Project Documentation
```

---

## 🔄 Data Pipeline Architecture

```
[ Raw CSV Datasets ] 
         │
         ▼
[ Explicit StructType Schema ] ──► [ Data Quality Assertions (Null / Deduplication Checks) ]
                                                       │
                                 ┌─────────────────────┴─────────────────────┐
                                 ▼                                           ▼
                      [ SCD Type 1 MERGE ]                       [ SCD Type 2 MERGE ]
                     (Latest Snapshot State)                    (Full Audit Tracking History)
```

### 1. Data Ingestion & Schema Contracts
Master customer data (`customer_master.csv`) and incremental batches (`customer_incremental.csv`) are ingested with an explicit `StructType` schema. Column names are sanitized to standardized `snake_case` (e.g., `customer_id`, `postal_code`) to ensure full compliance with Delta Lake table specifications.

### 2. Data Quality (DQ) Enforcement
Before execution of transactional merges, the pipeline runs programmatic assertion gates:
- Duplicate record elimination on key attributes (`customer_id`).
- Null key checks ensuring mandatory non-null primary keys (`assert null_ids == 0`).

### 3. Slowly Changing Dimensions (SCD)
- **SCD Type 1:** Uses `DeltaTable.alias().merge()` matching on `customer_id`. Matching records receive attributes updates (`whenMatchedUpdateAll`), while new customer IDs are inserted (`whenNotMatchedInsertAll`).
- **SCD Type 2:** Staged updates are combined with historical active flags. When an attribute change occurs (e.g., customer moves to `New Enterprise City`), the prior active record is flagged `is_active = false` with an `end_date`, and the new record version is inserted with `is_active = true` and `effective_date`.

---

## 🚀 Quickstart & Setup Guide

### 1. Environment Initialization
Clone the repository and install the pinned dependencies:
```bash
git clone <your-repository-url>
cd delta-lake-assignment
pip install -r requirements.txt
```

### 2. Running the Pipeline
Launch JupyterLab or open the project in VS Code:
```bash
jupyter lab
```
Navigate to `notebooks/delta_scd_assignment.ipynb` and select **Run All Cells**.

---

## 🔍 Verification & Testing

The notebook features automated runtime checks. Upon successful completion, the notebook outputs validation metrics:
```text
Spark setup complete. Working with project root: /path/to/delta-lake-assignment
Data loading completed securely.
Data cleaned successfully. Valid records: 400
Loaded 70 incremental records.
SCD1 MERGE completed. Total rows: 450
SCD2 MERGE completed. Total rows (including history): 470
All DQ Assertions passed successfully!
```

---

