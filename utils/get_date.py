from datetime import datetime
import pytz

def get_NY_date_MM_DD_YYYY():
    new_york_tz = pytz.timezone('America/New_York')
    return datetime.now(new_york_tz).strftime('%m/%d/%Y')

def get_NY_date_YYYY_MM_DD():
    new_york_tz = pytz.timezone('America/New_York')
    return datetime.now(new_york_tz).strftime('%Y/%m/%d')

def get_current_datetime():
    # YYYY-MM-DD HH:MM:SS
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_current_date_YY_MM_DD():
    # Get the current date
    current_date = datetime.now()

    # Format the date as YY_MM_DD
    return current_date.strftime("%y_%m_%d")    