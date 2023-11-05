from classes.discord.Analyst import Analyst
from classes.discord.Options_Contract import Options_Contract


class Analyst1(Analyst):
    def __init__(self):
        super().__init__(server_id="697936741117460640", channel_id="1035245170582626334")
        self.name = "Analyst1"
        

    # Splits each Discord chat messages into words in a list. 
    # First word will always be the title: 'open', 'close' or 'update'. 
    def _split_messages_into_words_list(self, message):
        try:
            title = message['embeds'][0]['title']
            description = message['embeds'][0]['description']
            description = " ".join([title, description])
            self.words_list = description.split()
        except KeyError as e:
            print(f"KeyError: {e}")
        except IndexError as e:
            print(f"IndexError: {e}")
            

    # If position opened or closed, create a new options contract object. This object will be sent to TWS API. 
    def _translate_words_list_to_options_contract(self):
        sentence = self.words_list
        first_word = sentence[0].upper()

        if (first_word == "OPEN" and not self._is_lotto_or_risky_trade(sentence)) or (first_word == "CLOSE"):
            self._create_contract(sentence)


    def _is_lotto_or_risky_trade(self, sentence: str):
        return any("lotto" in item.lower() or "risk" in item.lower() for item in sentence)


    def _create_contract(self, sentence: str):
        if sentence[1].upper() == "BTO":
            action = "BUY"
        elif sentence[1].upper() == "STC":
            action = "SELL"
        symbol = sentence[2]
        strike = self._convert_string_to_int_or_float(sentence[3][:-1])
        right = self._get_right_from_sentence(sentence[3][-1:])
        expiry_date = self._extract_expiry_date_YYYYMMDD(sentence[4])
        # Strike is only none if _convert_string_to_int_or_float() throws a ValueError exception
        if strike is not None:
            oc =  Options_Contract(action, symbol, strike, right, expiry_date, self.name)
            self.options_contracts.append(oc)