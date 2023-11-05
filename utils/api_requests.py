import json
import requests


"""
Functions for requesting data from the Flask server
"""
def get_data(url):
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Get the response data
        data = response.json()
        # Process the data
        return data
    else:
        # Request failed
        print('Request failed with status code:', response.status_code)


def post_data(url, data):
    # Send a POST request with the data
    response = requests.post(url, json=data)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print("Data has been posted to", url)
    else:
        # Request failed
        print('Request failed with status code:', response.status_code)
"""
END
"""

"""
Functions for requesting Discord API
"""
def get_data_from_discord_api(channel_id, headers, num):
    try:
        response = requests.get(f'https://discord.com/api/v9/channels/{channel_id}/messages?limit={num}', headers=headers)

        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print('Request failed with status code:', response.status_code)
    except requests.exceptions.ConnectionError as e:
        print(f"requests.exceptions.ConnectionError: {e}")
    except UnboundLocalError as e:
        print(f"UnboundLocalError: {e}")


def get_data_from_msg_id(channel_id, headers, msg_id, num=1):
    try:
        response = requests.get(f'https://discord.com/api/v9/channels/{channel_id}/messages?around={msg_id}&limit={num}', headers=headers)
        
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print('Request failed with status code:', response.status_code)
    except requests.exceptions.ConnectionError as e:
        print(f"requests.exceptions.ConnectionError: {e}")
    except UnboundLocalError as e:
        print(f"UnboundLocalError: {e}")


def get_data_from_discord_api_after_msg_id(channel_id, headers, last_id, num):
    try:
        response = requests.get(f'https://discord.com/api/v9/channels/{channel_id}/messages?after={last_id}&limit={num}', headers=headers)
        
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print('Request failed with status code:', response.status_code)
    except requests.exceptions.ConnectionError as e:
        print(f"requests.exceptions.ConnectionError: {e}")
    except UnboundLocalError as e:
        print(f"UnboundLocalError: {e}")


def get_data_from_discord_api_before_msg_id(channel_id, headers, last_id, num):
    try:
        response = requests.get(f'https://discord.com/api/v9/channels/{channel_id}/messages?before={last_id}&limit={num}', headers=headers)
        
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print('Request failed with status code:', response.status_code)
    except requests.exceptions.ConnectionError as e:
        print(f"requests.exceptions.ConnectionError: {e}")
    except UnboundLocalError as e:
        print(f"UnboundLocalError: {e}")
"""
END
"""