# The next 5 line of code is necessary to auto run this test by pressing play. 
# If the codes are not present, Python fails to find the imported modules. 
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from classes.discord.Analyst3 import Analyst3



import unittest

class TestAnalyst(unittest.TestCase):
    def setUp(self):
        self.analyst3 = Analyst3()
        

    def test_words_in_messages_appended_to_words_list_by_space(self):
        self.analyst3.message_data = [
            {
                "content": "len of Analyst3.options_contracts will be 0"
            }
        ]

        self.analyst3.process_messages()
        words_list = self.analyst3.words_list
        self.assertEqual(["len", "of", "Analyst3.options_contracts", "will", "be", "0"], words_list)


    def test_process_messages_non_contract_messages(self):
        self.analyst3.message_data = [
            {
                "content": "len of Analyst3.options_contracts will be 0"
            }
        ]
        self.analyst3.process_messages()
        self.assertEqual(0, len(self.analyst3.options_contracts))


    def test_process_messages_open_contract(self):
        self.analyst3.message_data = [
            {
                "content": "**Swing Trade**: BTO 5 V 235P 10/06 @ 1.02"
            }
        ]
        self.analyst3.process_messages()
        oc = self.analyst3.options_contracts[0]
        self.assertEqual(1, len(self.analyst3.options_contracts))

        self.assertEqual("BUY", oc.action) 
        self.assertEqual("V", oc.symbol)
        self.assertEqual(235, oc.strike)
        self.assertEqual("P", oc.right)
        self.assertEqual("20231006", oc.expiry_date)


    def test_process_messages_open_contract_lowercase(self):
        self.analyst3.message_data = [
            {
                "content": "**Swing Trade**: bto 5 V 235P 10/06 @ 1.02"
            }
        ]
        self.analyst3.process_messages()
        oc = self.analyst3.options_contracts[0]
        self.assertEqual(1, len(self.analyst3.options_contracts))

        self.assertEqual("BUY", oc.action) 
        self.assertEqual("V", oc.symbol)
        self.assertEqual(235, oc.strike)
        self.assertEqual("P", oc.right)
        self.assertEqual("20231006", oc.expiry_date)


    def test_process_messages_open_contract_mixedcase(self):
        self.analyst3.message_data = [
            {
                "content": "**Swing Trade**: BtO 5 V 235P 10/06 @ 1.02"
            }
        ]
        self.analyst3.process_messages()
        oc = self.analyst3.options_contracts[0]
        self.assertEqual(1, len(self.analyst3.options_contracts))

        self.assertEqual("BUY", oc.action) 
        self.assertEqual("V", oc.symbol)
        self.assertEqual(235, oc.strike)
        self.assertEqual("P", oc.right)
        self.assertEqual("20231006", oc.expiry_date)


    def test_process_messages_open_contract_fails(self):
        self.analyst3.message_data = [
            {
                "content": "**Swing Trade**: BTO"
            }
        ]
        self.analyst3.process_messages()
        self.assertEqual(0, len(self.analyst3.options_contracts))


    def test_process_messages_open_contract_fails_in_different_order(self):
        self.analyst3.message_data = [
            {
                "content": "**Swing Trade**: BtO 5 235P V 10/06 @ 1.02"
            }
        ]
        self.analyst3.process_messages()
        self.assertEqual(0, len(self.analyst3.options_contracts))


    def test_process_messages_open_contract_fails_in_incorrect_date_format(self):
        self.analyst3.message_data = [
            {
                "content": "**Swing Trade**: BtO 5 235P V 10_06 @ 1.02"
            }
        ]
        self.analyst3.process_messages()
        self.assertEqual(0, len(self.analyst3.options_contracts))


    def test_process_messages_open_contract_fails_if_strike_and_right_spaced(self):
        self.analyst3.message_data = [
            {
                "content": "**Swing Trade**: BTO 5 V 235 P 10/06 @ 1.02"
            }
        ]
        self.analyst3.process_messages()
        self.assertEqual(0, len(self.analyst3.options_contracts))


    """
    Selling contract unit tests
    
    """


if __name__ == '__main__':
    unittest.main()