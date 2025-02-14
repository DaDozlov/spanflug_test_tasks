import pandas as pd

def parse_suppliers_file(file_path):
    """Optimized function to parse the suppliers file."""
    suppliers = []
    
    with open(file_path, "r", encoding="utf-8") as file:
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
                    services.append(line)

                address = next(lines)

                suppliers.append({
                    "Supplier ID": supplier_id,
                    "Services": ", ".join(set(services)),
                    "Address": address
                })
                
            except StopIteration:
                break

    return pd.DataFrame(suppliers)

df_suppliers = parse_suppliers_file("2021-11-03_4M1QM_suppliers.txt.txt")

print(df_suppliers.head())