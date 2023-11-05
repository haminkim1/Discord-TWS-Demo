from classes.discord.Analyst import Analyst
from classes.discord.Options_Contract import Options_Contract
from auth.discord.auth_header import headers
from utils.api_requests import *
from typing import List
import time

class Analyst3(Analyst):
    def __init__(self):
        super().__init__(server_id="697936741117460640", channel_id="1139560883127857304")
        self.name = "Analyst3"
        self.closing_key_words = ["closing", "closed", "cut", "cutting", "exiting", "fully out", 
                                  "selling", "out of", "out", "stopping", "stopped"]
        self.trimming_key_words = ["trimming", "trimmed", "sold"]


    def _is_open_sentence(self, sentence: str):
        for i, word in enumerate(sentence):
            if word.upper() == "BTO":
                sentence[i] = word.upper()
                return True
        return False


    def _create_open_contract(self, sentence: str):
        action = "BUY"
        i = sentence.index("BTO")
        self._create_and_append_options_contract(action, i, sentence)

        
    def _is_close_sentence(self):
        for keyword in self.closing_key_words + self.trimming_key_words:
            first_words = " ".join(self.words_list[:len(keyword.split())]).lower()
            if keyword == first_words:
                print(keyword)
                return True
        return False


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
        print(oc_keywords)
        try:
            if oc_keywords[0].isalpha():
                symbol = oc_keywords[0].upper()
        except IndexError as e:
            print(f"IndexError: {e}")

        if replied_sentence:
            print(replied_sentence)
            if self._is_open_sentence(replied_sentence):
                i = replied_sentence.index("BTO")
                self._create_and_append_options_contract(action, i, replied_sentence)
                return
            

        data = get_data_from_discord_api_before_msg_id(self.channel_id, headers, self.current_message_id, 20) # change to 20 later
        time.sleep(1)
        for message in data:
            sentence = " ".join([message['content']]).split()
            sentence = [word.replace("**","").upper() for word in sentence]
            for i, word in enumerate(sentence):
                if word.upper() == "BTO" and ((symbol != "" and symbol == sentence[i + 2]) or symbol == ""):
                    self._create_and_append_options_contract(action, i, sentence)
                    print(f"Sentence: {sentence}")
                    print(f"Options contract: {self.options_contracts[0]}")
                    return
                

    # Combined 2 lists into a single list. Does not add items in duplicate if both lists contain the same value. 
    def _remove_duplicate_items_and_combine_lists(self, list1, list2):
        combined_list = []
        # Add items from list1 to the result list
        for item in list1:
            if item not in combined_list:
                combined_list.append(item)

        # Add unique items from list2 to the result list
        for item in list2:
            if item not in combined_list:
                combined_list.append(item)
        return combined_list
            
    
    def _create_and_append_options_contract(self, action, i, sentence: str):
        try:
            symbol = sentence[i+2].upper()
            strike = self._convert_string_to_int_or_float(sentence[i+3][:-1])
            right = self._get_right_from_sentence(sentence[i+3][-1:])
            expiry_date = self._extract_expiry_date_YYYYMMDD(sentence[i+4])
            if strike is not None and len(expiry_date) == 8:
                oc = Options_Contract(action, symbol, strike, right, expiry_date, self.name)
                self.options_contracts.append(oc)
        except IndexError as e:
            print(f"IndexError due to Analyst3 not writing open contract in a standardized way. {e}")  


