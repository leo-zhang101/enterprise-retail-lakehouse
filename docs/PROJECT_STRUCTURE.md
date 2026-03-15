# Enterprise Retail Lakehouse Platform — Project Structure

> Production-style data engineering platform for Australian enterprise retail analytics.

---

## 1. Complete Folder Tree

```
enterprise-retail-lakehouse/
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                    # Lint, test, build
│   │   └── docker-build.yml          # Docker image build
│   └── PULL_REQUEST_TEMPLATE.md
│
├── docker/
│   └── scripts/
│       ├── init-minio-buckets.sh
│       ├── init-postgres-schemas.sh
│       └── wait-for-services.sh
│
├── data_generator/
│   ├── src/
│   │   ├── __init__.py
│   │   └── generate_retail_data.py
│   ├── requirements.txt
│   └── README.md
│
├── ingestion/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── connectors/
│   │   │   ├── minio_client.py
│   │   │   └── s3_connector.py
│   │   ├── loaders/
│   │   │   ├── file_loader.py        # Local/CSV → MinIO
│   │   │   └── api_loader.py         # Optional: API → MinIO
│   │   └── config.py
│   ├── jobs/
│   │   └── run_ingestion.py          # Entry point
│   ├── requirements.txt
│   └── README.md
│
├── spark_jobs/
│   ├── jobs/
│   │   ├── bronze/
│   │   │   ├── __init__.py
│   │   │   ├── ingest_sales.py
│   │   │   ├── ingest_inventory.py
│   │   │   ├── ingest_products.py
│   │   │   ├── ingest_stores.py
│   │   │   ├── ingest_customers.py
│   │   │   └── ingest_promotions.py
│   │   ├── silver/
│   │   │   ├── __init__.py
│   │   │   ├── transform_sales.py
│   │   │   ├── transform_inventory.py
│   │   │   ├── transform_products.py
│   │   │   ├── transform_stores.py
│   │   │   ├── transform_customers.py
│   │   │   └── transform_promotions.py
│   │   └── gold/
│   │       ├── __init__.py
│   │       ├── build_sales_mart.py
│   │       ├── build_inventory_mart.py
│   │       └── build_reporting_mart.py
│   ├── lib/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── schemas.py                # Bronze/Silver/Gold schemas
│   │   ├── quality/
│   │   │   ├── __init__.py
│   │   │   └── validators.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── incremental.py
│   ├── config/
│   │   └── spark-defaults.yaml
│   ├── requirements.txt
│   └── README.md
│
├── airflow/
│   ├── dags/
│   │   └── retail_lakehouse_pipeline.py   # Single DAG for MVP; split later
│   ├── plugins/
│   │   └── operators/
│   │       ├── __init__.py
│   │       └── spark_submit_operator.py
│   ├── config/
│   │   └── airflow.cfg
│   ├── requirements.txt
│   └── README.md
│
├── warehouse/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── loaders/
│   │   │   ├── postgres_loader.py    # Gold → PostgreSQL
│   │   │   └── jdbc_loader.py        # Spark JDBC write
│   │   ├── connectors/
│   │   │   └── postgres_client.py
│   │   └── config.py
│   ├── jobs/
│   │   └── run_warehouse_load.py
│   ├── schemas/
│   │   └── init.sql                 # Target schema DDL
│   ├── requirements.txt
│   └── README.md
│
├── dbt/
│   └── retail_analytics/
│       ├── dbt_project.yml
│       ├── profiles.yml
│       ├── models/
│       │   ├── staging/
│       │   │   ├── stg_sales.sql
│       │   │   ├── stg_inventory.sql
│       │   │   ├── stg_products.sql
│       │   │   ├── stg_stores.sql
│       │   │   ├── stg_customers.sql
│       │   │   └── stg_promotions.sql
│       │   ├── intermediate/
│       │   │   ├── int_sales_daily.sql
│       │   │   └── int_inventory_snapshot.sql
│       │   └── marts/
│       │       ├── sales/
│       │       │   ├── fct_sales.sql
│       │       │   └── dim_product.sql
│       │       ├── inventory/
│       │       │   └── fct_inventory_snapshot.sql
│       │       └── reporting/
│       │           └── rpt_sales_summary.sql
│       ├── tests/
│       │   └── schema.yml
│       ├── macros/
│       │   └── australia_timezone.sql
│       ├── seeds/
│       └── README.md
│
├── dashboards/
│   ├── metabase/
│   │   ├── docker-compose.yml        # Metabase standalone
│   │   └── README.md
│   ├── config/
│   │   └── datasource.yml           # Connection config
│   └── exports/                     # Saved dashboard JSON (optional)
│       └── .gitkeep
│
├── shared/
│   └── src/
│       └── retail_lakehouse/
│           ├── __init__.py
│           ├── config/
│           │   ├── __init__.py
│           │   ├── settings.py
│           │   └── constants.py
│           ├── schemas/
│           │   ├── __init__.py
│           │   └── retail_schemas.py
│           └── utils/
│               ├── __init__.py
│               ├── logging_utils.py
│               └── date_utils.py
│
├── data/
│   ├── raw/                         # Local raw data (dev)
│   │   ├── sales/
│   │   ├── inventory/
│   │   ├── products/
│   │   ├── stores/
│   │   ├── customers/
│   │   └── promotions/
│   ├── schemas/
│   │   ├── sales.json
│   │   ├── inventory.json
│   │   └── ...
│   └── scripts/
│       └── seed_and_upload.sh       # Generate + upload to MinIO
│
├── tests/
│   ├── unit/
│   │   ├── test_schemas.py
│   │   ├── test_validators.py
│   │   └── test_config.py
│   ├── integration/
│   │   ├── test_ingestion.py
│   │   └── test_spark_bronze.py
│   ├── conftest.py
│   └── pytest.ini
│
├── docs/
│   ├── PROJECT_STRUCTURE.md         # This file
│   ├── ARCHITECTURE.md
│   ├── DATA_DICTIONARY.md
│   ├── RUNBOOK.md
│   └── diagrams/
│       └── data_flow.png
│
├── assets/
│   └── .gitkeep                     # Architecture diagrams, screenshots
│
├── scripts/
│   ├── setup_local.sh               # One-shot local setup
│   ├── run_full_pipeline.sh         # End-to-end run
│   └── generate_data.sh
│
├── docker-compose.yml               # Full stack orchestration
├── docker-compose.dev.yml           # Dev overrides (hot reload)
├── .env.example
├── .gitignore
├── Makefile                         # Common commands
├── README.md
└── LICENSE
```

