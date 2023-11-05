# The next 5 line of code is necessary to auto run this test by pressing play. 
# If the codes are not present, Python fails to find the imported modules. 
import sys
import os
import pytz

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from classes.discord.Analyst2 import Analyst2
from utils.get_date import get_NY_date_MM_DD_YYYY
from datetime import datetime, timedelta



import unittest

class TestAnalyst(unittest.TestCase):
    def setUp(self):
        self.analyst2 = Analyst2()
        

    def test_words_in_messages_appended_to_words_list_by_space(self):
        self.analyst2.message_data = [
            {
                "content": "len of Analyst2.options_contracts will be 0"
            }
        ]

        self.analyst2.process_messages()
        words_list = self.analyst2.words_list
        self.assertEqual(["len", "of", "Analyst2.options_contracts", "will", "be", "0"], words_list)


    def test_process_messages_non_contract_messages(self):
        self.analyst2.message_data = [
            {
                "content": "len of Analyst2.options_contracts will be 0"
            }
        ]
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))


    def test_process_messages_open_contract(self):
        self.analyst2.message_data = [
            {
                "content": "COIN 81c 10/13/23 @1.35"
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("BUY", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)

    
    def test_process_messages_open_contract_lowercase(self):
        self.analyst2.message_data = [
            {
                "content": "coin 81c 10/13/23 @1.35"
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("BUY", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)


    def test_process_messages_open_contract_uppercase(self):
        self.analyst2.message_data = [
            {
                "content": "COIN 81C 10/13/23 @1.35"
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("BUY", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)


    def test_process_messages_doesnt_create_open_contract_if_risky_or_lotto(self):
        self.analyst2.message_data = [
            {
                "content": "COIN 81C 10/13/23 @1.35 high risk"
            }
        ]
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))

        self.analyst2.message_data = [
            {
                "content": "COIN 81C 10/13/23 @1.35 lotto"
            }
        ]
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))


    def test_process_messages_close_contract_with_no_referenced_message(self):
        self.analyst2.message_data = [
            {
                "content": "sold coin"
            }
        ]
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))


    def test_process_messages_close_contract_lowercase(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "sold coin",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1.35",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)


    def test_process_messages_close_contract_uppercase(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "SOLD COIN",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1.35",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)


    def test_process_messages_close_contract_if_ref_message_is_also_close_sentence(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "SOLD COIN",
                "referenced_message": 
                    {
                        "id": "1164953611525165217",
                        "content": "Trimming",
                        "message_reference":
                            {
                                "message_id": "1164948287640567820"
                            }
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231027", oc.expiry_date)


    def test_process_messages_close_contract_firstword_stoploss_key_words_lowercase(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "cutting coin",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1.35",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)


    def test_process_messages_close_contract_firstword_stoploss_key_words_uppercase(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "CUTTING coin",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1.35",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)


    def test_process_messages_doesnt_create_close_contract_if_firstword_stoploss_key_words_is_not_the_first_word(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "coin cutting",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1.35",
                    }
            }
        ]
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))


    def test_process_messages_close_contract_stoploss_key_words_lowercase(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "stopped out of coin",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1.35",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)


    def test_process_messages_close_contract_stoploss_key_words_uppercase(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "STOPPED OUT OF COIN",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1.35",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)


    def test_process_messages_create_close_contract_if_stoploss_key_words_is_not_the_first_word(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "coin got stopped",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1.35",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)


    def test_process_messages_create_close_contract_if_stoploss_key_words_is_not_the_first_word_part2(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "not liking the price action. Letting this go.",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1.35",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)


    def test_process_messages_close_contract_closing_key_words_lowercase(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "all out of this contract",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1.35",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)


    def test_process_messages_close_contract_stoploss_key_words_uppercase(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "ALL OUT OF THIS CONTRACT",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1.35",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)


    def test_process_messages_create_close_contract_if_stoploss_key_words_is_not_the_first_word(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "Liking the price action. All out of this contract.",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1.35",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)


    def test_process_messages_create_close_contract_after_stops_at_entry_or_profits_alert_past_30_minutes_lowercase(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "Trimmed. Set stops at or above entry or profits",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1.35",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)


    def test_process_messages_create_close_contract_after_stops_at_entry_or_profits_alert_past_30_minutes_uppercase(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "TRIMMED. SET STOPS AT OR ABOVE ENTRY OR PROFITS",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1.35",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)


    def test_process_messages_firstword_trim_same_DTE(self):
        expiry_date_plus_2_days = get_NY_date_MM_DD_YYYY()
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "trim here",
                "timestamp": "2023-10-20T15:30:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": f"COIN 81C {expiry_date_plus_2_days} @1.35",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)


    def test_process_messages_firstword_trim_same_DTE_uppercase(self):
        expiry_date_plus_0_days = get_NY_date_MM_DD_YYYY()
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "TRIM HERE",
                "timestamp": "2023-10-20T15:30:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": f"COIN 81C {expiry_date_plus_0_days} @1.35",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)


    def test_process_messages_firstword_trim_1_DTE(self):
        ny_tz = pytz.timezone('America/New_York')
        ny_date = datetime.now(ny_tz)
        expiry_date_plus_1_days = ny_date + timedelta(days=1)
        expiry_date_plus_1_days = expiry_date_plus_1_days.strftime('%m/%d/%Y')
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "trim here",
                "timestamp": "2023-10-20T15:30:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": f"COIN 81C {expiry_date_plus_1_days} @1.35",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)


    def test_process_messages_firstword_trim_2_DTE(self):
        ny_tz = pytz.timezone('America/New_York')
        ny_date = datetime.now(ny_tz)
        expiry_date_plus_2_days = ny_date + timedelta(days=2)
        expiry_date_plus_2_days = expiry_date_plus_2_days.strftime('%m/%d/%Y')
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "trim here",
                "timestamp": "2023-10-20T15:30:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": f"COIN 81C {expiry_date_plus_2_days} @1.35",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))


    def test_process_messages_firstword_trim_3_DTE(self):
        ny_tz = pytz.timezone('America/New_York')
        ny_date = datetime.now(ny_tz)
        expiry_date_plus_3_days = ny_date + timedelta(days=3)
        expiry_date_plus_3_days = expiry_date_plus_3_days.strftime('%m/%d/%Y')
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "trim here",
                "timestamp": "2023-10-20T15:30:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": f"COIN 81C {expiry_date_plus_3_days} @1.35",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))


    def test_process_messages_firstword_trim_doesnt_create_close_contract_if_trim_not_firstword(self):
        expiry_date_plus_2_days = get_NY_date_MM_DD_YYYY()
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "Going to trim here",
                "timestamp": "2023-10-20T15:30:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": f"COIN 81C {expiry_date_plus_2_days} @1.35",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))


    def test_process_messages_partial_closing_keywords_0_DTE(self):
        expiry_date_plus_0_days = get_NY_date_MM_DD_YYYY()
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "Contract looks good. trimmed here",
                "timestamp": "2023-10-20T15:30:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": f"COIN 81C {expiry_date_plus_0_days} @1.35",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)


    def test_process_messages_partial_closing_keywords_0_DTE_uppercase(self):
        expiry_date_plus_0_days = get_NY_date_MM_DD_YYYY()
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "CONTRACT LOOKS GOOD. TRIMMED HERE",
                "timestamp": "2023-10-20T15:30:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": f"COIN 81C {expiry_date_plus_0_days} @1.35",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)


    def test_process_messages_partial_closing_keywords_1_DTE(self):
        expiry_date_plus_1_days = get_NY_date_MM_DD_YYYY()
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "Contract looks good. trimmed here",
                "timestamp": "2023-10-20T15:30:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": f"COIN 81C {expiry_date_plus_1_days} @1.35",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)


    def test_process_messages_partial_closing_keywords_2_DTE(self):
        ny_tz = pytz.timezone('America/New_York')
        ny_date = datetime.now(ny_tz)
        expiry_date_plus_2_days = ny_date + timedelta(days=2)
        expiry_date_plus_2_days = expiry_date_plus_2_days.strftime('%m/%d/%Y')
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "Contract looks good. trimmed here",
                "timestamp": "2023-10-20T15:30:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": f"COIN 81C {expiry_date_plus_2_days} @1.35",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))


    def test_process_messages_partial_closing_keywords_3_DTE(self):
        ny_tz = pytz.timezone('America/New_York')
        ny_date = datetime.now(ny_tz)
        expiry_date_plus_3_days = ny_date + timedelta(days=2)
        expiry_date_plus_3_days = expiry_date_plus_3_days.strftime('%m/%d/%Y')
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "Contract looks good. trimmed here",
                "timestamp": "2023-10-20T15:30:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": f"COIN 81C {expiry_date_plus_3_days} @1.35",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))


    def test_process_messages_does_not_calc_percentage_or_closing_price_if_stoploss_included_in_message(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "stoploss at @.50",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1.35",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))


    def test_process_messages_does_not_calc_percentage_or_closing_price_if_stoploss_included_in_message(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "stoploss at 50%",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1.35",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))


    def test_process_messages_create_contract_passing_closing_price_range(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "@0.75",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @0.5",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)

        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "@1.4",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)

        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "@1.95",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1.5",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)

        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "@3",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @2",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)


    def test_process_messages_doesnt_create_contract_failing_closing_price_range(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "@0.6",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @0.5",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.exit_percentage_less_than_50 = 0
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))


        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "@1.2",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.exit_percentage_50_to_100 = 0
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))

        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "@1.8",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1.5",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.exit_percentage_100_to_150 = 0
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))

        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "@2.1",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @2",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.exit_percentage_150_to_200 = 0
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))


    def test_process_messages_create_contract_passing_closing_percentage_range(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "50%",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @0.5",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]
        self.assertEqual(1, len(self.analyst2.options_contracts))

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)

        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "40%",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)

        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "30%",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1.5",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)

        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "25%",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @2",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        oc = self.analyst2.options_contracts[0]

        self.assertEqual("SELL", oc.action) 
        self.assertEqual("COIN", oc.symbol)
        self.assertEqual(81, oc.strike)
        self.assertEqual("C", oc.right)
        self.assertEqual("20231013", oc.expiry_date)

    # Commenting this as I've removed the closing price range from Analyst2. The program
    # will create closing contracts upon any closing alert.  
    def test_process_messages_doesnt_create_contract_failing_closing_price_range(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "5%",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @0.5",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.exit_percentage_less_than_50 = 0
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))


        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "5%",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.exit_percentage_50_to_100 = 0
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))

        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "5%",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @1.5",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.exit_percentage_100_to_150 = 0
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))

        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "5%",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @2",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.exit_percentage_150_to_200 = 0
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))


    def test_process_messages_doesnt_create_contract_empty_closing_price(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @0.5",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))

        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "@",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @0.5",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))

        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "@hi",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @0.5",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))


    def test_process_messages_doesnt_create_contract_empty_alerted_percentage(self):
        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "%",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @0.5",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))


        self.analyst2.message_data = [
            {
                "id": "1",
                "content": "hi%",
                "timestamp": "2023-10-20T15:59:44.779000+00:00",
                "referenced_message": 
                    {
                        "id": "2",
                        "content": "COIN 81C 10/13/23 @0.5",
                        "timestamp": "2023-10-20T15:28:35.466000+00:00",
                    }
            }
        ]
        self.analyst2.process_messages()
        self.assertEqual(0, len(self.analyst2.options_contracts))



if __name__ == '__main__':
    unittest.main()