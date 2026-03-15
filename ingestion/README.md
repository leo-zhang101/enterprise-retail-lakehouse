# Ingestion Module

Uploads local raw CSV files from `data/raw/` into the MinIO raw bucket.

## Overview

- **Source**: `data/raw/<entity>/<entity>.csv`
- **Target**: MinIO `raw/<entity>/load_date=YYYY-MM-DD/<entity>.csv`
- **Entities**: products, stores, customers, promotions, sales_transactions, inventory_snapshots

## Prerequisites

1. MinIO running (e.g. `docker compose up -d`)
2. Raw data generated (e.g. `python -m data_generator.src.generate_retail_data`)
3. Environment variables set (copy `.env.example` to `.env`)

## Usage

```bash
# Ingest all entities (load_date = today)
python -m ingestion.jobs.run_ingestion

# Ingest with specific load date
python -m ingestion.jobs.run_ingestion --load-date 2025-03-13

# Ingest specific entities only
python -m ingestion.jobs.run_ingestion --entities products stores sales_transactions

# Custom raw directory
python -m ingestion.jobs.run_ingestion --raw-dir /path/to/data/raw
```

## Module Structure

```
ingestion/
├── src/
│   ├── config.py           # Ingestion config (uses shared)
│   ├── connectors/
│   │   └── minio_client.py # MinIO client wrapper
│   └── loaders/
│       └── file_loader.py   # Upload logic
├── jobs/
│   └── run_ingestion.py    # CLI entry point
└── README.md
```

## Validation

- Local file must exist before upload
- Bucket is created if it does not exist
- Upload success/failure is logged per entity
- Job exits with code 1 if any entity fails
