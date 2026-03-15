-- Warehouse schema initialization
-- Staging: raw load from Gold parquet (upsert-ready)
-- Marts: analytics-ready tables (optional materialized views or final tables)
-- Run after PostgreSQL is up; staging/marts schemas created by docker init.

-- =============================================================================
-- STAGING TABLES (load Gold parquet into these; truncate-and-load or upsert)
-- =============================================================================

-- dim_product: one row per product
CREATE TABLE IF NOT EXISTS staging.dim_product (
    product_id VARCHAR(64) PRIMARY KEY,
    product_name VARCHAR(256),
    category VARCHAR(128),
    subcategory VARCHAR(128),
    brand VARCHAR(128),
    unit_price_aud DOUBLE PRECISION,
    cost_aud DOUBLE PRECISION,
    gross_margin_aud DOUBLE PRECISION,
    gross_margin_pct DOUBLE PRECISION,
    is_margin_available BOOLEAN,
    load_date DATE
);

-- dim_store: one row per store
CREATE TABLE IF NOT EXISTS staging.dim_store (
    store_id VARCHAR(64) PRIMARY KEY,
    store_name VARCHAR(256),
    city VARCHAR(128),
    state VARCHAR(32),
    postcode VARCHAR(32),
    address VARCHAR(512),
    load_date DATE
);

-- dim_customer: one row per customer
CREATE TABLE IF NOT EXISTS staging.dim_customer (
    customer_id VARCHAR(64) PRIMARY KEY,
    first_name VARCHAR(128),
    last_name VARCHAR(128),
    email VARCHAR(256),
    loyalty_tier VARCHAR(32),
    is_loyalty_member BOOLEAN,
    load_date DATE
);

-- fact_sales: one row per sale transaction
CREATE TABLE IF NOT EXISTS staging.fact_sales (
    sale_id VARCHAR(64) PRIMARY KEY,
    product_id VARCHAR(64),
    store_id VARCHAR(64),
    customer_id VARCHAR(64),
    promotion_id VARCHAR(64),
    quantity INTEGER,
    unit_price_aud DOUBLE PRECISION,
    discount_aud DOUBLE PRECISION,
    gross_sales_amount DOUBLE PRECISION,
    net_sales_amount DOUBLE PRECISION,
    discount_rate DOUBLE PRECISION,
    sale_date DATE,
    sale_timestamp TIMESTAMP,
    product_category VARCHAR(128),
    store_state VARCHAR(32),
    promotion_name VARCHAR(256),
    discount_type VARCHAR(64),
    is_valid_sale_record BOOLEAN,
    is_discounted BOOLEAN,
    is_member_sale BOOLEAN,
    load_date DATE
);

CREATE INDEX IF NOT EXISTS idx_fact_sales_store_date ON staging.fact_sales (store_id, sale_date);
CREATE INDEX IF NOT EXISTS idx_fact_sales_product ON staging.fact_sales (product_id);
CREATE INDEX IF NOT EXISTS idx_fact_sales_promotion ON staging.fact_sales (promotion_id);

-- fact_inventory_daily: one row per product per store per snapshot date
CREATE TABLE IF NOT EXISTS staging.fact_inventory_daily (
    snapshot_id VARCHAR(64) PRIMARY KEY,
    product_id VARCHAR(64),
    store_id VARCHAR(64),
    quantity_on_hand INTEGER,
    snapshot_date DATE,
    low_inventory_flag BOOLEAN,
    load_date DATE
);

CREATE INDEX IF NOT EXISTS idx_fact_inv_product_store ON staging.fact_inventory_daily (product_id, store_id);

-- fct_store_sales_daily: one row per store per sale date
CREATE TABLE IF NOT EXISTS staging.fct_store_sales_daily (
    store_id VARCHAR(64),
    sale_date DATE,
    transaction_count BIGINT,
    total_quantity_sold BIGINT,
    gross_sales_amount DOUBLE PRECISION,
    net_sales_amount DOUBLE PRECISION,
    total_discount_aud DOUBLE PRECISION,
    load_date DATE,
    PRIMARY KEY (store_id, sale_date)
);

-- fct_product_performance: one row per product
CREATE TABLE IF NOT EXISTS staging.fct_product_performance (
    product_id VARCHAR(64),
    product_category VARCHAR(128),
    transaction_count BIGINT,
    total_quantity_sold BIGINT,
    total_revenue DOUBLE PRECISION,
    avg_quantity_per_transaction DOUBLE PRECISION,
    avg_revenue_per_transaction DOUBLE PRECISION,
    load_date DATE,
    PRIMARY KEY (product_id, load_date)
);

-- fct_promotion_effectiveness: one row per promotion
CREATE TABLE IF NOT EXISTS staging.fct_promotion_effectiveness (
    promotion_id VARCHAR(64),
    promotion_name VARCHAR(256),
    discount_type VARCHAR(64),
    transaction_count BIGINT,
    total_quantity_sold BIGINT,
    total_revenue DOUBLE PRECISION,
    total_discount_given DOUBLE PRECISION,
    load_date DATE,
    PRIMARY KEY (promotion_id, load_date)
);
