{{
    config(
        materialized='table',
    )
}}

with daily_sales as (
    select * from {{ ref('int_sales_daily') }}
),

stores as (
    select * from {{ ref('stg_dim_store') }}
),

joined as (
    select
        d.store_id,
        s.store_name,
        s.store_city,
        s.store_state,
        d.sale_date,
        d.transaction_count,
        d.total_quantity_sold,
        d.gross_sales_amount,
        d.net_sales_amount,
        d.total_discount_aud
    from daily_sales d
    left join stores s on d.store_id = s.store_id
)

select * from joined