---

## 2. Top-Level Folder Explanations

| Folder | Purpose |
|--------|---------|
| **`.github/`** | CI/CD workflows, PR templates. Signals a professional, maintainable repo. |
| **`docker/`** | Init scripts for MinIO buckets, Postgres schemas. Compose files live at repo root. |
| **`data_generator/`** | Generates realistic AU retail CSV/JSON for local dev. Standalone module. |
| **`ingestion/`** | Raw data ingestion: local files / APIs → MinIO (S3). Separated so ingestion logic is independent and testable. |
| **`spark_jobs/`** | PySpark jobs for Bronze, Silver, Gold layers. Medallion architecture implementation. |
| **`airflow/`** | Airflow DAGs and custom operators. Schedules and coordinates all pipeline steps. |
| **`warehouse/`** | Loads Gold layer data from MinIO/Spark into PostgreSQL. Bridge between lake and warehouse. |
| **`dbt/`** | dbt models for staging, intermediate, and marts. Transforms warehouse tables into analytics-ready models. |
| **`dashboards/`** | Metabase (or similar) config and exported dashboards. Connects to PostgreSQL for BI. |
| **`shared/`** | Shared Python libs: config, schemas, utils. Used by ingestion, spark_jobs, warehouse, data_generator. |
| **`data/`** | Local raw data, JSON schemas, and scripts for seeding MinIO. Dev/test only. |
| **`tests/`** | Unit and integration tests. Keeps quality bar visible. |
| **`docs/`** | Architecture, data dictionary, runbook, diagrams. Portfolio and onboarding. |
| **`assets/`** | Static assets: architecture diagrams, screenshots, images for README/docs. |
| **`scripts/`** | Top-level automation: setup, full pipeline run, data generation. |

