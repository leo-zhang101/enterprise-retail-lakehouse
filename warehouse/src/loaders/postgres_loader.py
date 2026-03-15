"""
Load Gold parquet datasets into PostgreSQL staging tables.
"""

import logging
import os
from typing import Any, List, Optional

try:
    import pandas as pd
    import pyarrow.parquet as pq
except ImportError:
    pd = None
    pq = None

from warehouse.src.connectors.postgres_client import get_postgres_connection

logger = logging.getLogger(__name__)

# Gold table -> staging schema table mapping
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

# Tables using idempotent partition-based incremental loading (delete-by-load_date + upsert)
UPSERT_TABLES = {"fact_sales", "fact_inventory_daily"}


def _read_parquet(path: str) -> "pd.DataFrame":
    """Read parquet file or directory into DataFrame."""
    if pd is None or pq is None:
        raise ImportError("pandas and pyarrow required. Install with: pip install pandas pyarrow")
    return pd.read_parquet(path)


def _resolve_gold_path(gold_base: str, table: str, load_date: str) -> str:
    """Build path to Gold parquet for table and load_date. Safe for local and s3-style paths."""
    base = gold_base.rstrip("/")
    return f"{base}/{table}/load_date={load_date}"


def load_table_to_postgres(
    table: str,
    gold_base: str,
    load_date: str,
    schema: str = "staging",
) -> int:
    """
    Load a single Gold table into PostgreSQL staging.

    Args:
        table: Gold table name (e.g. dim_product).
        gold_base: Base path to Gold parquet (local or S3).
        load_date: Load date (YYYY-MM-DD).
        schema: Target schema (default staging).

    Returns:
        Number of rows loaded.

    Raises:
        FileNotFoundError: If Gold parquet not found.
    """
    path = _resolve_gold_path(gold_base, table, load_date)
    if not (path.startswith("s3://") or path.startswith("s3a://")) and not os.path.exists(path):
        raise FileNotFoundError(f"Gold parquet not found: {path}")

    logger.info("Loading %s from %s", table, path)
    df = _read_parquet(path)

    if df.empty:
        logger.warning("Table %s is empty, skipping", table)
        return 0

    # Ensure load_date column for consistency
    if "load_date" not in df.columns:
        df["load_date"] = load_date

    from psycopg2.extras import execute_values

    columns = list(df.columns)
    cols_str = ", ".join(f'"{c}"' for c in columns)
    rows = [tuple(row) for row in df.values]

    if table in UPSERT_TABLES:
        # Idempotent partition-based incremental: delete-by-load_date then upsert
        conflict_col = "sale_id" if table == "fact_sales" else "snapshot_id"
        update_set = ", ".join(f'"{c}" = EXCLUDED."{c}"' for c in columns if c != conflict_col)
        insert_sql = (
            f'INSERT INTO "{schema}"."{table}" ({cols_str}) VALUES %s '
            f'ON CONFLICT ("{conflict_col}") DO UPDATE SET {update_set}'
        )
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f'DELETE FROM "{schema}"."{table}" WHERE load_date = %s', (load_date,))
                execute_values(cur, insert_sql, rows, page_size=1000)
    else:
        # Full refresh: truncate then insert
        insert_sql = f'INSERT INTO "{schema}"."{table}" ({cols_str}) VALUES %s'
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f'TRUNCATE TABLE "{schema}"."{table}"')
                execute_values(cur, insert_sql, rows, page_size=1000)

    count = len(df)
    logger.info("Loaded %d rows into %s.%s", count, schema, table)
    return count


def run_warehouse_load(
    load_date: str,
    gold_base: Optional[str] = None,
    tables: Optional[List[str]] = None,
) -> dict[str, int]:
    """
    Load all Gold tables into PostgreSQL staging.

    Args:
        load_date: Load date (YYYY-MM-DD).
        gold_base: Base path to Gold parquet. Defaults to GOLD_PATH env or ./gold.
        tables: Tables to load. Defaults to all GOLD_TABLES.

    Returns:
        Dict of table -> count loaded.
    """
    gold_base = gold_base or os.environ.get("GOLD_PATH", "./gold")
    tables = tables or GOLD_TABLES

    results: dict[str, int] = {}
    for table in tables:
        try:
            count = load_table_to_postgres(table, gold_base, load_date)
            results[table] = count
        except Exception as e:
            logger.exception("Failed to load %s: %s", table, e)
            raise
    return results
