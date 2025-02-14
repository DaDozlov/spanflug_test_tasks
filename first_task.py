import sqlite3
import pandas as pd
import os
import plotly.express as px

FILE_PATH = os.path.join("data", "2021-11-03_4M1QM_suppliers.txt")
DB_FILE = "orders_db.sqlite"
CSV_FILE = "data/2021-11-03_HDCE3_orders_dataset.csv"


## Encoding fixes in files
## Probably it could be fixed with another way, but I tried different encodings
## and nothing helped me so far, that is why I decided to use 'brute-force' approach

ENCODING_FIXES = {
    "NÃ¼rnberg": "Nürnberg",
    "Ã¼": "ü",
    "Ã¤": "ä",
    "Ã¶": "ö",
    "ÃŸ": "ß",
    "Ã©": "é",
    "Ã€": "À",
    "Ã©": "é",
    "Ãˆ": "È",
    "Ã´": "ô",
    "ÃŠ": "Ê",
    "â‚¬": "€",
    "â€œ": "“",
    "â€\x9d": "”",
    "â€“": "-",
    "â€”": "—",
    "â€™": "'",
}

def fix_encoding(text):
    
    for wrong, correct in ENCODING_FIXES.items():
        text = text.replace(wrong, correct)
        
    return text

### Reading txt file ###

def parse_suppliers_file(file_path):
        
    suppliers = []
    
    with open(file_path, "r", encoding="utf-8", errors="replace") as file:
        lines = (line.strip() for line in file if line.strip())
        
        while True:
            try:
                supplier_id = next(lines)
                next(lines)
                
                services = []
                while True:
                    line = next(lines)
                    if line == "------":
                        break
                    services.append(fix_encoding(line))

                address = fix_encoding(next(lines))

                # join set to remove duplicates
                suppliers.append({
                    "Supplier ID": supplier_id,
                    "Services": ", ".join(set(services)),
                    "Address": address
                })
                
            except StopIteration:
                break

    return pd.DataFrame(suppliers)

df_suppliers_from_text = parse_suppliers_file(FILE_PATH)


### Reading data from SQL ###

### I had to do it with SQLite, because firstly I didn't have postgresql instances
### on my personal laptop, but when I saw the second task I installed it later anyway

def load_data(db_file, csv_file):
    
    conn = sqlite3.connect(db_file)
    
    cursor = conn.cursor()
    
    cursor.executescript("""
        drop table stg_table;
        drop table Orders;
        drop table Suppliers;
        drop table Customers;

        create table Suppliers(
            id integer primary key,
            name varchar(100));

        create table Customers(
            id integer primary key,
            name varchar(100));

        create table Orders(
            id integer primary key,
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
        """)
    
    conn.commit()
    
    df = pd.read_csv(csv_file, delimiter=";")
    df.to_sql("stg_table", conn, if_exists="append", index=False)
    
    cursor.execute("insert into Suppliers (name) select distinct(supplier_nm) from stg_table")
    cursor.execute("insert into Customers (name) select distinct(customer_nm) from stg_table")
    cursor.execute("""
        insert into Orders (supplier_id, customer_id, order_value, requested_delivery_date, actual_delivery_date, customer_rating)
        select su.id, c.id, s.order_value, s.requested_delivery_date, s.actual_delivery_date, s.customer_rating
        from stg_table as s
        join Suppliers as su
        on su.name = s.supplier_nm
        join Customers as c
        on c.name = s.customer_nm;
    """)
    
    conn.commit()
    
    df_orders = pd.read_sql("SELECT * FROM Orders", conn)
    df_customers = pd.read_sql("SELECT * FROM Customers", conn)
    df_suppliers = pd.read_sql("SELECT * FROM Suppliers", conn)
    
    conn.close()
    
    return df_orders, df_customers, df_suppliers

df_orders, df_customers, df_suppliers = load_data(DB_FILE, CSV_FILE)


# From this moment begins not really gut structured code
# if I had more time, I would do it differently and I would make it more readable
# But 4 hours not enough for it

#######################
### Small data cleansing
# drop duplicates
df_suppliers_from_text.drop_duplicates(inplace=True)
# fill nans with 0
df_orders['customer_rating'].fillna(0, inplace=True)

