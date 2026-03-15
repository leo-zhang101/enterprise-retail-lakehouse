"""
Retail Lakehouse Pipeline DAG.

Orchestrates end-to-end: ingestion -> bronze -> silver -> gold -> warehouse load -> dbt.
"""

from datetime import datetime, timedelta
import os

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable

# Config
PROJECT_ROOT = Variable.get("retail_project_root", default_var="/app")
SPARK_PACKAGES = os.environ.get(
    "SPARK_PACKAGES",
    "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262",
)
GOLD_PATH = os.environ.get("GOLD_PATH", "/tmp/gold")
DBT_PROJECT = os.path.join(PROJECT_ROOT, "dbt/retail_analytics")

default_args = {
    "owner": "retail",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

BRONZE_ENTITIES = [
    "customers",
    "stores",
    "products",
    "promotions",
    "sales_transactions",
    "inventory_snapshots",
]
SILVER_ENTITIES = BRONZE_ENTITIES
GOLD_TABLES = [
    "dim_product",
    "dim_store",
    "dim_customer",
    "fact_sales",
    "fact_inventory_daily",
    "fct_store_sales_daily",
    "fct_product_performance",
    "fct_promotion_effectiveness",
]


def _spark_submit_cmd(script: str, load_date: str) -> str:
    """Build spark-submit command with optional packages."""
    base = f"spark-submit --packages {SPARK_PACKAGES}" if SPARK_PACKAGES else "spark-submit"
    return f"cd {PROJECT_ROOT} && PYTHONPATH=. {base} {script} --load-date {load_date}"


with DAG(
    dag_id="retail_lakehouse_pipeline",
    default_args=default_args,
    description="End-to-end retail lakehouse: ingestion, bronze, silver, gold, warehouse, dbt",
    schedule=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["retail", "lakehouse"],
    params={"load_date": None},
) as dag:

    load_date = "{{ params.load_date or ds }}"

    # 1. Ingestion
    with TaskGroup("ingestion", tooltip="Upload raw CSV to MinIO") as ingestion_group:
        ingest = BashOperator(
            task_id="run_ingestion",
            bash_command=f"cd {PROJECT_ROOT} && PYTHONPATH=. python -m ingestion.jobs.run_ingestion --load-date {load_date}",
        )

    # 2. Bronze
    with TaskGroup("bronze", tooltip="Spark Bronze ingestion") as bronze_group:
        bronze_tasks = []
        for entity in BRONZE_ENTITIES:
            script = f"{PROJECT_ROOT}/spark_jobs/jobs/bronze/ingest_{entity}.py"
            t = BashOperator(
                task_id=f"ingest_{entity}",
                bash_command=_spark_submit_cmd(script, load_date),
            )
            bronze_tasks.append(t)

    # 3. Silver
    with TaskGroup("silver", tooltip="Spark Silver transform") as silver_group:
        silver_tasks = []
        for entity in SILVER_ENTITIES:
            script = f"{PROJECT_ROOT}/spark_jobs/jobs/silver/transform_{entity}.py"
            t = BashOperator(
                task_id=f"transform_{entity}",
                bash_command=_spark_submit_cmd(script, load_date),
            )
            silver_tasks.append(t)

    # 4. Gold
    with TaskGroup("gold", tooltip="Spark Gold build") as gold_group:
        gold_tasks = []
        for table in GOLD_TABLES:
            name = table.replace("_", "-")
            script = f"{PROJECT_ROOT}/spark_jobs/jobs/gold/build_{table}.py"
            t = BashOperator(
                task_id=f"build_{name}",
                bash_command=_spark_submit_cmd(script, load_date),
            )
            gold_tasks.append(t)

    # 5. Sync Gold from MinIO (clear target first to avoid nesting/stale data)
    sync_gold = BashOperator(
        task_id="sync_gold_from_minio",
        bash_command=f"rm -rf {GOLD_PATH} && mkdir -p {GOLD_PATH} && mc cp -r minio/gold/ {GOLD_PATH}",
    )

    # 6. Warehouse load
    warehouse_load = BashOperator(
        task_id="warehouse_load",
        bash_command=f"cd {PROJECT_ROOT} && PYTHONPATH=. GOLD_PATH={GOLD_PATH} python warehouse/jobs/run_warehouse_load.py --load-date {load_date}",
    )

    # 7. dbt (DBT_PROFILES_DIR so dbt finds profiles.yml in project)
    with TaskGroup("dbt", tooltip="dbt run and test") as dbt_group:
        dbt_run = BashOperator(
            task_id="dbt_run",
            bash_command=f"cd {DBT_PROJECT} && DBT_PROFILES_DIR={DBT_PROJECT} dbt run",
        )
        dbt_test = BashOperator(
            task_id="dbt_test",
            bash_command=f"cd {DBT_PROJECT} && DBT_PROFILES_DIR={DBT_PROJECT} dbt test",
        )
        dbt_run >> dbt_test

    # Dependencies
    ingestion_group >> bronze_group >> silver_group >> gold_group
    gold_group >> sync_gold >> warehouse_load >> dbt_group
