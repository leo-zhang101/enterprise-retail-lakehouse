# Airflow Orchestration

Production-style DAG that orchestrates the retail lakehouse pipeline end-to-end.

**Local**: Self-hosted Airflow. **AWS**: Same DAGs; migrate to Amazon MWAA. Replace spark-submit with Glue/EMR job triggers. See [docs/AWS_PRODUCTION_MAPPING.md](../docs/AWS_PRODUCTION_MAPPING.md).

## Pipeline Order

1. **Ingestion** — Upload raw CSV to MinIO
2. **Bronze** — Spark ingest (6 entities)
3. **Silver** — Spark transform (6 entities)
4. **Gold** — Spark build (8 tables)
5. **Sync Gold** — Copy Gold parquet from MinIO to local (for warehouse loader)
6. **Warehouse load** — Load Gold into PostgreSQL staging
7. **dbt** — Run and test

## Prerequisites

- Airflow 2.x
- Spark (for Bronze/Silver/Gold)
- MinIO client (`mc`) configured for sync step
- PostgreSQL with staging tables
- dbt-core and dbt-postgres

## Configuration

### Airflow Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `retail_project_root` | `/app` | Project root path (where ingestion, spark_jobs, warehouse, dbt live) |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `SPARK_PACKAGES` | Hadoop AWS packages for spark-submit (optional if bundled) |
| `GOLD_PATH` | Local path for Gold parquet after sync (default: `/tmp/gold`) |
| `POSTGRES_*` | PostgreSQL connection for warehouse and dbt |
| `MINIO_*` | MinIO credentials (local) |
| `STORAGE_BACKEND` | `minio` (local) or `s3` (AWS) |

### dbt Profile (Airflow Worker)

The dbt tasks set `DBT_PROFILES_DIR` to the dbt project directory so `profiles.yml` is found during DAG execution. Ensure the Airflow worker has:

- `profiles.yml` at `dbt/retail_analytics/profiles.yml` (in the mounted project)
- `POSTGRES_*` env vars set for the warehouse connection

### MinIO Sync

The `sync_gold_from_minio` task clears `GOLD_PATH`, then copies Gold parquet from MinIO to avoid path nesting or stale data on repeated runs. Ensure:

1. `mc` is installed in the Airflow worker
2. MinIO alias is configured: `mc alias set minio http://<minio-host>:9000 <user> <password>`
3. `GOLD_PATH` is writable by the Airflow worker

**Alternative**: If using `s3fs` and S3-compatible access, you can replace the sync task with a no-op and set `GOLD_PATH=s3://gold/` for the warehouse loader (requires `s3fs` in the warehouse container).

## Local Docker Usage

1. Add Airflow to your Docker setup (e.g. `docker-compose` with `apache/airflow` image)
2. Mount the project: `-v $(pwd):/app`
3. Mount the DAGs folder: `-v $(pwd)/airflow/dags:/opt/airflow/dags`
4. Set `retail_project_root` to `/app` (or your mount path)
5. Ensure Spark, `mc`, and dbt are available in the worker (or use separate executor for Spark)

### Example docker-compose addition

```yaml
airflow:
  image: apache/airflow:2.7.0
  volumes:
    - .:/app
    - ./airflow/dags:/opt/airflow/dags
  environment:
    AIRFLOW__CORE__LOAD_EXAMPLES: "false"
    PROJECT_ROOT: /app
  # Add Spark, mc, dbt to the image or use a custom image
```

## Triggering the DAG

- **Manual**: Trigger with config `{"load_date": "2025-03-13"}` to override the default (execution date)
- **Scheduled**: Set `schedule` (e.g. `@daily`) and use execution date as load_date

## Task Groups

Tasks **inside** Bronze, Silver, and Gold groups run **in parallel** (e.g. all 6 Bronze ingest tasks run concurrently).

| Group | Tasks |
|-------|-------|
| ingestion | run_ingestion |
| bronze | ingest_customers, ingest_stores, ingest_products, ingest_promotions, ingest_sales_transactions, ingest_inventory_snapshots (parallel) |
| silver | transform_* (6 entities, parallel) |
| gold | build_* (8 tables, parallel) |
| dbt | dbt_run, dbt_test |

## Retry Configuration

- Default: 2 retries, 2-minute delay
- Adjust via `default_args` in the DAG
