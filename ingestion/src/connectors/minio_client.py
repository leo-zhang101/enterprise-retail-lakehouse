"""
MinIO (S3-compatible) client for the retail lakehouse.
"""

from pathlib import Path
from typing import Optional

from minio import Minio
from minio.error import S3Error

from retail_lakehouse.utils.logging_utils import get_logger

logger = get_logger(__name__)


def get_minio_client(
    endpoint: str,
    access_key: str,
    secret_key: str,
    secure: bool = False,
) -> Minio:
    """Create and return a MinIO client."""
    # Parse endpoint: http://localhost:9000 -> host:port
    url = endpoint.replace("https://", "").replace("http://", "")
    if "/" in url:
        url = url.split("/")[0]
    return Minio(
        url,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure,
    )


def ensure_bucket_exists(client: Minio, bucket: str) -> bool:
    """Create bucket if it does not exist. Return True on success."""
    try:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
            logger.info("Created bucket: %s", bucket)
        return True
    except S3Error as e:
        logger.error("Failed to ensure bucket %s: %s", bucket, e)
        return False


def upload_file(
    client: Minio,
    bucket: str,
    object_name: str,
    file_path: Path,
) -> bool:
    """
    Upload a local file to MinIO.

    Returns True on success, False on failure.
    """
    try:
        client.fput_object(bucket, object_name, str(file_path))
        logger.debug("Uploaded %s -> %s/%s", file_path, bucket, object_name)
        return True
    except S3Error as e:
        logger.error("Upload failed %s -> %s/%s: %s", file_path, bucket, object_name, e)
        return False


def object_exists(client: Minio, bucket: str, object_name: str) -> bool:
    """Verify that an object exists in MinIO. Returns True if found."""
    try:
        client.stat_object(bucket, object_name)
        return True
    except S3Error:
        return False
