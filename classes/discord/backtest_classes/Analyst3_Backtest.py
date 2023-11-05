from classes.discord.Analyst3 import Analyst3
from google_sheets.gspread_modules import record_backtest_trade_log
from typing import List
import threading
import time

class Analyst3_Backtest(Analyst3):
    def __init__(self):
        super().__init__()
        self.message_data = {}
        self.index = 0


    def process_messages(self):
        try:
            for i, message in enumerate(self.message_data):
                self.opening_or_closing_message = ""
                self.referenced_opening_contract_msg = ""
                self.index = i
                self.opening_or_closing_message = message['content']
                self._split_messages_into_words_list(message)
                self._translate_words_list_to_options_contract()
        except Exception as e:
            print(f"Exception: {e}")
    

    def _create_and_append_options_contract(self, action, i, sentence: str):
        try:
            symbol = sentence[i+2].upper()
            strike = self._convert_string_to_int_or_float(sentence[i+3][:-1])
            right = self._get_right_from_sentence(sentence[i+3][-1:])
            expiry_date = self._extract_expiry_date_YYYYMMDD(sentence[i+4])
            contract_price = 0
            if action == "BUY":
                contract_price = self._convert_string_to_int_or_float(sentence[i+6])
            else:
                if "@" in self.words_list:
                    index = self.words_list.index("@")
                    print(self.words_list, self.words_list[index+1])
                    contract_price = self._convert_string_to_int_or_float(self.words_list[index+1])
                    print(sentence)
                    print(strike, expiry_date, contract_price)
            if strike is not None and len(expiry_date) == 8:
                """
                self.words_list (opening and closing contract message)
                self.referenced_opening_contract_msg (Referenced opening message from closing contract message)
                """
                trade_ID = f"{expiry_date}_{symbol}_{strike}{right}_{self.name}"
                data = [
                    {"Action": action, "Trade ID": trade_ID, "Cost ($)": contract_price, 
                    "Msg": self.opening_or_closing_message, "Ref Msg": self.referenced_opening_contract_msg}
                ]
                # Needs to be CSV first then import to gspread. Otherwise rate quote will be reached if looped. 
                record_log_thread = threading.Thread(target=record_backtest_trade_log, args=(data))
                record_log_thread.start()
                time.sleep(3)
        except IndexError as e:
            print(f"IndexError due to Analyst3 not writing open contract in a standardized way. {e}")  


    def _create_close_contract(self):
        action = "SELL"
        symbol = ""
        sentence = self.words_list
        replied_sentence = self.referenced_message_list        

        # Check and replace if there's any word starting or ending with **. 
        bold_words = [word.replace("**","").upper() for word in sentence 
                      if word.startswith("**") or word.endswith("**")]
        upper_words = [word.replace("**","") for word in sentence 
                         if word.isupper()]

        oc_keywords: List[str] = self._remove_duplicate_items_and_combine_lists(bold_words, upper_words)
        try:
            if oc_keywords[0].isalpha():
                symbol = oc_keywords[0].upper()
        except IndexError as e:
            print(f"IndexError: {e}")

        if replied_sentence:
            if self._is_open_sentence(replied_sentence):
                i = replied_sentence.index("BTO")
                self.referenced_opening_contract_msg = " ".join(replied_sentence)
                self._create_and_append_options_contract(action, i, replied_sentence)
                return
            
        data = self.message_data[:self.index+1]
        for message in reversed(data):
            sentence = " ".join([message['content']]).split()
            sentence = [word.replace("**","").upper() for word in sentence]
            for i, word in enumerate(sentence):
                if word.upper() == "BTO" and ((symbol != "" and symbol == sentence[i + 2]) or symbol == ""):
                    self.referenced_opening_contract_msg = message['content']
                    self._create_and_append_options_contract(action, i, sentence)
                    return