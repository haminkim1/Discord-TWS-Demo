from auth.discord.auth_header import headers
from classes.discord.Analyst import Analyst
from classes.discord.Options_Contract import Options_Contract
from utils.get_date import get_NY_date_MM_DD_YYYY
from utils.api_requests import get_data_from_msg_id
from datetime import datetime
import csv
import os
import re
import time

# TODO
    # Could consider the num of times a message has been replied. 
    # If "^", re-read the previous message against the replied message of "^"

class Analyst2(Analyst):
    def __init__(self):
        super().__init__(server_id="697936741117460640", channel_id="1025803258691862678")
        self.name = "Analyst2"
        self.closing_key_words = ["sold", "out of", "runner", "runners", "all out"]
        self.trimming_key_words = ["trimmed", "trimming"]
        self.firstword_stoploss_key_words = ["cutting", "cut"]
        self.stoploss_key_words = ["stopped", "no longer in", "letting this go", "stoploss hit"]
        self.exit_percentage_less_than_50 = 100
        self.exit_percentage_50_to_100 = 100
        self.exit_percentage_100_to_150 = 100
        self.exit_percentage_150_to_200 = 100
        self.exit_percentage_above_200 = 100


    def _is_open_sentence(self, sentence: str):
        if len(sentence) > 3 and sentence[0].isalpha() and sentence[1].isalnum() and any("/" in c for c in sentence[2]):
            return True
        else:
            return False    


    def _create_open_contract(self, sentence: str):
        # Prevent opening risky trades
        if self._is_lotto_or_risky_trade():
            return
        action = "BUY"
        self._create_and_append_options_contract(action, sentence)
        self._check_and_close_positions_with_same_symbol_and_analyst_name(sentence)


    # Get data from positions.csv
    # If symbol and right is the same, close positions. 
    def _check_and_close_positions_with_same_symbol_and_analyst_name(self, sentence: str):
        symbol = sentence[0].upper()

        """
        Regular Expression Pattern Explanation:
        (\d+)           - Capture one or more digits (e.g., '20231020') as Group 1.
        _               - Match an underscore character.
        ([A-Za-z]+)     - Capture one or more uppercase or lowercase letters (e.g., 'XOM') as Group 2.
        _               - Match an underscore character.
        ([0-9]+\.?[0-9]*)? - Capture an optional numeric value with or without decimal points (e.g., '110.0' or '110') as Group 3.
        ([A-Za-z])      - Capture a single uppercase or lowercase letter (e.g., 'C') as Group 4.
        _               - Match an underscore character.
        ([A-Za-z_]+)    - Capture one or more uppercase or lowercase letters or underscores (e.g., 'Analyst3') as Group 5.

        This pattern is designed to extract various parts from a string that follows a specific format:
        "20231020_XOM_110.0C_Analyst" or similar patterns. It captures the date, symbol, value, letter, and the rest of the string.
        """
        pattern = r'(\d+)_([A-Za-z]+)_([0-9]+\.?[0-9]*)?([A-Za-z])_([A-Za-z_]+)'

        path = "csv_files\positions"
        file_name = "positions.csv"
        file_path = os.path.join(path, file_name)

        reader: str
        # trade_ids = read_csv(file_path)
        with open(file_path, mode="r") as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                match = re.search(pattern, row['Trade ID'])
                if match:
                    exp_in_id = match.group(1)
                    symbol_in_id = match.group(2)
                    strike_in_id = match.group(3)
                    right_in_id = match.group(4)
                    name_in_id = match.group(5)

                    if symbol == symbol_in_id and self.name == name_in_id:
                        action = "SELL"
                        strike_in_id = self._convert_string_to_int_or_float(strike_in_id)
                        oc = Options_Contract(action, symbol_in_id, strike_in_id, right_in_id, exp_in_id, self.name)
                        self.options_contracts.append(oc)


    def _is_close_sentence(self):
        # Referenced message list is False if there are no messages replied to
        if not self.referenced_message:
            return False

        if self._referenced_msg_or_parent_referenced_msg_is_open_sentence():
            if (self._stoploss_or_closing_keywords_mentioned() or
                self._set_stops_at_entry_or_profits_mentioned() or
                self._keyword_trim_mentioned() or
                self._close_contract_based_on_alerted_closing_price_or_exit_percentage()):
                return True

        return False


    # Timer set up to prevent discord API rate limit
    def _referenced_msg_or_parent_referenced_msg_is_open_sentence(self):
        try:           
            while 'message_reference' in self.referenced_message:
                msg_id = self.referenced_message['id']
                time.sleep(1)
                data = get_data_from_msg_id(self.channel_id, headers, msg_id)
                self.referenced_message = data[0]['referenced_message']
                self.referenced_message_list = " ".join([data[0]['referenced_message']['content']]).split()
            return self._is_open_sentence(self.referenced_message_list)
        except KeyError:
            return False
        

    def _stoploss_or_closing_keywords_mentioned(self):
        # Returns true if the first word of the message is a stoploss keyword. 
        stoploss_hit = False
        for keyword in self.firstword_stoploss_key_words:
            try:
                first_word = self.words_list[0].lower()
                if keyword == first_word:
                    stoploss_hit = True
            except IndexError:
                ...
        
        # Returns true if the message mentions any stoploss or closing keywords
        for keyword in self.stoploss_key_words + self.closing_key_words:
            if keyword in self.message['content'].lower():
                stoploss_hit = True
        return stoploss_hit
    

    def _set_stops_at_entry_or_profits_mentioned(self):
        # He often messages "stops at entry/profits" on a contract he opened. After that he does not notify alerts when he 
        # fully closed the position. This is usually his last alert of that contract. However, if he messages this alert
        # soon after his open contract, he continues alerting. Therefore, I've set the time limit of 30 minutes. 
        stops_mentioned = False
        words_list_lower = [word.lower() for word in self.words_list]
        if "stops" in words_list_lower:
            index = words_list_lower.index("stops")
            for i in range(index + 1, len(words_list_lower)):     
                if "entry" in words_list_lower[i] or "profits" in words_list_lower[i] or "profit" in words_list_lower[i]:
                    time_difference_in_hrs = self._get_time_difference_in_hours_from_Discord_timestamps(self.message['timestamp'], self.referenced_message['timestamp'])
                    if time_difference_in_hrs > 0.25:
                        stops_mentioned = True
        return stops_mentioned


    def _get_time_difference_in_hours_from_Discord_timestamps(self, timestamp1, timestamp2):
        try:
            datetime1 = datetime.fromisoformat(timestamp1)
            datetime2 = datetime.fromisoformat(timestamp2)

            # Returns time difference in hours
            return abs((datetime2 - datetime1).total_seconds()) / 3600
        except TypeError:
            return 0


    def _keyword_trim_mentioned(self):
        trim_mentioned = False
        NY_date_today = self._extract_expiry_date_YYYYMMDD(get_NY_date_MM_DD_YYYY())
        expiry_date = self._extract_expiry_date_YYYYMMDD(self.referenced_message_list[2])
        if "trim" in self.words_list[0].lower():
            # Check expiry date and close position if close to expiry. 
            if self._contract_close_to_expiry_date(NY_date_today, expiry_date):
                trim_mentioned = True

        # Closing position after first partial closing keyword if contract is close to expiry. 
        for keyword in self.trimming_key_words:
            if keyword in self.message['content'].lower():
                if len(expiry_date) == 8:
                    if self._contract_close_to_expiry_date(NY_date_today, expiry_date):
                        trim_mentioned = True
        return trim_mentioned


    def _contract_close_to_expiry_date(self, today, exp_date):
        # get year, month and date
        # If today and exp_date is same, return True
        if today == exp_date:
            return True
        else:
            date1 = datetime.strptime(today, "%Y%m%d")
            date2 = datetime.strptime(exp_date, "%Y%m%d")
            return (date2 - date1).days < 2


    def _close_contract_based_on_alerted_closing_price_or_exit_percentage(self):
        # First checks whether the message contains any
        # Check whether @ and % exists without any keywords existing, then compare to the open price
        # and close if profitable enough. 
        has_closing_price_or_exit_percentage = False
        if not "sl" in self.message['content'].lower() and not "stoploss" in self.message['content'].lower() and not "loss" in self.message['content'].lower():
            closing_price = self._get_contract_price_from_message(self.words_list)
            opening_price = self._get_contract_price_from_message(self.referenced_message_list)

            calced_exit_percentage = self._calculate_exit_percentage(opening_price, closing_price)
            alerted_exit_percentage = self._get_alerted_exit_percentage_from_message(self.words_list)

            if (self._contract_within_closing_range(opening_price, calced_exit_percentage) or 
                self._contract_within_closing_range(opening_price, alerted_exit_percentage)):
                has_closing_price_or_exit_percentage = True
            
        return has_closing_price_or_exit_percentage     


    def _calculate_exit_percentage(self, open, close):
        try:
            return ((close - open) / open) * 100
        except TypeError:
            return None
    

    # Multiply by 100 as each contract contains 100 shares. 
    def _calculate_PnL(self, close, open, qty):
        try:
            return (close - open) * 100 * qty
        except TypeError:
            return None
        

    def _get_alerted_exit_percentage_from_message(self, message):
        pattern = r'(\d+)%'

        for word in message:
            match = re.search(pattern, word)

            if match:
                return int(match.group(1))
        return None


    # Bracket range of opening price positions:
    #     0-0.50: Above 50% (0.5 profit)
    #     0.51-1.00: Above 40%
    #     1.01-1.5: Above 30%
    #     1.5-2.0: Above 25% (0.375-0.5 profit)
    #     2.0 and above: Close on first trim (Above 0%)
    def _contract_within_closing_range(self, opening_price, exit_percentage):
        try:
            if not exit_percentage:
                return False
            # Commenting calculations checking if contract is within closing range to close contract upon first alert. 
            elif opening_price <= 0.5:
                return self.exit_percentage_less_than_50 >= 40
            elif opening_price > 0.5 and opening_price <= 1:
                return self.exit_percentage_50_to_100 >= 30
            elif opening_price > 1 and opening_price <= 1.5:
                return self.exit_percentage_100_to_150 >= 20
            elif opening_price > 1.5 and opening_price <= 2:
                return self.exit_percentage_150_to_200 >= 15
            else:
                return True
        except TypeError:
            return False


    def _create_close_contract(self):
        action = "SELL"
        self._create_and_append_options_contract(action, self.referenced_message_list)
    

    def _create_and_append_options_contract(self, action, sentence: str):
        try:
            symbol = sentence[0].upper()
            strike = self._convert_string_to_int_or_float(sentence[1][:-1])
            right = self._get_right_from_sentence(sentence[1][-1:])
            expiry_date = self._extract_expiry_date_YYYYMMDD(sentence[2])
            if strike is not None and len(expiry_date) == 8:
                oc = Options_Contract(action, symbol, strike, right, expiry_date, self.name)
                self.options_contracts.append(oc)
        except IndexError as e:
            print(f"IndexError due to Analyst2 not writing open contract in a standardized way. {e}")  

    
