# Spark Jobs

PySpark jobs for the Bronze, Silver, and Gold layers of the retail lakehouse.

**Local**: MinIO (S3-compatible). **AWS**: Same code, S3 buckets; run via Glue or EMR Serverless. See [docs/AWS_PRODUCTION_MAPPING.md](../docs/AWS_PRODUCTION_MAPPING.md).

## Bronze Layer

Reads raw CSV from raw zone (MinIO or S3) and writes cleaned Parquet to Bronze.

### Paths

- **Read**: `s3a://raw/<entity>/load_date=YYYY-MM-DD/<entity>.csv`
- **Write**: `s3a://bronze/<entity>/load_date=YYYY-MM-DD/`

### Entities

- customers
- stores
- products
- promotions
- sales_transactions
- inventory_snapshots

### Bronze Responsibilities

- Read raw CSV from MinIO
- Cast columns to expected schema (dates/timestamps standardized)
- Add ingestion metadata: `ingestion_timestamp`, `load_date`, `source_file`
- Remove duplicate rows (by primary key)
- Write Parquet to bronze zone

### S3A / Hadoop AWS Support (Local Development)

Spark must have S3A and Hadoop AWS JARs to read/write MinIO. Options:

**Option 1: Spark with bundled Hadoop (recommended for local)**

```bash
# Install pyspark (includes Hadoop)
pip install pyspark

# Spark 3.5+ includes hadoop-aws. For older Spark, add packages:
spark-submit --packages org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \
  spark_jobs/jobs/bronze/ingest_customers.py --load-date 2025-03-13
```

**Option 2: Add packages to spark-submit**

```bash
spark-submit \
  --packages org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \
  spark_jobs/jobs/bronze/ingest_customers.py --load-date 2025-03-13
```

**Option 3: Use Spark installed via Homebrew or system package**

Ensure `SPARK_HOME` is set and that `$SPARK_HOME/jars` includes `hadoop-aws-*.jar` and `aws-java-sdk-bundle-*.jar`. Download from Maven if missing.

### Usage

```bash
# From project root; load_date must match ingested raw data
export PYTHONPATH=.

# Ingest a single entity
spark-submit spark_jobs/jobs/bronze/ingest_customers.py --load-date 2025-03-13

# Or with packages (if S3A not bundled)
spark-submit --packages org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \
  spark_jobs/jobs/bronze/ingest_customers.py --load-date 2025-03-13
```

---

## Silver Layer

Reads Bronze parquet from MinIO, applies business cleaning and standardization, writes curated Silver parquet.

### Paths

- **Read**: `s3a://bronze/<entity>/load_date=YYYY-MM-DD/`
- **Write**: `s3a://silver/<entity>/load_date=YYYY-MM-DD/`

### Silver Responsibilities

- Read Bronze parquet from MinIO
- Apply business cleaning and standardization
- Handle nulls where appropriate
- Add useful business fields
- Write Parquet to silver zone

### Entity-Specific Transforms

| Entity | Transforms |
|--------|------------|
| customers | Standardize loyalty_tier (default Guest), derive is_loyalty_member |
| stores | Trim text, uppercase state, normalize city/store_name (initcap) |
| products | Trim text, derive gross_margin_aud, gross_margin_pct, is_margin_available |
| promotions | Standardize discount_type, derive promotion_active_days (null-safe, non-negative) |
| sales_transactions | Derive amounts, DQ guards (quantity>0, unit_price>0, net_sales≥0, discount_rate∈[0,1]), is_valid_sale_record, enrich via joins (product_category, store_state, promotion_name, discount_type) |
| inventory_snapshots | Derive low_inventory_flag (threshold from `LOW_INVENTORY_THRESHOLD`, default 10) |

### Usage

```bash
# Run after Bronze; load_date must match
spark-submit spark_jobs/jobs/silver/transform_customers.py --load-date 2025-03-13
```

---

## Gold Layer

Reads Silver parquet from MinIO, builds analytics-ready datasets, writes Gold parquet.

### Paths

- **Read**: `s3a://silver/<entity>/load_date=YYYY-MM-DD/`
- **Write**: `s3a://gold/<table>/load_date=YYYY-MM-DD/`

### Gold Tables

| Table | Grain | Write strategy | Purpose |
|-------|-------|----------------|---------|
| dim_product | One row per product | Full refresh | Product master |
| dim_store | One row per store | Full refresh | Store master |
| dim_customer | One row per customer | Full refresh | Customer master |
| fact_sales | One row per sale transaction | **Incremental partition** | Transaction-level sales fact |
| fact_inventory_daily | One row per product/store/snapshot date | **Incremental partition** | Daily inventory fact |
| fct_store_sales_daily | One row per store per sale date | Full refresh | Store daily sales summary mart |
| fct_product_performance | One row per product | Full refresh | Product performance summary mart |
| fct_promotion_effectiveness | One row per promotion | Full refresh | Promotion effectiveness mart |

**Partition-based incremental processing** (fact_sales, fact_inventory_daily): Reads Silver for load_date only; writes with `partitionBy(load_date)` and dynamic partition overwrite; only the load_date partition is replaced; idempotent for re-runs.

### Usage

```bash
# Run after Silver; load_date must match
spark-submit spark_jobs/jobs/gold/build_dim_product.py --load-date 2025-03-13
spark-submit spark_jobs/jobs/gold/build_fact_sales.py --load-date 2025-03-13
# ... or run all Gold builds
```

---

### Environment

**Local (MinIO)** — set in `.env`:

- `MINIO_ENDPOINT` (default: http://localhost:9000)
- `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`
- `LOW_INVENTORY_THRESHOLD` (default: 10)

**AWS** — set `STORAGE_BACKEND=s3` and optionally:

- `S3_BUCKET_RAW`, `S3_BUCKET_BRONZE`, `S3_BUCKET_SILVER`, `S3_BUCKET_GOLD`
- `AWS_REGION` (default: ap-southeast-2)

Same s3a:// paths; Spark uses default AWS credentials. See [docs/AWS_PRODUCTION_MAPPING.md](../docs/AWS_PRODUCTION_MAPPING.md).

### Module Structure

```
spark_jobs/
├── lib/
│   ├── config.py           # MinIO paths, bucket names
│   ├── schemas.py          # Bronze StructType schemas
│   ├── bronze_ingest.py    # Shared Bronze ingestion logic
│   ├── silver_transform.py # Shared Silver transform logic
│   ├── gold_transform.py   # Shared Gold build logic
│   └── utils/
│       └── spark_session.py # SparkSession with S3A config
├── jobs/
│   ├── bronze/
│   │   ├── ingest_customers.py
│   │   ├── ingest_stores.py
│   │   ├── ingest_products.py
│   │   ├── ingest_promotions.py
│   │   ├── ingest_sales_transactions.py
│   │   └── ingest_inventory_snapshots.py
│   └── silver/
│       ├── transform_customers.py
│       ├── transform_stores.py
│       ├── transform_products.py
│       ├── transform_promotions.py
│       ├── transform_sales_transactions.py
│       └── transform_inventory_snapshots.py
│   └── gold/
│       ├── build_dim_product.py
│       ├── build_dim_store.py
│       ├── build_dim_customer.py
│       ├── build_fact_sales.py
│       ├── build_fact_inventory_daily.py
│       ├── build_fct_store_sales_daily.py
│       ├── build_fct_product_performance.py
│       └── build_fct_promotion_effectiveness.py
└── README.md
```
