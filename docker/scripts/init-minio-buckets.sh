#!/bin/bash
# init-minio-buckets.sh
# Creates Medallion buckets (raw, bronze, silver, gold) in MinIO.
# Run manually when MinIO is up, or rely on minio-init in docker-compose.

set -e

: "${MINIO_HOST:=localhost}"
: "${MINIO_PORT:=9000}"
: "${MINIO_ROOT_USER:=minioadmin}"
: "${MINIO_ROOT_PASSWORD:=minioadmin}"

BUCKETS="raw bronze silver gold"

echo "Creating MinIO buckets (${MINIO_HOST}:${MINIO_PORT})..."

mc alias set local "http://${MINIO_HOST}:${MINIO_PORT}" "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" 2>/dev/null || true

for bucket in $BUCKETS; do
    mc mb "local/${bucket}" --ignore-existing 2>/dev/null && echo "  Created: ${bucket}" || echo "  Exists:  ${bucket}"
done

echo "Done."
