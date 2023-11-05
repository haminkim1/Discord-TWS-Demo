from classes.discord.Analyst2 import Analyst2


class Analyst2_Backtest(Analyst2):
    def __init__(self):
        super().__init__()
        self.message_data = {}
        self.index = 0
        self.json_data = []
        self.csv_data = []
        self.stoploss_price = 0
        self.trimming_price = 0


    def _create_and_append_options_contract(self, action, sentence: str):
        try:
            symbol = sentence[0].upper()
            strike = self._convert_string_to_int_or_float(sentence[1][:-1])
            right = self._get_right_from_sentence(sentence[1][-1:])
            expiry_date = self._extract_expiry_date_YYYYMMDD(sentence[2])
            trade_ID = f"{expiry_date}_{symbol}_{strike}{right}_{self.name}"
            if strike is not None and len(expiry_date) == 8:
                if action == "BUY":
                    contract_price = self._get_contract_price_from_message(sentence)
                    row = {
                        "Trade_ID": trade_ID,
                        "Date Entered": self.message['timestamp'],
                        "Open Cost ($)": contract_price,
                        "Date Closed": None,
                        "Closing Cost ($)": None,
                        "PnL ($)": 0,
                        "Exit Percentage (%)": 0,
                        "Opening Message ID": self.message['id'],
                        "Closing Message ID": None,
                        "Opening Message Content": self.message['content'],
                        "Closing Message Content": None
                    }
                    self.csv_data.append(row)
                    # Append dict of the csv table headigns to csv_data
                else:
                    for row in self.csv_data:
                        if trade_ID == row['Trade_ID']:
                            contract_price = self._get_contract_price_from_message(self.words_list)
                            alerted_exit_percentage = self._get_alerted_exit_percentage_from_message(self.words_list)
                            if alerted_exit_percentage:
                                contract_price = alerted_exit_percentage / 100 * row['Open Cost ($)'] + row['Open Cost ($)']
                            if not contract_price and not alerted_exit_percentage:
                                # Also if closing or partial closing keywords then make contract price 15% higher than open cost
                                if self._stoploss_or_closing_keywords_mentioned():
                                    contract_price = self._get_stoploss_price(row['Open Cost ($)'])
                                else:
                                    contract_price = self._get_trimming_price(row['Open Cost ($)'])
                            
                            row['Date Closed'] = self.message['timestamp']
                            row['Closing Cost ($)'] = contract_price
                            row['Closing Message ID'] = self.message['id']
                            row['Closing Message Content'] = self.message['content']
                            row['PnL ($)'] = self._calculate_PnL(row['Closing Cost ($)'], row['Open Cost ($)'], 1)
                            row['Exit Percentage (%)'] = self._calculate_exit_percentage(row['Open Cost ($)'], row['Closing Cost ($)'])
                            break
        except IndexError as e:
            print(f"IndexError due to Analyst3 not writing open contract in a standardized way. {e}")  
        except KeyError as e:
            print(f"Key {e} doesn't exist")

    # Timer set up to prevent discord API rate limit
    def _referenced_msg_or_parent_referenced_msg_is_open_sentence(self):
        try:           
            while 'message_reference' in self.referenced_message:
                msg_id = self.referenced_message['id']
                new_json_data = self.json_data[:self.index+1]
                for data in reversed(new_json_data):
                    if data['id'] == msg_id:
                        self.referenced_message = data['referenced_message']
                        self.referenced_message_list = " ".join([data['referenced_message']['content']]).split()
                        break
            return self._is_open_sentence(self.referenced_message_list)
        except KeyError:
            return False
    

    def _check_and_close_positions_with_same_symbol_and_analyst_name(self, sentence: str):
        ...

    
    def _get_stoploss_price(self, cost):
        return cost * self.stoploss_price


    def _get_trimming_price(self, cost):
        return cost * self.trimming_price
    

    """
    Overridden these methods to play around parameters and get as much profit as possible during backtesting. 
    """
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
                    if time_difference_in_hrs > 0:
                        stops_mentioned = True
        return stops_mentioned


    def _contract_within_closing_range(self, opening_price, exit_percentage):
        try:
            if not exit_percentage:
                return False
            else:
                return True
        except TypeError:
            return False

        
