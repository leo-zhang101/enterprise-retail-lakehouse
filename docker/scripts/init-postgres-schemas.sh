#!/bin/bash
# init-postgres-schemas.sh
# Creates staging and marts schemas for dbt.
# Runs automatically via docker-entrypoint-initdb.d on first Postgres start.

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE SCHEMA IF NOT EXISTS staging;
    CREATE SCHEMA IF NOT EXISTS marts;
    GRANT ALL ON SCHEMA staging TO $POSTGRES_USER;
    GRANT ALL ON SCHEMA marts TO $POSTGRES_USER;
EOSQL
