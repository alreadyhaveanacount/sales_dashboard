####################################################################################
#                            THIS IS FOR TESTING ONLY                              #
####################################################################################

import pandas as pd
from sys import argv
from random import choice, uniform, randint

if len(argv) < 2:
    print("Syntax: python entry_generator.py ENTRY_AMOUNT")
    exit(1)

data = pd.read_csv("./data/sales_data_formatted.csv")

unique_ids = data["Product_ID"].unique()
sales_reps = data["Sales_Rep"].unique()
regions = data["Region"].unique()
categories = data["Product_Category"].unique()
customer_types = data["Customer_Type"].unique()
payment_methods = data["Payment_Method"].unique()
sales_channels = data["Sales_Channel"].unique()
months = [i for i in range(1, 12)]
days = [i for i in range(1, 29)]

def generate_row():
    reg = choice(regions)
    sales_rep = choice(sales_reps)
    unit_cost = round(uniform(100, 4000), 2)

    return {
        "Product_ID": choice(unique_ids),
        "Sales_Rep": sales_rep,
        "Region": reg,
        "Sales_Amount": round(uniform(3000, 8000), 2),
        "Quantity_Sold": randint(10, 40),
        "Product_Category": choice(categories),
        "Unit_Cost": unit_cost,
        "Unit_Price": round(unit_cost+uniform(100, 300), 2),
        "Customer_Type": choice(customer_types),
        "Discount": round(uniform(0.00, 0.30), 2),
        "Payment_Method": choice(payment_methods),
        "Sales_Channel": choice(sales_channels),
        "Region_and_Sales_Rep": f"{reg}-{sales_rep}",
        "YEAR": 2024,
        "MONTH": choice(months),
        "DAY": choice(days)
    }

new_entries = pd.DataFrame([generate_row() for i in range(int(argv[1]))])

data = pd.concat([data, new_entries], ignore_index=True)

data.to_csv("./data/sales_data_formatted.csv", index=False)