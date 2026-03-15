# Resume-Ready Project Description

**Australian Data Engineer style** — concise, metrics-oriented, recruiter-friendly.

---

## One-liner

Built an end-to-end retail analytics lakehouse (Medallion architecture) with PySpark, Airflow, dbt, and PostgreSQL—locally runnable, AWS-mappable, with partition-based incremental processing and production-style orchestration.

---

## Bullet points (pick 2–3)

- Designed and implemented an **AWS-aligned Medallion lakehouse** (Bronze/Silver/Gold) for Australian retail data using PySpark; S3-compatible paths (MinIO locally, S3 in production); partition-based incremental processing for fact tables; 6 entity types with schema enforcement and data quality guards.

- Orchestrated the full pipeline with **Apache Airflow** and **dbt**—ingestion, Spark jobs, warehouse load, dbt run/test—with parallel task groups, parameterised load dates, and idempotent partition-based incremental loading for facts.

- Built **dbt models** (staging, intermediate, marts) on PostgreSQL with primary-key and relationship tests; produced 3 reporting marts; documented AWS production mapping (S3, Glue/EMR, MWAA, RDS).

- Delivered a **local-first, AWS-mappable** stack (Docker Compose) with config-driven storage backend (MinIO/S3); suitable for development and portfolio demos; same design maps to S3, Glue, MWAA, RDS.
