{{
    config(
        materialized='view',
    )
}}

with source as (
    select * from {{ source('warehouse_staging', 'dim_store') }}
),

renamed as (
    select
        store_id,
        store_name,
        city as store_city,
        state as store_state,
        postcode as store_postcode,
        address as store_address,
        load_date
    from source
)

select * from renamed
