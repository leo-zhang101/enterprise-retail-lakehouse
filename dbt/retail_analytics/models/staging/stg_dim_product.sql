{{
    config(
        materialized='view',
    )
}}

with source as (
    select * from {{ source('warehouse_staging', 'dim_product') }}
),

renamed as (
    select
        product_id,
        product_name,
        category as product_category,
        subcategory as product_subcategory,
        brand,
        unit_price_aud,
        cost_aud,
        gross_margin_aud,
        gross_margin_pct,
        is_margin_available,
        load_date
    from source
)

select * from renamed
