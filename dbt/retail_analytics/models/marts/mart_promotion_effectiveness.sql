{{
    config(
        materialized='table',
    )
}}

with promotion_sales as (
    select * from {{ ref('int_promotion_sales') }}
),

enriched as (
    select
        promotion_id,
        promotion_name,
        discount_type,
        transaction_count,
        total_quantity_sold,
        total_revenue,
        total_discount_given,
        round(
            case when total_revenue > 0
            then (total_discount_given / total_revenue) * 100
            else null
            end,
            2
        ) as discount_pct_of_revenue
    from promotion_sales
)

select * from enriched
