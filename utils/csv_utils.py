import csv
import os
from classes.discord.Options_Contract import Options_Contract
from config.config import is_production_env
from utils.get_date import get_NY_date_MM_DD_YYYY, get_current_date_YY_MM_DD
from google_sheets.gspread_modules import record_trade_log



# Define the data to be written to the CSV
def post_data_as_CSV(oc: Options_Contract, cost: float, comm: float):
    path = "csv_files/google_sheets"
    trade_ID = f"{oc.expiry_date}_{oc.symbol}_{oc.strike}{oc.right}_{oc.analyst_name}"
    cost = round(cost, 2)
    comm = round(comm, 2)
    date = get_NY_date_MM_DD_YYYY()
    data = None

    action = oc.action.upper()
    if is_production_env():
        file_name = f"{get_current_date_YY_MM_DD()}_{oc.analyst_name}_Prod.csv"
    else:
        file_name = f"{get_current_date_YY_MM_DD()}_{oc.analyst_name}.csv"
    data = [
        {"Action": action, "Trade ID": trade_ID, "Date": date, "Cost ($)": cost, "Commission ($)": comm}
    ]
    post_header_and_data(file_name, data, path)


def post_header_and_data(file, data, path):
    file_path = os.path.join(path, file)
    # Check if the file exists
    file_exists = os.path.isfile(file_path)
    # # Open the CSV file in append mode (if it exists) or write mode (if it doesn't exist)
    with open(file_path, mode="a" if file_exists else "w", newline="") as csv_file:
        fieldnames = []
        keys = data[0].keys()
        for key in keys:
            fieldnames.append(key)
        
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write the header if the file is newly created
        if not file_exists:
            writer.writeheader()

        # Write the data
        writer.writerows(data)


def post_headers(file, headers, path):
    file_path = os.path.join(path, file)
    # Check if the file exists
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode="a" if file_exists else "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)


def post(file, data, headers, path):
    file_path = os.path.join(path, file)
    # Check if the file exists
    file_exists = os.path.isfile(file_path)
    # # Open the CSV file in append mode (if it exists) or write mode (if it doesn't exist)
    with open(file_path, mode="a" if file_exists else "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)

        writer.writeheader()

        for row in data:
            try:
                writer.writerow(row)  
            except UnicodeEncodeError:
                row['Closing Message Content'] = "Failed to add content to CSV due to UnicodeEncodeError"
                try:
                    writer.writerow(row)
                except:
                    row['Opening Message Content'] = "Failed to add content to CSV due to UnicodeEncodeError"
                    writer.writerow(row)




def delete(file, data, path):
    file_path = os.path.join(path, file)
    rows = []

    # # Open the CSV file in append mode (if it exists) or write mode (if it doesn't exist)
    with open(file_path, mode="r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            rows.append(row)
        for row in rows:
            if row['Trade ID'] == data[0]['Trade ID']:
                rows.remove(row)
                break
    
    with open(file_path, mode="w", newline="") as out_file:
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(out_file, fieldnames=fieldnames)
        writer.writeheader()

        # for row in rows:
        writer.writerows(rows)



def post_csv_to_gspread():
    path = "csv_files/google_sheets"
    # Get a list of all CSV files in the directory
    csv_files = [os.path.join(path, file) for file in os.listdir(path) if file.endswith(".csv")]

    # Iterate through each CSV file
    for csv_file in csv_files:
        # Open the CSV file for reading
        with open(csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            row_number = 1  # Initialize the row number

            # Iterate through each row in the CSV file
            for row in reader:
                # Access data by column headers
                log_success = record_trade_log(row)

                if not log_success:
                    print(f"Error at row {row_number}: {row}")
                    return

                row_number += 1
            print(f"Successfully transferred data from CSV file {csv_file}")


def update_positions(oc: Options_Contract):
    path = "csv_files\positions"
    file_name = "positions.csv"
    
    trade_ID = f"{oc.expiry_date}_{oc.symbol}_{oc.strike}{oc.right}_{oc.analyst_name}"
    data = None
    action = oc.action.upper()
    data = [
        {"Trade ID": trade_ID}
    ]
    if action == "BUY":
        post_header_and_data(file_name, data, path)
    else:
        delete(file_name, data, path)
        

"""
Below functions are for analyst backtesting
"""
# Define the data to be written to the CSV
def post_backtest_data_as_CSV(oc: Options_Contract, cost: float, opening_or_closing_msg: str, referenced_opening_msg: str):
    trade_ID = f"{oc.expiry_date}_{oc.symbol}_{oc.strike}{oc.right}_{oc.analyst_name}"
    cost = round(cost, 2)
    data = None

    action = oc.action.upper()
    file_name = f"backtest_{oc.analyst_name}.csv"
    data = [
        {"Action": action, "Trade ID": trade_ID, "Cost ($)": cost, "Msg": opening_or_closing_msg, "Ref Msg": referenced_opening_msg}
    ]
    post_backtest(file_name, data)


def post_backtest(file, data):
    path = "csv_files/google_sheets"
    file = os.path.join(path, file)
    # Check if the file exists
    file_exists = os.path.isfile(file)

    # # Open the CSV file in append mode (if it exists) or write mode (if it doesn't exist)
    with open(file, mode="a" if file_exists else "w", newline="") as csv_file:
        fieldnames = ["Action", "Trade ID", "Cost ($)", "Msg", "Ref Msg"]
        
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write the header if the file is newly created
        if not file_exists:
            writer.writeheader()

        # Write the data
        writer.writerows(data)


def post_backtest_csv_to_gspread():
    path = "csv_files/google_sheets"
    # Get a list of all CSV files in the directory
    csv_files = [os.path.join(path, file) for file in os.listdir(path) if file.endswith(".csv")]

    # Iterate through each CSV file
    for csv_file in csv_files:
        # Open the CSV file for reading
        with open(csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            row_number = 1  # Initialize the row number

            # Iterate through each row in the CSV file
            for row in reader:
                # Access data by column headers
                log_success = record_trade_log(row)

                if not log_success:
                    print(f"Error at row {row_number}: {row}")
                    return

                row_number += 1
            print(f"Successfully transferred data from CSV file {csv_file}")

"""
End of backtest functions
"""
