# Dashboards

Recommended Metabase dashboards for the retail analytics marts. Connect Metabase to PostgreSQL and use the `marts` schema tables.

## Prerequisites

- PostgreSQL with dbt marts built (`mart_store_sales_daily`, `mart_product_performance`, `mart_promotion_effectiveness`)
- Metabase installed (Docker or standalone)
- Datasource: PostgreSQL `retail_warehouse`, schema `marts`

---

## Dashboard 1: Store Performance

**Purpose**: Daily sales performance by store and region.

**Tables**: `mart_store_sales_daily`

| Chart | Type | Dimensions | Metrics |
|-------|------|------------|---------|
| Net sales by date | Line | sale_date | net_sales_amount |
| Net sales by store | Bar | store_name, store_state | net_sales_amount |
| Transaction count by store | Table | store_name, store_city, store_state | transaction_count, total_quantity_sold |
| Top stores by revenue | Bar (horizontal) | store_name | net_sales_amount |

**Filters**: sale_date (date range), store_state

---

## Dashboard 2: Product Performance

**Purpose**: Product-level revenue, volume, and margin analysis.

**Tables**: `mart_product_performance`

| Chart | Type | Dimensions | Metrics |
|-------|------|------------|---------|
| Revenue by category | Bar | product_category | total_revenue |
| Top products by revenue | Table | product_name, product_category, brand | total_revenue, total_quantity_sold |
| Avg revenue per transaction | Bar | product_category | avg_revenue_per_transaction |
| Margin overview | Table | product_name, product_category | gross_margin_pct, unit_price_aud |

**Filters**: product_category, brand

---

## Dashboard 3: Promotion Effectiveness

**Purpose**: Promotion ROI and discount impact.

**Tables**: `mart_promotion_effectiveness`

| Chart | Type | Dimensions | Metrics |
|-------|------|------------|---------|
| Revenue by promotion | Bar | promotion_name | total_revenue |
| Discount vs revenue | Scatter / Table | promotion_name | total_discount_given, total_revenue |
| Discount % of revenue | Bar | promotion_name | discount_pct_of_revenue |
| Units sold by promotion | Table | promotion_name, discount_type | total_quantity_sold, transaction_count |

**Filters**: discount_type
