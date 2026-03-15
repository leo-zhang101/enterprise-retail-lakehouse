{{
    config(
        materialized='view',
    )
}}

with sales as (
    select * from {{ ref('stg_fact_sales') }}
),

daily as (
    select
        store_id,
        sale_date,
        count(sale_id) as transaction_count,
        sum(quantity) as total_quantity_sold,
        sum(gross_sales_amount) as gross_sales_amount,
        sum(net_sales_amount) as net_sales_amount,
        sum(discount_aud) as total_discount_aud
    from sales
    group by store_id, sale_date
)

select * from daily
