# The next 5 line of code is necessary to auto run this test by pressing play. 
# If the codes are not present, Python fails to find the imported modules. 
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from classes.discord.Analyst1 import Analyst1



import unittest

class TestAnalyst(unittest.TestCase):
    def setUp(self):
        self.analyst1 = Analyst1()
        

    def test_process_messages_title_is_update(self):
        self.analyst1.message_data = [
            {
                "embeds": [
                    {
                        "title": "Update:",
                        "description": "CPI predictions curtesy of Twitter",
                    }
                ],
            }
        ]
        self.analyst1.process_messages()
        options_contract = self.analyst1.options_contracts
        self.assertEqual(0, len(options_contract))

        words_list = self.analyst1.words_list
        self.assertEqual(["Update:", "CPI", "predictions", "curtesy", "of", "Twitter"], words_list)

    def test_process_messages_title_is_open(self):
        self.analyst1.message_data = [
            {
                "embeds": [
                    {
                        "title": "Open",
                        "description": "BTO HUT 4C 8/21 @ 0.40 - if BTC breaks with positive CPI reaction, this will be ITM.",
                    }
                ],
            }
        ]
        self.analyst1.process_messages()
        options_contract = self.analyst1.options_contracts[0]
        self.assertEqual("BUY", options_contract.action) 
        self.assertEqual("HUT", options_contract.symbol)
        self.assertEqual(4, options_contract.strike)
        self.assertEqual("C", options_contract.right)
        self.assertEqual("20240821", options_contract.expiry_date)

        words_list = self.analyst1.words_list
        self.assertEqual(["Open", "BTO", "HUT", "4C", "8/21", "@", "0.40", "-", "if", "BTC", "breaks", "with", "positive", "CPI", "reaction,", "this", "will", "be", "ITM."], words_list)


    def test_process_messages_title_is_close(self):
        self.analyst1.message_data = [
            {
                "embeds": [
                    {
                        "title": "Close",
                        "description": "STC HUT 4C 8/21 @ 0.40 (CPI LOTTO) - if BTC breaks with positive CPI reaction, this will be ITM.",
                    }
                ],
            }
        ]
        self.analyst1.process_messages()
        options_contract = self.analyst1.options_contracts[0]
        self.assertEqual("SELL", options_contract.action) 
        self.assertEqual("HUT", options_contract.symbol)
        self.assertEqual(4, options_contract.strike)
        self.assertEqual("C", options_contract.right)
        self.assertEqual("20240821", options_contract.expiry_date)

        words_list = self.analyst1.words_list
        self.assertEqual(["Close", "STC", "HUT", "4C", "8/21", "@", "0.40", "(CPI", "LOTTO)", "-", "if", "BTC", "breaks", "with", "positive", "CPI", "reaction,", "this", "will", "be", "ITM."], words_list)


    def test_open_fails_if_lotto_or_risky_trade(self):
        self.analyst1.message_data = [
            {
                "embeds": [
                    {
                        "title": "Open",
                        "description": "BTO HUT 4C 8/21 @ 0.40 (LOTTO) - if BTC breaks with positive CPI reaction, this will be ITM.",
                    }
                ],
            }
        ]
        self.analyst1.process_messages()
        options_contract = self.analyst1.options_contracts
        self.assertEqual(0, len(options_contract))

        self.analyst1.message_data = [
            {
                "embeds": [
                    {
                        "title": "Open",
                        "description": "BTO HUT 4C 8/21 @ 0.40 (HIGH RISK) - if BTC breaks with positive CPI reaction, this will be ITM.",
                    }
                ],
            }
        ]
        self.analyst1.process_messages()
        options_contract = self.analyst1.options_contracts
        self.assertEqual(0, len(options_contract))

        self.analyst1.message_data = [
            {
                "embeds": [
                    {
                        "title": "Open",
                        "description": "BTO HUT 4C 8/21 @ 0.40 (RISKY) - if BTC breaks with positive CPI reaction, this will be ITM.",
                    }
                ],
            }
        ]
        self.analyst1.process_messages()
        options_contract = self.analyst1.options_contracts
        self.assertEqual(0, len(options_contract))


        self.analyst1.message_data = [
            {
                "embeds": [
                    {
                        "title": "Open",
                        "description": "BTO HUT 4C 8/21 @ 0.40 (RISKY/LOTTO) - if BTC breaks with positive CPI reaction, this will be ITM.",
                    }
                ],
            }
        ]
        self.analyst1.process_messages()
        options_contract = self.analyst1.options_contracts
        self.assertEqual(0, len(options_contract))
        
        

    def test_process_messages_title_is_update_but_BTO(self):
        self.analyst1.message_data = [
            {
                "embeds": [
                    {
                        "title": "Update:",
                        "description": "BTO HUT 4C 8/21 @ 0.40 (CPI LOTTO) - if BTC breaks with positive CPI reaction, this will be ITM.",
                    }
                ],
            }
        ]
        self.analyst1.process_messages()
        options_contract = self.analyst1.options_contracts
        self.assertEqual(0, len(options_contract))

        words_list = self.analyst1.words_list
        self.assertEqual(["Update:", "BTO", "HUT", "4C", "8/21", "@", "0.40", "(CPI", "LOTTO)", "-", "if", "BTC", "breaks", "with", "positive", "CPI", "reaction,", "this", "will", "be", "ITM."], words_list)


    def test_process_messages_title_is_open_but_Inextractable_message(self):
        self.analyst1.message_data = [
            {
                "embeds": [
                    {
                        "title": "Open",
                        "description": "BTO 250 PLTR @ 17.06.",
                    }
                ],
            }
        ]
        self.analyst1.process_messages()
        options_contract = self.analyst1.options_contracts
        self.assertEqual(0, len(options_contract))

        words_list = self.analyst1.words_list
        self.assertEqual(['Open', 'BTO', '250', 'PLTR', '@', '17.06.'], words_list)

    # def test_exception_throws_if_dicts_description_not_exist(self):
    #     self.Analyst1.message_data = [
    #         {
    #             "embeds": [
    #                 {
    #                     "type": "rich",
    #                     "title": "Update:",
    #                     "color": 4368373,
    #                     "footer": {
    #                         "text": "© Turning Points Entities, Inc; Official Analyst1Panda Bot; For Informational Purposes Only, Not Financial Advice\n08/11/23 ● 06:58 AM",
    #                         "icon_url": "https://cdn.discordapp.com/attachments/955288518710685696/979490425381462097/BAMBOO_PANDA.png",
    #                         "proxy_icon_url": "https://media.discordapp.net/attachments/955288518710685696/979490425381462097/BAMBOO_PANDA.png"
    #                     }
    #                 }
    #             ],
    #         }

    #     ]
    #     with self.assertRaises(KeyError):
    #         self.Analyst1.process_messages()


if __name__ == '__main__':
    unittest.main()