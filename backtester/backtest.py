# The next 5 line of code is necessary to auto run this test by pressing play. 
# If the codes are not present, Python fails to find the imported modules. 
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from classes.discord.backtest_classes.Analyst2_Backtest import Analyst2_Backtest
from classes.discord.Analyst4 import Analyst4
import os
from backtester.modules.modules import *
from google_sheets.gspread_modules import *
from utils.csv_utils import *

def main():
    """
    SELECT ANALYST HERE
    """
    analyst = Analyst4()
    """
    DON'T TOUCH BELOW CODE IF ONLY PLANNING TO RUN THE PROGRAM
    """
    file_name = f"{analyst.name}.json"
    directory_path = "backtester\message_data"
    
    file_path = os.path.join(directory_path, file_name)
    analyst.json_data = read_JSON_file(file_path)

    csv_path = "csv_files/backtests"
    csv_file_name = f"{analyst.name}_Backtest.csv"

    analyst.stoploss_price = 1 - float(input("Stoploss price in percentage: ")) / 100
    analyst.trimming_price = float(input("Trimming price in percentage: ")) / 100 + 1

    for index, d in enumerate(analyst.json_data):
        analyst.index = index
        analyst.message_data = [d]

        analyst.process_messages()
        print(f"Processed message sent on {analyst.message['timestamp']}")
    headers = [
        "Trade_ID",
        "Date Entered",
        "Open Cost ($)",
        "Date Closed",
        "Closing Cost ($)",
        "PnL ($)",
        "Exit Percentage (%)",
        "Opening Message ID",
        "Closing Message ID",
        "Opening Message Content",
        "Closing Message Content",
        "Last Message ID"
    ]

    print(f"Stoploss price: -{analyst.stoploss_price}")
    print(f"Trimming price: {analyst.trimming_price}")
    post(csv_file_name, analyst.csv_data, headers, csv_path)

    last_message_ID = analyst.current_message_id

# Read alert
# If open, create dict and add values. Default values are None
# Default values for PnL and Exit Percentage are both 0
# Append to a dict list. 
# If close, search through same Trade_ID within dict list. Add values. 
# If values are not None, then calculate PnL and Exit Percentage. 

        


# Execute the main function if this script is run directly
if __name__ == "__main__":
    main()