################
### New features
## I had many ideas for future, also I should have joined it with main tables, but I hope it's OK
## delays
df_orders['requested_delivery_date'] = pd.to_datetime(df_orders['requested_delivery_date'], errors='coerce')
df_orders['actual_delivery_date'] = pd.to_datetime(df_orders['actual_delivery_date'], errors='coerce')
df_orders["order_delay_days"] = (df_orders["actual_delivery_date"] - df_orders["requested_delivery_date"]).dt.days


## Orders Frequency
# Orders per customer
customer_order_counts = df_orders["customer_id"].value_counts().reset_index()
customer_order_counts.columns = ["customer_id", "customer_order_frequency"]

# Orders per supplier
supplier_order_counts = df_orders["supplier_id"].value_counts().reset_index()
supplier_order_counts.columns = ["supplier_id", "supplier_order_frequency"]

## Number of Suppliers per Customer
customer_supplier_counts = df_orders.groupby("customer_id")["supplier_id"].nunique().reset_index()
customer_supplier_counts.columns = ["customer_id", "num_suppliers"]

## Number of Customers per Supplier
supplier_customer_counts = df_orders.groupby("supplier_id")["customer_id"].nunique().reset_index()
supplier_customer_counts.columns = ["supplier_id", "num_customers"]

## Order Value for Customers
customer_order_values = df_orders.groupby("customer_id")["order_value"].sum().reset_index()
customer_order_values.columns = ["customer_id", "total_order_value_customer"]

## Order Value for Suppliers
supplier_order_values = df_orders.groupby("supplier_id")["order_value"].sum().reset_index()
supplier_order_values.columns = ["supplier_id", "total_order_value_supplier"]

############
## Cleansing
# drop duplicates
df_suppliers_from_text.drop_duplicates(inplace=True)

# rename column
df_suppliers_from_text.rename(columns={"Supplier ID": "supplier_id"}, inplace=True)

# one hot encode the services
df_suppliers_from_text = df_suppliers_from_text.assign(
    Services=df_suppliers_from_text['Services'].str.split(', ')
).explode('Services')

df_suppliers_from_text = pd.get_dummies(df_suppliers_from_text, columns=['Services'])

###########################################
## Metrics and best suppliers and customers

# select top 10 customers by total order value
top_customers = customer_order_values.nlargest(10, "total_order_value_customer")

top_customers_sorted = top_customers.sort_values(by="total_order_value_customer", ascending=False)
top_customers_sorted["customer_id_str"] = top_customers_sorted["customer_id"].astype(str)

fig = px.bar(
    top_customers_sorted,
    x="customer_id_str",
    y="total_order_value_customer",
    title="Top 10 Most Valuable Customers",
    labels={"customer_id_str": "Customer ID", "total_order_value_customer": "Total Order Value"},
    text_auto=True
)

fig.write_image("top_10_customers.png", scale=6)

#
# uncomment this for displaying the bar chart
# fig.show()
#

# here I also had many ideas, but not really enough time to implement it all
# best suppliers analysis
# total sum delays per supplier
supplier_delays = df_orders.groupby("supplier_id")["order_delay_days"].sum().reset_index()
supplier_delays.columns = ["supplier_id", "total_delay_days"]
supplier_metrics = supplier_delays.merge(supplier_customer_counts, on="supplier_id").merge(supplier_order_values, on="supplier_id")

# rank suppliers based on criteria
supplier_metrics["rank_delay"] = supplier_metrics["total_delay_days"].rank(ascending=True, method="min")
supplier_metrics["rank_customers"] = supplier_metrics["num_customers"].rank(ascending=False, method="min")
supplier_metrics["rank_order_value"] = supplier_metrics["total_order_value_supplier"].rank(ascending=False, method="min")

supplier_metrics["overall_score"] = supplier_metrics["rank_delay"] + supplier_metrics["rank_customers"] + supplier_metrics["rank_order_value"]
best_suppliers = supplier_metrics.sort_values(by="overall_score").reset_index(drop=True)

###
# top 10 suppliers (list)
print("")
print("")
print("")
print("List of the top 10 suppliers by following metrics:")
print("Least delays in total")
print("Number of customers")
print("Total orders sum")
print("")
print("")
print("")
print(best_suppliers[:10])

output_text = (
    "\n\n\n"
    "List of the top 10 suppliers by following metrics:\n"
    "Least delays in total\n"
    "Number of customers\n"
    "Total orders sum\n"
    "\n\n\n"
    + best_suppliers[:10].to_string(index=False)
)

with open("top_10_suppliers.txt", "w") as f:
    f.write(output_text)