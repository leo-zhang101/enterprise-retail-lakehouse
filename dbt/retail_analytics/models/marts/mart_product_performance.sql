{{
    config(
        materialized='table',
    )
}}

with product_sales as (
    select * from {{ ref('int_product_sales') }}
),

products as (
    select * from {{ ref('stg_dim_product') }}
),

joined as (
    select
        p.product_id,
        p.product_name,
        coalesce(ps.product_category, p.product_category) as product_category,
        p.product_subcategory,
        p.brand,
        p.unit_price_aud,
        p.gross_margin_pct,
        ps.transaction_count,
        ps.total_quantity_sold,
        ps.total_revenue,
        ps.avg_quantity_per_transaction,
        ps.avg_revenue_per_transaction
    from product_sales ps
    left join products p on ps.product_id = p.product_id
)

select * from joined
