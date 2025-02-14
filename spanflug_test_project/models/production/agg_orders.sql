{{ config(materialized='table') }}

with aggregated_orders as (
    select
        supplier_id,
        supplier_name,
        count(order_id) as total_orders,
        sum(order_value) as total_order_value,
        avg(delivery_delay_days) as avg_delivery_delay
    from {{ ref('fact_orders') }}
    group by supplier_id, supplier_name
)

select * from aggregated_orders