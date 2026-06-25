# Shopping Dataset Analysis

This repository contains an end-to-end exploratory data analysis (EDA), data cleaning, feature engineering, and visualization of a shopping dataset.

---

## Folder Structure

```text
shopping-analysis/
├── data/
│   └── combined_dataset.csv
├── notebook/
│   └── analysis.ipynb
└── README.md
```

---

## Objective

The objective of this project is to perform EDA, clean raw transaction and catalog data, engineer new business-critical features, visualize key trends, and derive actionable business recommendations.

---

## Workflow Steps

### Step 1: Load Data
* Imported libraries: `pandas`, `numpy`, `matplotlib.pyplot`, and `seaborn`.
* Loaded the dataset and inspected basic shape, columns, and initial records.

### Step 2: Understand Data
* Inspected column types, summary statistics (`info()`, `describe()`), and null values count.

### Step 3: Data Cleaning
* Cleansed pricing columns (specifically converting `final_price` from object format to numeric values by stripping currency symbols and quotes).
* Handled missing values using target fill-ins (filling numerical null values in `discount` with `0` and textual/categorical null values with placeholders like `'Unknown'`).
* Handled duplicate checks and dropped unnecessary repetitions.

### Step 4: Feature Engineering
* Engineered a `price_difference` column representing direct savings (`initial_price - final_price`).
* Created a `popularity` metric combining product rating score and rating frequency (`rating * ratings_count`).
* Parsed complex columns (specifically extracting `5_star_count` from `amount_of_stars` JSON metadata).

### Step 5: Analysis
* Performed univariate analysis on target metrics (`final_price`, `rating`, and `category`).
* Conducted bivariate analysis (price vs. rating, popularity vs. rating).
* Aggregated category-level summary metrics (mean pricing, rating, and counts).

### Step 6: Visualization
* Plotted histograms, count-plots, outlier boxplots, and scatterplots.

### Step 7: Insights
* Summarized high-level insights and detailed target actions for marketing, pricing, and inventory management.