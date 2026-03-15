# Enterprise Retail Lakehouse Platform — Common commands

.PHONY: up down logs verify env clean ps help

help:
	@echo "Enterprise Retail Lakehouse Platform"
	@echo ""
	@echo "  make up      - Start MinIO + PostgreSQL"
	@echo "  make down    - Stop all services"
	@echo "  make clean   - Stop services and remove volumes"
	@echo "  make ps      - List running services"
	@echo "  make logs    - Tail service logs"
	@echo "  make verify  - Verify MinIO buckets and Postgres schemas"
	@echo "  make env     - Copy .env.example to .env"

up:
	docker compose up -d

down:
	docker compose down

clean:
	docker compose down -v

ps:
	docker compose ps

logs:
	docker compose logs -f

verify:
	@echo "=== MinIO buckets ==="
	@docker compose run --rm minio-init sh -c "mc alias set minio http://minio:9000 \$${MINIO_ROOT_USER} \$${MINIO_ROOT_PASSWORD} && mc ls minio/" 2>/dev/null || echo "MinIO not running"
	@echo ""
	@echo "=== PostgreSQL schemas ==="
	@docker compose exec postgres psql -U $${POSTGRES_USER:-retail} -d $${POSTGRES_DB:-retail_warehouse} -c "\dn" 2>/dev/null || echo "Postgres not running"

env:
	cp -n .env.example .env 2>/dev/null || cp .env.example .env
	@echo "Created .env from .env.example"