---

## 3. Key Files per Module

### `docker/`
| File | Role |
|------|------|
| `scripts/init-minio-buckets.sh` | Creates `raw`, `bronze`, `silver`, `gold` buckets |
| `scripts/init-postgres-schemas.sh` | Creates schemas/tables for dbt target |
| `scripts/wait-for-services.sh` | Waits for services before init |

### `data_generator/`
| File | Role |
|------|------|
| `src/generate_retail_data.py` | Generates realistic AU retail CSV/JSON (sales, inventory, products, etc.) |

### `ingestion/`
| File | Role |
|------|------|
| `src/connectors/minio_client.py` | MinIO/S3 client wrapper |
| `src/loaders/file_loader.py` | Reads local CSV/JSON, writes to MinIO raw |
| `jobs/run_ingestion.py` | CLI entry point for ingestion job |

### `spark_jobs/`
| File | Role |
|------|------|
| `lib/schemas.py` | Pyspark StructType for Bronze/Silver/Gold |
| `lib/quality/validators.py` | Null checks, type validation, row counts |
| `lib/utils/incremental.py` | Incremental load helpers (e.g. by date) |
| `jobs/bronze/ingest_*.py` | Raw → Bronze (one per entity) |
| `jobs/silver/transform_*.py` | Bronze → Silver (clean, dedupe) |
| `jobs/gold/build_*_mart.py` | Silver → Gold (aggregations, marts) |

### `airflow/`
| File | Role |
|------|------|
| `dags/retail_lakehouse_pipeline.py` | Single DAG: ingestion → bronze → silver → gold → warehouse → dbt (MVP) |
| `plugins/operators/spark_submit_operator.py` | Custom SparkSubmit operator |

### `warehouse/`
| File | Role |
|------|------|
| `src/loaders/postgres_loader.py` | Reads from MinIO/Spark, writes to PostgreSQL |
| `schemas/init.sql` | DDL for `staging`, `marts` schemas |
| `jobs/run_warehouse_load.py` | Entry point for load job |

### `dbt/`
| File | Role |
|------|------|
| `dbt_project.yml` | Project config, model paths |
| `profiles.yml` | PostgreSQL connection |
| `models/staging/*.sql` | 1:1 with warehouse staging tables |
| `models/marts/**/*.sql` | Fact/dim models for reporting |

### `dashboards/`
| File | Role |
|------|------|
| `metabase/docker-compose.yml` | Standalone Metabase for local BI |
| `config/datasource.yml` | PostgreSQL connection for Metabase |

### `shared/`
| File | Role |
|------|------|
| `retail_lakehouse/config/settings.py` | Env-based config (paths, credentials) |
| `retail_lakehouse/schemas/retail_schemas.py` | Python dict schemas for validation |
| `retail_lakehouse/utils/logging_utils.py` | Structured logging |
| `retail_lakehouse/utils/date_utils.py` | Date/Timezone helpers (AU) |

---

## 4. Recommended Build Order

### Phase 1: Foundation
1. Create folder structure and `.gitignore`, `LICENSE`, `README.md`
2. Add `docker-compose.yml` at root with MinIO + PostgreSQL only
3. Add `docker/scripts/init-minio-buckets.sh`, `init-postgres-schemas.sh`
4. Add `shared/src/retail_lakehouse/` with `config`, `schemas`, `utils`
5. Add `data/schemas/*.json` (entity schemas)
6. Add `data_generator/` with `generate_retail_data.py`
7. Add `data/scripts/seed_and_upload.sh`
8. Verify: `docker compose up`, generate data, upload to MinIO

