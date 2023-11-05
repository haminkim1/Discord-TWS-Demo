from auth.gspread.auth_gspread import authenticate_gspread
from config.config import is_production_env
from utils.get_date import get_NY_date_MM_DD_YYYY

def record_trade_log(data):
    try:
        if is_production_env():
            analyst_name = f"{get_analyst_name_from_trade_ID(data['Trade ID'])}_Prod"
        else:
            analyst_name = get_analyst_name_from_trade_ID(data['Trade ID'])
        global worksheet
        worksheet = authenticate_gspread(analyst_name)
        next_empty_index = find_next_empty_row()

        trade_ID = data["Trade ID"]
        date = data["Date"]
        cost = data["Cost ($)"]
        commission = data["Commission ($)"]

        if data["Action"].upper() == "BUY":
            record_buy_log(next_empty_index, trade_ID, date, cost, commission)
        elif data["Action"].upper() == "SELL":
            record_sell_log(trade_ID, date, cost, commission)

    except KeyError as e:
        print(f"KeyError: The key {e} is missing from the 'data' dictionary.")
        return False
    except Exception as e:
        print(f"Exception: {e}")
        return False
    return True


def get_analyst_name_from_trade_ID(input_string):
    # Split the input string by underscores
    parts = input_string.split("_")
    
    # Check if there are at least 4 parts (including 3 underscores)
    if len(parts) >= 4:
        extracted_strings = "_".join(parts[3:])
    else:
        extracted_strings = None  # Not enough parts to extract

    return extracted_strings


def find_next_empty_row(column_index=1):
    # Get all values in column A (Trade ID column)
    column_values = worksheet.col_values(column_index)

    # Find the index of the first empty cell (an empty string in the list of column values)
    try:
        next_empty_index = column_values.index("") + 1
    except ValueError:
        # If no empty cell is found, the next empty row number will be one more than the number of rows in the worksheet
        next_empty_index = len(column_values) + 1

    return next_empty_index


def record_buy_log(i: int, trade_ID: str, date: str, cost: float, commission: float):
    worksheet.update(f"A{i}:D{i}", [[trade_ID, date, cost, commission]])
    worksheet.format(f"B{i}:D{i}", {
        "horizontalAlignment": "CENTER",
    })


def record_sell_log(trade_ID: str, date: str, cost: float, commission: float):
    cell_list = worksheet.findall(trade_ID)
    for cell in cell_list:
        i = cell.row
        # The value of cell within column "Date Closed"
        val = worksheet.cell(i, 7).value
        if val is None:
            date = get_NY_date_MM_DD_YYYY()
            worksheet.update(f"E{i}:G{i}", [[cost, commission, date]])
            break

def get_worksheet(analyst_name):
    global worksheet
    worksheet = authenticate_gspread(analyst_name)

"""
Below functions are for analyst backtesting
"""
def record_backtest_trade_log(data):
    try:
        next_empty_index = find_next_empty_row()

        trade_ID = data["Trade ID"]
        cost = data["Cost ($)"]
        message = data["Msg"]
        ref_msg = data["Ref Msg"]

        if data["Action"].upper() == "BUY":
            record_backtest_buy_log(next_empty_index, trade_ID, cost, message)
        elif data["Action"].upper() == "SELL":
            record_backtest_sell_log(trade_ID, cost, message, ref_msg)

    except KeyError as e:
        print(f"KeyError: The key {e} is missing from the 'data' dictionary.")
    except Exception as e:
        print(f"Exception: {e}")


def record_backtest_buy_log(i: int, trade_ID: str, cost: float, message: str):
    worksheet.update(f"A{i}:B{i}", [[trade_ID, cost]])
    worksheet.update(f"G{i}", message)
    worksheet.format(f"B{i}", {
        "horizontalAlignment": "CENTER",
    })


def record_backtest_sell_log(trade_ID: str, cost: float, message: str, ref_msg: str):
    cell_list = worksheet.findall(trade_ID)
    for cell in cell_list:
        i = cell.row
        # The value of cell within column "Exit Cost ($)"
        val = worksheet.cell(i, 3).value
        if val is None:
            worksheet.update(f"C{i}", cost)
            worksheet.update(f"H{i}:I{i}", [[message, ref_msg]])
            break
"""
End of backtest functions
"""