# The next 5 line of code is necessary to auto run this test by pressing play. 
# If the codes are not present, Python fails to find the imported modules. 
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from classes.discord.Analyst import Analyst
from classes.discord.test_classes.Analyst1_Test_Analyst import Analyst1_Test_Analyst
from classes.discord.Analyst2 import Analyst2
from classes.discord.Analyst4 import Analyst4
from classes.discord.Analyst3 import Analyst3
from auth.discord.auth_header import headers
from utils.api_requests import *
from backtester.modules.modules import *
import time
import os

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
    file_existed_before_running_app = os.path.exists(file_path)

    if file_existed_before_running_app:
        existing_data = read_JSON_file(file_path)
        last_id = existing_data[len(existing_data)-1]['id']
    else:
        initial_data = get_data_from_discord_api(analyst.channel_id, headers, 1)
        write_JSON_file(initial_data, file_path)
        last_id = initial_data[0]['id']
    
    while True:
        last_id = add_message_data_to_JSON_file(analyst, last_id, file_path, file_existed_before_running_app)
        # last_id will be 0 if program has reached end of chat in the channel.
        if last_id == 0:
            return
        time.sleep(5)


# Execute the main function if this script is run directly
if __name__ == "__main__":
    main()


