{{
    config(
        materialized='view',
    )
}}

with source as (
    select * from {{ source('warehouse_staging', 'fact_inventory_daily') }}
),

renamed as (
    select
        snapshot_id,
        product_id,
        store_id,
        quantity_on_hand,
        snapshot_date,
        low_inventory_flag,
        load_date
    from source
)

select * from renamed
