{{ config(materialized='table') }}

with orders as (
    select *
    from {{ ref('stg_orders') }}
),

customers as (
    select id as customer_id, name as customer_name
    from {{ source('raw_data', 'customers') }}
),

suppliers as (
    select id as supplier_id, name as supplier_name
    from {{ source('raw_data', 'suppliers') }}
)

select
    o.order_id,
    o.supplier_id,
    s.supplier_name,
    o.customer_id,
    c.customer_name,
    o.order_value,
    o.requested_delivery_date,
    o.actual_delivery_date,
    o.cleaned_customer_rating,
    o.delivery_delay_days
from orders o
left join customers c on o.customer_id = c.customer_id
left join suppliers s on o.supplier_id = s.supplier_id