### Phase 2: Ingestion
1. Implement `ingestion/src/connectors/minio_client.py`
2. Implement `ingestion/src/loaders/file_loader.py`
3. Implement `ingestion/jobs/run_ingestion.py`
4. Add ingestion to docker-compose (optional service)
5. Verify: Raw data lands in MinIO `raw/` bucket

### Phase 3: Spark Bronze
1. Add Spark to `docker-compose.yml` (spark-submit or standalone)
2. Implement `spark_jobs/lib/schemas.py` (Bronze schemas)
3. Implement `spark_jobs/lib/config.py`
4. Implement Bronze jobs: `ingest_sales`, `ingest_inventory`, etc.
5. Verify: Bronze Parquet in MinIO `bronze/`

### Phase 4: Spark Silver
1. Implement `spark_jobs/lib/quality/validators.py`
2. Implement Silver schemas in `spark_jobs/lib/schemas.py`
3. Implement Silver jobs: `transform_sales`, etc.
4. Add incremental logic in `spark_jobs/lib/utils/incremental.py` (optional)
5. Verify: Silver Parquet in MinIO `silver/`

### Phase 5: Spark Gold
1. Implement Gold schemas
2. Implement Gold jobs: `build_sales_mart`, `build_inventory_mart`, `build_reporting_mart`
3. Verify: Gold Parquet in MinIO `gold/`

### Phase 6: Warehouse Load
1. Implement `warehouse/schemas/init.sql`
2. Implement `warehouse/src/connectors/postgres_client.py`
3. Implement `warehouse/src/loaders/postgres_loader.py` (Spark JDBC or pandas)
4. Implement `warehouse/jobs/run_warehouse_load.py`
5. Verify: Gold data in PostgreSQL

### Phase 7: Orchestration
1. Add Airflow to `docker-compose.yml`
2. Implement `airflow/plugins/operators/spark_submit_operator.py`
3. Implement `airflow/dags/retail_lakehouse_pipeline.py` (single DAG for MVP)
4. Wire task dependencies within the DAG
5. Verify: Full pipeline runs via Airflow

### Phase 8: dbt
1. Initialize `dbt/retail_analytics/` project
2. Configure `profiles.yml` for PostgreSQL
3. Implement staging models
4. Implement intermediate models
5. Implement marts (sales, inventory, reporting)
6. Add `06_dbt_dag` to run `dbt build`
7. Verify: Marts in PostgreSQL

### Phase 9: Dashboards
1. Add Metabase to `docker-compose` or `dashboards/metabase/`
2. Configure PostgreSQL datasource
3. Create sample dashboards (sales, inventory)
4. Document in `dashboards/README.md`

### Phase 10: Polish
1. Add `tests/` (unit + integration)
2. Add `.github/workflows/ci.yml`
3. Complete `docs/` (ARCHITECTURE, DATA_DICTIONARY, RUNBOOK)
4. Add `Makefile` and `scripts/setup_local.sh`, `run_full_pipeline.sh`
5. Add `assets/` with architecture diagram, screenshots
6. Final README with quickstart, architecture diagram, screenshots

---

## 5. Summary

| Phase | Deliverable |
|-------|-------------|
| 1 | Docker (MinIO, Postgres), shared libs, data generator |
| 2 | Ingestion: raw → MinIO |
| 3 | Spark Bronze |
| 4 | Spark Silver |
| 5 | Spark Gold |
| 6 | Warehouse load: Gold → PostgreSQL |
| 7 | Airflow orchestration |
| 8 | dbt models |
| 9 | Metabase dashboards |
| 10 | Tests, CI, docs, assets, polish |
