"""
Ingestion configuration.
"""

from pathlib import Path

from retail_lakehouse.config.settings import get_settings
from retail_lakehouse.config.constants import ENTITIES, BUCKETS


def get_ingestion_config() -> dict:
    """Return config for ingestion (paths, MinIO, entities)."""
    settings = get_settings()
    return {
        "raw_dir": settings["raw_dir"],
        "minio_endpoint": settings["minio_endpoint"],
        "minio_access_key": settings["minio_access_key"],
        "minio_secret_key": settings["minio_secret_key"],
        "minio_secure": settings["minio_secure"],
        "raw_bucket": BUCKETS["raw"],
        "entities": list(ENTITIES),
    }


def get_local_entity_path(raw_dir: Path, entity: str) -> Path:
    """Return path to entity folder under data/raw/."""
    return raw_dir / entity


def get_entity_filename(entity: str) -> str:
    """Return expected CSV filename for entity."""
    return f"{entity}.csv"
