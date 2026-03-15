"""
File loader: upload local CSV files from data/raw/ to MinIO raw bucket.
"""

from datetime import date
from pathlib import Path
from typing import Optional

from retail_lakehouse.utils.logging_utils import get_logger

from ingestion.src.connectors.minio_client import (
    get_minio_client,
    ensure_bucket_exists,
    upload_file,
    object_exists,
)
from ingestion.src.config import get_ingestion_config, get_entity_filename

logger = get_logger(__name__)


def _validate_entity(entity: str, allowed_entities: list[str]) -> None:
    """Raise ValueError if entity is not in allowed list (fail fast)."""
    if entity not in allowed_entities:
        raise ValueError(
            f"Unsupported entity: {entity}. Allowed: {allowed_entities}"
        )


def build_object_key(entity: str, load_date: date, filename: str) -> str:
    """Build MinIO object key: entity/load_date=YYYY-MM-DD/filename."""
    load_date_str = load_date.strftime("%Y-%m-%d")
    return f"{entity}/load_date={load_date_str}/{filename}"


def load_entity_to_minio(
    entity: str,
    raw_dir: Path,
    load_date: date,
    client=None,
) -> bool:
    """
    Load a single entity's CSV from local raw_dir to MinIO raw bucket.

    Args:
        entity: Entity name (e.g. products, stores).
        raw_dir: Local data/raw directory.
        load_date: Partition date for load_date=YYYY-MM-DD.
        client: Optional pre-created MinIO client.

    Returns:
        True if upload and verification succeeded, False otherwise.
    """
    config = get_ingestion_config()
    _validate_entity(entity, config["entities"])
    filename = get_entity_filename(entity)
    local_path = raw_dir / entity / filename

    if not local_path.exists():
        logger.warning("Local file does not exist: %s", local_path)
        return False

    if client is None:
        client = get_minio_client(
            endpoint=config["minio_endpoint"],
            access_key=config["minio_access_key"],
            secret_key=config["minio_secret_key"],
            secure=config["minio_secure"],
        )

    bucket = config["raw_bucket"]
    if not ensure_bucket_exists(client, bucket):
        return False

    object_key = build_object_key(entity, load_date, filename)
    if not upload_file(client, bucket, object_key, local_path):
        return False
    if not object_exists(client, bucket, object_key):
        logger.error("Post-upload verification failed: %s/%s not found", bucket, object_key)
        return False
    logger.info("Ingested %s -> %s/%s (verified)", entity, bucket, object_key)
    return True


def load_all_entities(
    raw_dir: Optional[Path] = None,
    load_date: Optional[date] = None,
    entities: Optional[list[str]] = None,
) -> dict[str, bool]:
    """
    Load all entity CSVs from local raw_dir to MinIO raw bucket.

    Returns:
        Dict mapping entity -> success (True/False).
    """
    from datetime import date as dt_date

    config = get_ingestion_config()
    raw_dir = raw_dir or config["raw_dir"]
    load_date = load_date or dt_date.today()
    entities = entities or config["entities"]

    for entity in entities:
        _validate_entity(entity, config["entities"])

    client = get_minio_client(
        endpoint=config["minio_endpoint"],
        access_key=config["minio_access_key"],
        secret_key=config["minio_secret_key"],
        secure=config["minio_secure"],
    )

    results = {}
    for entity in entities:
        results[entity] = load_entity_to_minio(entity, raw_dir, load_date, client=client)

    return results
