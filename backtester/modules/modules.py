from classes.discord.Analyst import Analyst
from auth.discord.auth_header import headers
from utils.api_requests import *
from typing import List
import json


def read_JSON_file(file_path):
    with open(file_path, "r") as json_file:
        try:
            return json.load(json_file)
        except json.JSONDecodeError:
            # Handle the case where the file is empty or not valid JSON
            return []


def write_JSON_file(data, file_path):
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)      


def add_message_data_to_JSON_file(analyst: Analyst, last_id, file_path, file_existed_before_running_app):
    print("Last id is: ", last_id)
    data: List = []

    if file_existed_before_running_app:
        data: List = get_data_from_discord_api_after_msg_id(analyst.channel_id, headers, last_id, 50)
        last_id = data[0]['id']
    else:
        data: List = get_data_from_discord_api_before_msg_id(analyst.channel_id, headers, last_id, 50)
        last_id = data[len(data)-1]['id']

    if data:
        data.reverse()
        output_to_JSON(data, file_path, file_existed_before_running_app)
        return last_id
    else:
        return 0

    
def output_to_JSON(data, file_path, file_existed_before_running_app):
    existing_data = read_JSON_file(file_path)
    if file_existed_before_running_app:
        existing_data = existing_data + data
    else:
        existing_data = data + existing_data

    write_JSON_file(existing_data, file_path)
