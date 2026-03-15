"""
PostgreSQL connection client for warehouse load.
"""

import os
from contextlib import contextmanager
from typing import Generator, Optional

try:
    import psycopg2
    from psycopg2 import sql
    from psycopg2.extras import execute_values
except ImportError:
    psycopg2 = None  # type: ignore
    sql = None
    execute_values = None


def _get_conn_params() -> dict:
    """Build connection params from environment."""
    return {
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "port": int(os.environ.get("POSTGRES_PORT", "5432")),
        "dbname": os.environ.get("POSTGRES_DB", "retail_warehouse"),
        "user": os.environ.get("POSTGRES_USER", "retail"),
        "password": os.environ.get("POSTGRES_PASSWORD", "retail"),
    }


@contextmanager
def get_postgres_connection() -> Generator:
    """
    Context manager for PostgreSQL connection.

    Yields:
        psycopg2 connection.
    """
    if psycopg2 is None:
        raise ImportError("psycopg2 is required. Install with: pip install psycopg2-binary")
    conn = psycopg2.connect(**_get_conn_params())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def test_connection() -> bool:
    """Test PostgreSQL connectivity. Returns True if successful."""
    try:
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return True
    except Exception:
        return False
