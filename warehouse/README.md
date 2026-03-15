# Warehouse Load

Load Gold parquet datasets from MinIO (local) or S3 (AWS) into PostgreSQL staging tables.

**Local**: PostgreSQL (Docker). **AWS**: Same loader, RDS PostgreSQL (or Redshift). See [docs/AWS_PRODUCTION_MAPPING.md](../docs/AWS_PRODUCTION_MAPPING.md).

## Overview

- **Staging schema**: Raw load from Gold parquet.
- **Load strategy**: Full refresh for dimensions and marts; idempotent partition-based incremental loading for fact tables.
- **Marts schema**: Reserved for analytics-ready materialized views (optional, not auto-created here).

### Full refresh vs incremental

| Table | Strategy | Description |
|-------|----------|-------------|
| dim_product, dim_store, dim_customer | Full refresh | Truncate table, insert all rows. |
| fct_store_sales_daily, fct_product_performance, fct_promotion_effectiveness | Full refresh | Truncate table, insert all rows. |
| fact_sales, fact_inventory_daily | Incremental | Idempotent partition-based incremental loading: delete-by-load_date plus PostgreSQL upsert (INSERT ... ON CONFLICT DO UPDATE). |

## Prerequisites

- PostgreSQL running (e.g. `docker compose up -d postgres`)
- Gold parquet available at `GOLD_PATH` (see below)
- Python deps: `psycopg2-binary`, `pandas`, `pyarrow`

## Setup

```bash
# From project root
pip install psycopg2-binary pandas pyarrow

# Initialize staging tables (run once)
psql -h localhost -U retail -d retail_warehouse -f warehouse/schemas/init.sql
```

## Gold Path

Gold parquet is written by Spark to MinIO with layout: `gold/<table>/load_date=YYYY-MM-DD/`.

The loader expects **local filesystem paths** by default. To use Gold from MinIO:

1. **Sync to local first** (recommended): Copy the Gold bucket from MinIO, preserving layout:
   ```bash
   mc cp -r minio/gold ./gold
   # Yields: ./gold/dim_product/load_date=2025-03-13/, ./gold/dim_store/load_date=2025-03-13/, etc.
   export GOLD_PATH=./gold
   ```

2. **Direct S3/MinIO access**: With `pip install s3fs` and AWS credentials (or MinIO env vars), set `GOLD_PATH=s3://bucket/gold/` to read parquet directly from S3-compatible storage. In AWS, use `GOLD_PATH=s3://retail-gold/` (or your S3 bucket).

## Usage

```bash
# From project root
export PYTHONPATH=.
export GOLD_PATH=./gold   # or path where Gold parquet lives

python warehouse/jobs/run_warehouse_load.py --load-date 2025-03-13
```

### Options

- `--load-date` (required): YYYY-MM-DD matching Gold partition
- `--gold-path`: Override base path to Gold parquet
- `--tables`: Load specific tables only (default: all)

## Environment

| Variable        | Default           | Description                    |
|----------------|-------------------|--------------------------------|
| POSTGRES_HOST  | localhost         | PostgreSQL host                |
| POSTGRES_PORT  | 5432              | PostgreSQL port                |
| POSTGRES_DB    | retail_warehouse  | Database name                  |
| POSTGRES_USER  | retail            | User                           |
| POSTGRES_PASSWORD | retail         | Password                       |
| GOLD_PATH      | ./gold            | Base path to Gold parquet      |

## Staging Tables

| Table                     | Grain                          | Load strategy | Purpose                    |
|---------------------------|--------------------------------|---------------|----------------------------|
| dim_product               | One row per product            | Full refresh  | Product master             |
| dim_store                 | One row per store              | Full refresh  | Store master               |
| dim_customer              | One row per customer           | Full refresh  | Customer master            |
| fact_sales                | One row per sale transaction   | Incremental   | Transaction-level sales    |
| fact_inventory_daily      | One row per product/store/date| Incremental   | Daily inventory snapshot   |
| fct_store_sales_daily     | One row per store per date     | Full refresh  | Store daily sales summary  |
| fct_product_performance   | One row per product            | Full refresh  | Product performance summary|
| fct_promotion_effectiveness | One row per promotion        | Full refresh  | Promotion effectiveness    |
