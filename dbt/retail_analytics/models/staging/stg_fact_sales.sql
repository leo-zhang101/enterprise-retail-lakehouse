{{
    config(
        materialized='view',
    )
}}

with source as (
    select * from {{ source('warehouse_staging', 'fact_sales') }}
),

renamed as (
    select
        sale_id,
        product_id,
        store_id,
        customer_id,
        promotion_id,
        quantity,
        unit_price_aud,
        discount_aud,
        gross_sales_amount,
        net_sales_amount,
        discount_rate,
        sale_date,
        sale_timestamp,
        product_category,
        store_state,
        promotion_name,
        discount_type,
        is_valid_sale_record,
        is_discounted,
        is_member_sale,
        load_date
    from source
    where is_valid_sale_record = true
)

select * from renamed
