from auth.discord.auth_header import headers
from classes.discord.Analyst import Analyst
from classes.discord.Analyst1 import Analyst1
from classes.discord.test_classes.Analyst1_Test_Analyst import Analyst1_Test_Analyst
from classes.discord.Analyst3 import Analyst3
from classes.discord.test_classes.Analyst3_Test import Analyst3_Test
from classes.discord.Analyst2 import Analyst2
from classes.discord.test_classes.Analyst2_Test import Analyst2_Test
from classes.ibkr.IBKR_Bot import IBKR_Trade_Bot
from utils.api_requests import *
from utils.csv_utils import post_data_as_CSV, update_positions
from utils.get_date import get_current_datetime
from config.config import flask_port_no, is_production_env

import re
import threading
import time

def main():
    # Uncomment below for prod
    Analyst1 = Analyst1()
    Analyst2 = Analyst2()
    Analyst3 = Analyst3()

    # Uncomment below for testing only
    Analyst1_test_analyst = Analyst1_Test_Analyst()
    Analyst2_test = Analyst2_Test()
    Analyst3_test = Analyst3_Test()
    
    analysts = []
    
    analysts.append(Analyst2_test)
    analysts.append(Analyst2)
    analysts.append(Analyst3)


    ibkr_bot = IBKR_Trade_Bot()
    # If IBKR TWS isConnected
        # Get positions from CSV file and append to variable (maybe don't have to append to variable)
        # If new order has been executed, set a variable to True
        # If order executed
            # Update CSV file
    while True:
        if not ibkr_bot.app.isConnected():
            ibkr_bot.turn_on_API()
        else:
            for analyst in analysts:
                heartbeat(analyst, ibkr_bot)


        time.sleep(3)

def heartbeat(analyst: Analyst, ibkr_bot: IBKR_Trade_Bot):
    data = get_data(f"http://127.0.0.1:{flask_port_no()}/{analyst.server_id}/{analyst.channel_id}/latest-messages")
    
    """
    Send a message to a recipient.
    Checks if JSON data exists, number of new messages (difference) is not 0 and whether the app has already sent an
    API request to Discord
    """
    failed_options_orders = []
    if data and data["difference"] != 0 and not data["appHasSentAPIRequestToDiscord"]:
        data["appHasSentAPIRequestToDiscord"] = True
        post_data(f"http://127.0.0.1:{flask_port_no()}/{analyst.server_id}/{analyst.channel_id}/latest-messages", data)
        process_new_alerts_into_Options_Contract(data, analyst)

    if analyst.options_contracts:
        place_orders_from_options_contracts(analyst.options_contracts, failed_options_orders, ibkr_bot)
        analyst.options_contracts = copy_failed_options_contract_orders(failed_options_orders)


def process_new_alerts_into_Options_Contract(data, analyst: Analyst):
    last_message_ID = get_last_message_ID_from_data(data["lastMessageID"])
    analyst.num_difference = data["difference"]
    analyst.get_discord_messages_from_channel(headers, last_message_ID)
    analyst.process_messages()


def get_last_message_ID_from_data(ID: str):
    match = re.search(r'\d+', ID)
    if match:
        return int(match.group())
    else:
        return ""
    

def place_orders_from_options_contracts(oc_list: list, failed_oc_list: list, ibkr_bot: IBKR_Trade_Bot):
    for oc in oc_list:
        ibkr_bot.execute_order_to_TWS(oc)

        if ibkr_bot.order_failed:
            failed_oc_list.append(oc)


def copy_failed_options_contract_orders(failed_oc_list: list):
    if not failed_oc_list:
        return []
    else:
        return failed_oc_list[:]
    

# Call this method for troubleshooting purposes under heartbeat() 
# when laptop randomly restarts overnight to track time the laptop restarted. 
def record_current_date_time():
    # Open a text file in write mode ('w')
    file_path = 'date_time.txt'

    # Text content to write to the file
    date_time = get_current_datetime()
    content = "Current date time: " + str(date_time)

    with open(file_path, 'w') as file:
        file.write(content)


# Execute the main function if this script is run directly
if __name__ == "__main__":
    main()

