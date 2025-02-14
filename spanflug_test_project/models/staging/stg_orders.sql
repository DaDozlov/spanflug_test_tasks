{{ config(materialized='view') }}

with orders as (
    select
        id as order_id,
        supplier_id,
        customer_id,
        order_value,
        requested_delivery_date,
        actual_delivery_date,
        
        coalesce(customer_rating, 0) as cleaned_customer_rating,

        case
            when actual_delivery_date is null then 0
            else actual_delivery_date - requested_delivery_date
        end as delivery_delay_days

    from {{ source('raw_data', 'orders') }}
)

select * from orders