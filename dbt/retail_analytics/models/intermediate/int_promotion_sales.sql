{{
    config(
        materialized='view',
    )
}}

with sales as (
    select * from {{ ref('stg_fact_sales') }}
),

promotion_sales as (
    select
        promotion_id,
        promotion_name,
        discount_type,
        count(sale_id) as transaction_count,
        sum(quantity) as total_quantity_sold,
        sum(net_sales_amount) as total_revenue,
        sum(discount_aud) as total_discount_given
    from sales
    where promotion_id is not null
    group by promotion_id, promotion_name, discount_type
)

select * from promotion_sales
