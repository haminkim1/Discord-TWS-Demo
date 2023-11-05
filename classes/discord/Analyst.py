from utils.api_requests import *
from utils.get_date import get_NY_date_YYYY_MM_DD

import re

class Analyst:
    def __init__(self, server_id, channel_id):
        self.server_id = server_id
        self.channel_id = channel_id
        self.name = "Analyst"
        self._num_difference = 0
        self.message = ""
        self.message_data = {}
        self.words_list = []
        self.options_contracts = []

        # Variables for Analyst3 and Analyst2
        self.open_positions = []
        self.closing_key_words = []
        self.trimming_key_words = []
        self.current_message_id = ""
        self.referenced_message = None
        self.referenced_message_list = None


    def get_discord_messages_from_channel(self, headers, last_message_id):
        self.message_data = get_data_from_discord_api_after_msg_id(self.channel_id, headers, last_message_id, self.num_difference)
    

    def process_messages(self):
        try:
            for message in reversed(self.message_data):
                self._init_for_each_message()
                self._split_messages_into_words_list(message)
                self._translate_words_list_to_options_contract()
        except IndexError as e:
            print("Error likely due to empty content")
        except Exception as e:
            print(f"Exception: {e}")
    

    def _init_for_each_message(self):
        self.message = ""
        self.words_list = []
        self.current_message_id = ""
        self.referenced_message = None
        self.referenced_message_list = None
    

    # Splits each Discord chat messages into words in a list. 
    def _split_messages_into_words_list(self, message):
        try:
            self.message = message
            self.words_list = " ".join([message['content']]).split()
            self.current_message_id = message['id']
            # Check if 'referenced_message' and 'content' exist in message
            if 'referenced_message' in message and 'content' in message['referenced_message']:
                self.referenced_message = message['referenced_message']
                self.referenced_message_list = " ".join([message['referenced_message']['content']]).split()
        except KeyError:
            ...
        except IndexError:
            ...


    """
    START
    From here to end are the methods for checking whether the discord messages are able to be processed
    into open or close options contracts
    """
    def _translate_words_list_to_options_contract(self):
        sentence = self.words_list
        if self._is_open_sentence(sentence):
            self._create_open_contract(sentence)
            return
        if self._is_close_sentence():
            self._create_close_contract()


    def _is_open_sentence(self, sentence: str):
        ...


    def _create_open_contract(self, sentence: str):
        ...

    
    def _is_lotto_or_risky_trade(self):
        if "risk" in self.message['content'].lower() or "lotto" in self.message['content'].lower():
            return True
        else:
            return False


        
    def _is_close_sentence(self):
        ...


    def _create_close_contract(self):
        ...

    def _create_and_append_options_contract(self, action, i, sentence: str):
        ...
    """
    END
    """


    """
    Template method for Analyst1
    """
    def _create_contract(self, sentence: str):
        ...


    """
    START
    These are methods used to retrieve options contract details from Discord messages
    """
    def _convert_string_to_int_or_float(self, value: str):
        try:
            float_value = float(value)
            if float_value.is_integer():
                integer_value = int(float_value)
                return integer_value
            elif float_value % 1 == 0:
                return int(float_value)
            else:
                return float_value
        except ValueError:
            return None


    def _get_right_from_sentence(self, right: str):
            return right.upper()


    def _extract_expiry_date_YYYYMMDD(self, date: str):
        expiry_year = ""
        expiry_month = ""
        expiry_day = ""
        try:
            # If date format is MM/DD/YY or YYYY
            if date.count("/") == 2:
                expiry_month, expiry_day, expiry_year = date.split('/')
                if len(expiry_year) != 4:
                    expiry_year = "20" + expiry_year  
            
            # If date format is MM/DD
            elif date.count("/") == 1:
                today = get_NY_date_YYYY_MM_DD()
                year, month, day = today.split('/')

                expiry_month, expiry_day = date.split('/')

                # If date is before current date, assume contract expiry date is next year's.
                if int(expiry_month) < int(month) or (int(expiry_month) == int(month) and int(expiry_day) < int(day)):
                    year = str(int(year) + 1)
                expiry_year = year
                
            if len(expiry_month) == 1:
                expiry_month = "0" + expiry_month
            
            if len(expiry_day) == 1:
                expiry_day = "0" + expiry_day
            
            # YYYYMMDD format
            return f"{expiry_year}{expiry_month}{expiry_day}"
        except Exception:
            print("Something went wrong while extracting expiry date")
            return ""
        
    # Regular expression pattern to capture contract price after "@"
    def _get_contract_price_from_message(self, message):
        pattern = r'@(\d+(?:\.\d+)?)'
        
        for word in message:
            match = re.search(pattern, word)
            
            if match:
                return float(match.group(1))
        return None

    """
    END
    """




    @property
    def num_difference(self):
        return self._num_difference
    

    @num_difference.setter
    def num_difference(self, num_difference):
        self._num_difference = num_difference
