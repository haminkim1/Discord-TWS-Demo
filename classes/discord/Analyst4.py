from classes.discord.Analyst import Analyst
from classes.discord.Options_Contract import Options_Contract

import re


class Analyst4(Analyst):
    def __init__(self):
        # Update id numbers once I have access. 
        super().__init__(server_id="836435995854897193", channel_id="1126325195301462117")
        self.name = "Analyst4"
        self.contract_price_limit = 3 


    def _is_open_sentence(self, sentence: str):
        return self.words_list[0].upper() == "BTO" and not self._is_lotto_or_risky_trade()
    

    def _create_open_contract(self, sentence: str):
        action = "BUY"
        self._create_and_append_options_contract(action, sentence)


    def _is_close_sentence(self):
        return self.words_list[0].upper() == "STC"

    
    def _create_close_contract(self):
        action = "SELL"
        self._create_and_append_options_contract(action, self.words_list)


    def _create_and_append_options_contract(self, action, sentence: str):
        symbol = sentence[2]
        strike = self._convert_string_to_int_or_float(sentence[3][:-1])
        right = self._get_right_from_sentence(sentence[3][-1:])
        expiry_date = self._extract_expiry_date_YYYYMMDD(sentence[4])
        contract_price = self._get_contract_price_from_message(sentence)
        # Strike is only none if _convert_string_to_int_or_float() throws a ValueError exception
        if strike is not None:
            oc =  Options_Contract(action, symbol, strike, right, expiry_date, self.name)
            self.options_contracts.append(oc)
    
    def _is_expensive_contract(self):
        # Price may be valued as None so checking for TypeError
        try:
            price = self._get_contract_price_from_message(self.words_list)
            # Update the self.contract_price_limit to increase or decrease the price limit. 
            return price > self.contract_price_limit and self.contract_price_limit != 0
        except TypeError:
            return False
        
    def _get_contract_price_from_message(self, message):
        pattern = r'@(\d+(?:\.\d+)?)'
        price = None
        for word in message[4:]:
            match = re.search(pattern, word)
            if match:
                return float(match.group(1))
            price = self._convert_string_to_int_or_float(word)
            if price:
                return price
        return price