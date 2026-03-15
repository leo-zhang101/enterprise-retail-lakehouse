# Retail Analytics (dbt)

dbt project that models PostgreSQL staging tables into analytics-ready marts for the retail lakehouse platform.

## Overview

- **Sources**: PostgreSQL `staging` schema (dim_product, dim_store, dim_customer, fact_sales, fact_inventory_daily)
- **Staging models**: Standardize and rename fields; filter to valid records where applicable
- **Intermediate models**: Reusable analytical logic (daily aggregates, product/promotion summaries)
- **Marts**: Business-facing, reporting-ready tables

## Prerequisites

- dbt-core 1.5+ and dbt-postgres
- PostgreSQL with staging tables loaded (run warehouse load first)

```bash
pip install dbt-core dbt-postgres
```

## Setup

1. Set PostgreSQL environment variables (or use defaults):
   - `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`

2. Copy or symlink `profiles.yml` so dbt can find it:
   ```bash
   mkdir -p ~/.dbt
   cp profiles.yml ~/.dbt/profiles.yml
   # Or: export DBT_PROFILES_DIR=$PWD
   ```

## Project Structure

```
dbt/retail_analytics/
├── dbt_project.yml
├── profiles.yml
├── models/
│   ├── staging/
│   │   ├── _sources.yml      # Source definitions
│   │   ├── stg_dim_product.sql
│   │   ├── stg_dim_store.sql
│   │   ├── stg_dim_customer.sql
│   │   ├── stg_fact_sales.sql
│   │   └── stg_fact_inventory_daily.sql
│   ├── intermediate/
│   │   ├── int_sales_daily.sql
│   │   ├── int_product_sales.sql
│   │   └── int_promotion_sales.sql
│   └── marts/
│       ├── mart_store_sales_daily.sql
│       ├── mart_product_performance.sql
│       └── mart_promotion_effectiveness.sql
├── tests/
│   └── schema.yml            # Model tests (unique, not_null, relationships)
├── macros/
│   └── generate_schema_name.sql
└── README.md
```

## Usage

```bash
cd dbt/retail_analytics

# Build all models
dbt run

# Run tests
dbt test

# Generate docs
dbt docs generate
dbt docs serve
```

## Model Layers

| Layer | Models | Purpose |
|-------|--------|---------|
| Staging | stg_dim_*, stg_fact_* | Clean sources; standardize names; filter invalid sales |
| Intermediate | int_sales_daily, int_product_sales, int_promotion_sales | Reusable aggregates |
| Marts | mart_store_sales_daily, mart_product_performance, mart_promotion_effectiveness | Reporting-ready tables |

## Output Schemas

- `staging`: stg_* views
- `intermediate`: int_* views
- `marts`: mart_* tables
