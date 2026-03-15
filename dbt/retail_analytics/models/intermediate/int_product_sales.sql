{{
    config(
        materialized='view',
    )
}}

with sales as (
    select * from {{ ref('stg_fact_sales') }}
),

product_sales as (
    select
        product_id,
        product_category,
        count(sale_id) as transaction_count,
        sum(quantity) as total_quantity_sold,
        sum(net_sales_amount) as total_revenue,
        avg(quantity) as avg_quantity_per_transaction,
        avg(net_sales_amount) as avg_revenue_per_transaction
    from sales
    group by product_id, product_category
)

select * from product_sales
