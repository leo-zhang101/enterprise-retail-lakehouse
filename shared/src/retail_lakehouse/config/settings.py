"""
Environment-based configuration for the retail lakehouse platform.
"""

import os
from pathlib import Path
from functools import lru_cache

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _str(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def _int(key: str, default: int = 0) -> int:
    val = os.environ.get(key)
    return int(val) if val else default


@lru_cache(maxsize=1)
def get_settings() -> dict:
    """Load and cache environment-based settings."""
    project_root = Path(__file__).resolve().parents[4]
    data_dir = Path(_str("DATA_DIR", str(project_root / "data")))
    raw_dir = data_dir / "raw"

    return {
        # Paths
        "project_root": project_root,
        "data_dir": data_dir,
        "raw_dir": raw_dir,
        # MinIO
        "minio_endpoint": _str("MINIO_ENDPOINT", "http://localhost:9000"),
        "minio_access_key": _str("MINIO_ACCESS_KEY", _str("MINIO_ROOT_USER", "minioadmin")),
        "minio_secret_key": _str("MINIO_SECRET_KEY", _str("MINIO_ROOT_PASSWORD", "minioadmin")),
        "minio_secure": _str("MINIO_SECURE", "false").lower() == "true",
        # PostgreSQL
        "postgres_host": _str("POSTGRES_HOST", "localhost"),
        "postgres_port": _int("POSTGRES_PORT", 5432),
        "postgres_user": _str("POSTGRES_USER", "retail"),
        "postgres_password": _str("POSTGRES_PASSWORD", "retail"),
        "postgres_db": _str("POSTGRES_DB", "retail_warehouse"),
    }


def get_raw_path(entity: str) -> Path:
    """Return the raw data directory for an entity."""
    settings = get_settings()
    return settings["raw_dir"] / entity
