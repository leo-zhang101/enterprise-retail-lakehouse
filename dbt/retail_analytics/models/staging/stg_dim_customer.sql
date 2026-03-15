{{
    config(
        materialized='view',
    )
}}

with source as (
    select * from {{ source('warehouse_staging', 'dim_customer') }}
),

renamed as (
    select
        customer_id,
        first_name,
        last_name,
        email,
        loyalty_tier,
        is_loyalty_member,
        load_date
    from source
)

select * from renamed
