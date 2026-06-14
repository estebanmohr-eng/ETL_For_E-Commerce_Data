# E-commerce ETL Pipeline

A Python ETL (Extract, Transform, Load) pipeline that processes raw e-commerce data — orders, order items, customers, and products — cleans it according to documented business rules, answers a set of key business questions, and exports the results in both CSV and Parquet formats.

## Description

This project simulates a real-world data engineering workflow: ingesting raw CSV exports from an e-commerce platform, performing data quality checks (nulls, duplicates, and type consistency), and producing analysis-ready datasets plus pre-computed business insights.

The pipeline is built with **pandas** and follows the classic ETL structure:

1. **Extract** — Load and validate the raw CSV files.
2. **Transform** — Handle missing values and duplicates, enforce correct data types, and answer business questions.
3. **Load** — Export cleaned datasets and business-question results as CSV and Parquet files.

## Requirements

- Python 3.x
- [pandas](https://pandas.pydata.org/)
- A Parquet engine for pandas (e.g. `pyarrow` or `fastparquet`)

Install dependencies:

```bash
pip install pandas pyarrow
```

## How to Run

1. Clone this repository. The `data/` folder is already included with the sample CSV files:
   - `ecommerce_orders.csv`
   - `ecommerce_order_items.csv`
   - `ecommerce_customers.csv`
   - `ecommerce_products.csv`
2. Run the script:

```bash
python etl.py
```

The script will print exploration summaries, data quality reports, and business question results to the console as it runs, and will automatically create the `output/` folder structure described below.

## Data Source

The data used in this project is **synthetic/fictitious**, generated with the dataset generator from [Data Engineering Academy by Ian Saura](https://www.iansaura.com/). It was created for learning and portfolio purposes only and does not represent real customers, orders, or products.

## Cleaning Decisions

The cleaning strategy was designed around three target business questions:

1. Who are the top 5 customers by spending?
2. What is the best-selling product (by quantity)?
3. How did sales evolve month over month?

Based on these objectives, each dataset's columns were classified as **critical** or **non-critical**:

### Null Handling

- **Critical columns** (essential for answering the business questions): rows with missing values in these columns are **dropped**.
  - Orders: `order_id`, `customer_id`, `order_date`, `total_amount`
  - Order Items: `order_item_id`, `order_id`, `product_id`
  - Customers: `customer_id`
  - Products: `product_id`, `price`

- **Non-critical columns**: missing values are **filled** rather than dropped, to preserve as many rows as possible:
  - String columns → filled with `""`
  - Numeric columns → filled with `0`
  - Boolean columns → filled with `False`

  This applies to columns such as `order_number`, `payment_method`, `shipping_method`, `notes`, `status`, `discount_percent`, `shipping_cost`, `tax_amount`, `promotion_id`, `subtotal` (Orders); `unit_price`, `quantity`, `subtotal` (Order Items); `first_name`, `last_name`, `email`, `phone`, `birth_date`, `city`, `country`, `postal_code`, `segment`, `registration_date`, `last_login`, `accepts_marketing`, `is_verified` (Customers); and `sku`, `product_name`, `description`, `category_id`, `brand_id`, `supplier_id`, `cost`, `weight_kg`, `is_active`, `created_at`, `updated_at` (Products).


The pipeline also reports, for each dataset, the percentage of null values per column (both before and after cleaning) and the number of rows removed due to critical nulls.

### Duplicate Handling

- Duplicates are identified based on each dataset's **critical columns** (the same columns used for null filtering), since these uniquely identify a record for the purposes of this analysis.
- Duplicate rows are removed using `drop_duplicates()`, and the pipeline reports the duplicate count both as a percentage of the original dataset and as a percentage of the dataset after null cleaning.
- A final check confirms that no duplicates remain after cleaning.

### Type Enforcement

After deduplication, column types are standardized:

- **Dates** converted to `datetime` (`order_date`; `birth_date`, `registration_date`, `last_login`; `created_at`, `updated_at`), with invalid values coerced to `NaT`.
- **Floats** enforced for monetary and quantity fields (e.g. `total_amount`, `subtotal`, `discount_percent`, `shipping_cost`, `tax_amount`, `unit_price`, `quantity`, `cost`, `weight_kg`, `price`, `postal_code`), with invalid values coerced to `NaN`.
- **Integers** enforced for ID fields (e.g. `order_id`, `customer_id`, `promotion_id`, `order_item_id`, `product_id`, `category_id`, `brand_id`, `supplier_id`), using downcasting where possible.
- **Booleans** enforced for flag fields (`accepts_marketing`, `is_verified`, `is_active`) via numeric coercion followed by boolean casting.

At each conversion step, the pipeline checks for newly introduced nulls. Any rows that become invalid as a result of type coercion are dropped, and the number of affected rows is reported per dataset.

> The "Transform: Other" section is reserved for additional transformations (e.g. deriving a year/month column from `order_date`, or dropping irrelevant columns) as the analysis evolves.

## Business Questions Answered

1. **Top 5 customers by spending** — Orders are grouped by `customer_id`, total spending is summed and sorted descending, and the top 5 are enriched with customer details (name, city, email).
2. **Best-selling product by quantity** — Order items are grouped by `product_id`, quantities are summed and sorted descending, and the top 5 are enriched with product details (name, SKU). The single top result is also saved separately as the "best-selling product."
3. **Month-over-month sales evolution** — Orders are grouped by year-month (derived from `order_date`) and total sales are summed and sorted chronologically.

Additional business questions (e.g. best-selling product category, city with the most customers, most common payment method) can be added in this section as the analysis grows.

## Output

Running the script generates an `output/` directory with two subfolders, each containing the cleaned datasets and the results of the business questions:

```
output/
├── csv/
│   ├── orders_clean.csv
│   ├── order_items_clean.csv
│   ├── customers_clean.csv
│   ├── products_clean.csv
│   ├── top_5_customers.csv
│   ├── best_selling_product.csv
│   └── sales_evolution.csv
└── parquet/
    ├── orders_clean.parquet
    ├── order_items_clean.parquet
    ├── customers_clean.parquet
    ├── products_clean.parquet
    ├── top_5_customers.parquet
    ├── best_selling_product.parquet
    └── sales_evolution.parquet
```

- **`*_clean` files**: the fully cleaned and type-validated datasets, ready for further analysis or loading into a database/data warehouse.
- **`top_5_customers`**: the 5 highest-spending customers with their contact details.
- **`best_selling_product`**: the single top-selling product by quantity sold.
- **`sales_evolution`**: total sales aggregated by month, in chronological order.

Both CSV (for portability and quick inspection) and Parquet (for efficient storage and downstream analytics) formats are provided.

> Note: The `output/` folder is generated when running the script and is excluded from version control via `.gitignore`, since it contains derived artifacts rather than source data. A small sample of the results may be included separately under `examples/` for quick reference.

## Author

**Esteban Mohr** ([estebanmohr-eng](https://github.com/estebanmohr-eng))

## License

This project is licensed under the MIT License.