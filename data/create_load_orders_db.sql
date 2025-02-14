drop table stg_table;
drop table Orders;
drop table Suppliers;
drop table Customers;

create table Suppliers(
    id serial primary key,
    name varchar(100));

create table Customers(
    id serial primary key,
    name varchar(100));

create table Orders(
    id serial primary key,
	supplier_id int references Suppliers(id),
	customer_id int references Customers(id),
    order_value numeric,
    requested_delivery_date date,
    actual_delivery_date date,
	customer_rating numeric);

create table stg_table (
	supplier_nm varchar(100),
	customer_nm varchar(100),
	order_value numeric,
    requested_delivery_date date,
    actual_delivery_date date,
	customer_rating numeric);

copy stg_table
from '/home/daniil/project/spanflug_test_tasks/data/2021-11-03_HDCE3_orders_dataset.csv' 
delimiter ';' 
csv header;

select * from stg_table;

insert into Suppliers (name)
select distinct(supplier_nm) from stg_table;

insert into Customers (name)
select distinct(customer_nm) from stg_table;

insert into Orders (supplier_id, customer_id, order_value, requested_delivery_date, actual_delivery_date, customer_rating)
select su.id, c.id, s.order_value, s.requested_delivery_date, s.actual_delivery_date, s.customer_rating
from stg_table as s
join Suppliers as su
on su.name = s.supplier_nm
join Customers as c
on c.name = s.customer_nm;

select * from Suppliers;
select * from Customers;
select * from Orders;
