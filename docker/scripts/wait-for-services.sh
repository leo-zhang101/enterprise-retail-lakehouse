#!/bin/bash
# wait-for-services.sh
# Waits for MinIO and PostgreSQL to accept connections.
#
# Requires: nc (netcat) — install via: brew install netcat (macOS) or apt install netcat-openbsd (Debian/Ubuntu)
# Usage: ./docker/scripts/wait-for-services.sh [timeout_seconds]

set -e

TIMEOUT="${1:-60}"
MINIO_HOST="${MINIO_HOST:-localhost}"
MINIO_PORT="${MINIO_PORT:-9000}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

wait_for_port() {
    local host=$1 port=$2 name=$3
    local elapsed=0
    while ! nc -z "$host" "$port" 2>/dev/null; do
        sleep 2
        elapsed=$((elapsed + 2))
        if [ "$elapsed" -ge "$TIMEOUT" ]; then
            echo "Timeout waiting for $name at $host:$port"
            exit 1
        fi
        echo "Waiting for $name ($host:$port)..."
    done
    echo "$name is ready."
}

wait_for_port "$MINIO_HOST" "$MINIO_PORT" "MinIO"
wait_for_port "$POSTGRES_HOST" "$POSTGRES_PORT" "PostgreSQL"

echo "All services ready."
