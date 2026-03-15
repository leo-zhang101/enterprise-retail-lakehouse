# Interview Talking Points

Practical, realistic talking points for discussing this project in Data Engineer interviews.

---

## Architecture decisions

- **Why Medallion?** Industry-standard pattern for lakehouse; clear separation of raw, cleaned, and business-ready data. Easy to explain to stakeholders and aligns with Databricks/Delta Lake terminology.
- **Why MinIO locally?** S3-compatible API; same Spark s3a:// paths work in AWS. No cloud cost for development; Docker Compose keeps the stack portable. Set `STORAGE_BACKEND=s3` and bucket env vars to point at AWS S3.
- **Why PostgreSQL for the warehouse?** Lightweight, widely used for analytics warehouses and dbt. Good fit for marts and BI tools. In AWS, RDS PostgreSQL; Redshift for petabyte-scale.

---

## AWS production mapping

- **MinIO → S3**: Same s3a:// paths. Config swap via `STORAGE_BACKEND` and `S3_BUCKET_*` env vars.
- **Spark → Glue/EMR**: PySpark jobs run as Glue Jobs or EMR Serverless. Same code; point at S3.
- **Airflow → MWAA**: DAGs migrate as-is. Replace spark-submit tasks with Glue/EMR job triggers.
- **Warehouse load**: Run from MWAA or container; connect to RDS. Use `GOLD_PATH=s3://...` with s3fs for direct S3 read.

---

## Data quality

- **Silver layer**: Guards (quantity > 0, unit_price > 0, net_sales ≥ 0, discount_rate ∈ [0,1]); `is_valid_sale_record` flag. Downstream filter invalid rows.
- **dbt tests**: Unique and not-null on primary keys; relationship tests between facts and dimensions.

---

## Orchestration and incremental

- **Airflow**: Single DAG with task groups (ingestion, bronze, silver, gold, warehouse, dbt). Bronze/Silver/Gold run in parallel.
- **Partition-based incremental**: Gold fact_sales and fact_inventory_daily use dynamic partition overwrite; warehouse uses delete-by-load_date plus upsert. Idempotent for re-runs.

---

## Trade-offs and limitations

- **Sync step (local)**: Gold copied from MinIO to local before warehouse load. In AWS, use s3fs for direct S3 read.
- **Spark in Airflow**: BashOperator + spark-submit locally. In AWS, GlueJobOperator or EMR triggers.
